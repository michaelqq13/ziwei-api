"""
LINE Bot Webhook 處理器
處理來自 LINE Platform 的 Webhook 事件
"""
import json
import logging
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.db.database import get_db
from app.config.linebot_config import LineBotConfig, validate_config
from app.models.linebot_models import LineBotUser, DivinationHistory, ChartBinding, MemoryUserSession
from app.logic.permission_manager import permission_manager, get_user_with_permissions
from app.logic.divination_logic import divination_logic, get_divination_result
from app.utils.rich_menu_manager import rich_menu_manager
from app.utils.divination_flex_message import DivinationFlexMessageGenerator
import os
import re
import requests
from app.config.database_config import DatabaseConfig
from starlette.background import BackgroundTasks

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter()

# 記憶體中的用戶會話管理
user_sessions: Dict[str, MemoryUserSession] = {}

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_optional_db() -> Optional[Session]:
    """獲取可選的數據庫會話"""
    try:
        # 嘗試創建數據庫會話
        database_url = DatabaseConfig.get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 測試數據庫連接
        db.execute("SELECT 1")
        return db
    except Exception as e:
        logger.warning(f"數據庫連接失敗，使用簡化模式：{e}")
        return None

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

def get_or_create_session(user_id: str) -> MemoryUserSession:
    """獲取或創建用戶會話"""
    if user_id not in user_sessions:
        user_sessions[user_id] = MemoryUserSession(user_id)
    return user_sessions[user_id]

def send_line_message(user_id: str, message: str) -> bool:
    """發送LINE訊息"""
    try:
        from app.config.linebot_config import LineBotConfig
        import requests
        
        # 構建訊息數據
        headers = {
            'Authorization': f'Bearer {LineBotConfig.LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': user_id,
            'messages': [
                {
                    'type': 'text',
                    'text': message
                }
            ]
        }
        
        # 發送訊息
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info(f"成功發送訊息給用戶 {user_id}")
            return True
        else:
            logger.error(f"發送訊息失敗，狀態碼：{response.status_code}，回應：{response.text}")
            return False
        
    except Exception as e:
        logger.error(f"發送LINE訊息失敗：{e}")
        return False

def send_line_flex_messages(user_id: str, messages: List) -> bool:
    """
    發送多個 LINE Flex 訊息給用戶
    
    Args:
        user_id: 用戶ID
        messages: FlexMessage列表
    """
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LineBotConfig.CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # 將FlexMessage轉換為字典格式
        message_objects = []
        for msg in messages:
            try:
                # 嘗試使用 to_dict 方法
                if hasattr(msg, 'to_dict'):
                    msg_dict = msg.to_dict()
                    logger.info(f"使用 to_dict() 轉換訊息: {msg.alt_text}")
                    message_objects.append(msg_dict)
                elif hasattr(msg, '__dict__'):
                    # 如果沒有 to_dict 方法，嘗試手動構建字典
                    msg_dict = {
                        "type": "flex",
                        "altText": msg.alt_text,
                        "contents": msg.contents.to_dict() if hasattr(msg.contents, 'to_dict') else msg.contents
                    }
                    logger.info(f"手動構建字典: {msg.alt_text}")
                    message_objects.append(msg_dict)
                else:
                    # 如果是字典格式，直接使用
                    logger.info(f"直接使用字典格式")
                    message_objects.append(msg)
            except Exception as convert_error:
                logger.error(f"轉換訊息時發生錯誤: {convert_error}")
                logger.error(f"訊息類型: {type(msg)}")
                logger.error(f"訊息屬性: {dir(msg)}")
                continue
        
        if not message_objects:
            logger.error("沒有成功轉換的訊息")
            return False
        
        data = {
            "to": user_id,
            "messages": message_objects
        }
        
        logger.info("=== 開始發送 LINE Flex 訊息 ===")
        logger.info(f"目標用戶ID: {user_id}")
        logger.info(f"訊息數量: {len(message_objects)}")
        logger.info(f"第一個訊息結構: {json.dumps(message_objects[0], ensure_ascii=False, indent=2)[:500]}...")
        
        response = requests.post(url, headers=headers, json=data)
        
        logger.info("=== LINE API 回應 ===")
        logger.info(f"回應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("✅ Flex訊息發送成功")
            return True
        else:
            logger.error(f"❌ Flex訊息發送失敗 (HTTP {response.status_code})")
            logger.error(f"錯誤詳情: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 發送Flex訊息時發生異常: {e}")
        logger.error(f"異常詳情: {traceback.format_exc()}")
        return False

def format_divination_result(result: Dict) -> str:
    """格式化占卜結果為用戶友好的訊息"""
    if not result.get("success"):
        return "🔮 占卜過程發生錯誤，請稍後再試。"
    
    # 基本資訊
    gender_text = "男性" if result["gender"] == "M" else "女性"
    
    # 解析時間字符串並轉換為台北時間
    divination_time_str = result["divination_time"]
    if divination_time_str.endswith('+08:00'):
        # 如果已經包含時區信息，直接解析
        divination_time = datetime.fromisoformat(divination_time_str)
    else:
        # 如果沒有時區信息，當作UTC時間處理，然後轉換為台北時間
        divination_time = datetime.fromisoformat(divination_time_str.replace('Z', '+00:00'))
        if divination_time.tzinfo is None:
            divination_time = divination_time.replace(tzinfo=timezone.utc)
        divination_time = divination_time.astimezone(TAIPEI_TZ)
    
    time_str = divination_time.strftime("%Y-%m-%d %H:%M")
    
    message = f"""🔮 **紫微斗數占卜結果** ✨

📅 占卜時間：{time_str} (台北時間)
👤 性別：{gender_text}
🏰 太極點命宮：{result["taichi_palace"]}
🕰️ 分鐘地支：{result["minute_dizhi"]}
⭐ 宮干：{result["palace_tiangan"]}

━━━━━━━━━━━━━━━━━
📊 **基本命盤資訊**

"""
    
    # 添加基本盤資訊
    basic_chart = result.get("basic_chart", {})
    if basic_chart:
        for palace_name, info in basic_chart.items():
            message += f"【{palace_name}】\n"
            message += f"天干：{info.get('tiangan', '未知')} 地支：{info.get('dizhi', '未知')}\n"
            stars = info.get('stars', [])
            if stars:
                message += f"星曜：{', '.join(stars)}\n"
            message += "\n"
    
    message += "━━━━━━━━━━━━━━━━━\n"
    message += "📊 **四化解析**\n\n"
    message += "💰 祿：有利的事情（好運、財運、順利、機會）\n"
    message += "👑 權：有主導權的事情（領導力、決策權、掌控力）\n"
    message += "🌟 科：提升地位名聲（受人重視、被看見、受表揚）\n"
    message += "⚡ 忌：可能困擾的事情（阻礙、困難、需要注意）\n"
    
    # 添加四化結果
    for i, sihua in enumerate(result["sihua_results"], 1):
        emoji_map = {"忌": "⚡", "祿": "💰", "權": "👑", "科": "📚"}
        emoji = emoji_map.get(sihua["type"], "⭐")
        
        # 在每個四化星前加分隔線
        message += "\n━━━━━━━━━━━━━━━━━━━━\n"
        message += f"{emoji} **{sihua['type']}星 - {sihua['star']}**\n"
        message += f"   落宮：{sihua['palace']}\n\n"
        message += f"{sihua['explanation']}\n"
    
    message += "━━━━━━━━━━━━━━━━━\n"
    message += "✨ 願星空指引您的方向 ✨"
    
    return message

def format_user_info(user_stats: Dict) -> str:
    """格式化用戶資訊"""
    user_info = user_stats["user_info"]
    stats = user_stats["statistics"] 
    membership = user_stats["membership_info"]
    
    message = f"""👤 **會員資訊** ✨

🏷️ 暱稱：{user_info["display_name"] or "未設定"}
🎖️ 等級：{membership["level_name"]}
📅 加入時間：{datetime.fromisoformat(user_info["created_at"]).strftime("%Y-%m-%d")}

📊 **使用統計**
🔮 總占卜次數：{stats["total_divinations"]} 次
📅 本週占卜：{stats["weekly_divinations"]} 次
"""
    
    if not membership["is_premium"]:
        message += f"⏳ 週限制：{stats['weekly_limit']} 次\n"
    else:
        message += "⏳ 週限制：無限制 ✨\n"
    
    message += f"\n🔐 **功能權限**\n"
    
    permissions = user_stats["permissions"]
    if permissions["divination"]["allowed"]:
        if permissions["divination"]["reason"] == "unlimited":
            message += "🔮 占卜功能：✅ 無限制\n"
        else:
            remaining = permissions["divination"]["remaining_count"]
            message += f"🔮 占卜功能：✅ 剩餘 {remaining} 次\n"
    else:
        message += "🔮 占卜功能：❌ 本週額度已用完\n"
    
    fortune_features = [
        ("yearly_fortune", "📊 流年運勢"),
        ("monthly_fortune", "🌙 流月運勢"), 
        ("daily_fortune", "☀️ 流日運勢")
    ]
    
    for feature_key, feature_name in fortune_features:
        if permissions[feature_key]["allowed"]:
            message += f"{feature_name}：✅ 可使用\n"
        else:
            message += f"{feature_name}：❌ 需付費會員\n"
    
    message += "⭐ 命盤綁定：✅ 可使用\n"
    
    message += f"\n📝 **個人設定**\n"
    message += "• 輸入「設定暱稱」可修改顯示名稱\n"
    
    if not membership["is_premium"]:
        message += "\n💎 升級付費會員享受更多功能！"
    
    return message

def handle_divination_request(db: Optional[Session], user: LineBotUser, session: MemoryUserSession) -> str:
    """處理占卜請求"""
    
    # 檢查是否已有本週占卜記錄（只在有數據庫時檢查）
    if db:
        try:
            from app.logic.divination import get_this_week_divination
            existing_divination = get_this_week_divination(user.line_user_id, db)
            
            if existing_divination:
                return f"""🔮 **本週占卜** ✨

您本週已經占過卜了！

📅 占卜時間：{existing_divination.divination_time.strftime("%Y-%m-%d %H:%M")}
👤 性別：{'男性' if existing_divination.gender == 'M' else '女性'}

⏰ 每週只能占卜一次，請下週再來！"""
        except Exception as e:
            logger.warning(f"檢查本週占卜記錄時發生錯誤: {e}")
    
    # 開始占卜流程
    session.set_state("waiting_for_gender")
    
    quick_reply_items = [
        {"type": "action", "action": {"type": "message", "label": "👨 男性", "text": "男"}},
        {"type": "action", "action": {"type": "message", "label": "👩 女性", "text": "女"}}
    ]
    
    message = """🔮 **觸機占卜** ✨

根據當下時間和您的性別特質進行占卜分析

⚡ **請選擇您的性別：**
• 點選下方按鈕或直接輸入
• 這將用於計算您的專屬命盤"""
    
    # 發送帶有Quick Reply按鈕的訊息
    send_line_message(user.line_user_id, message, quick_reply_items)
    return ""  # 返回空字符串而不是None，表示訊息已經發送

def handle_gender_input(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理性別輸入"""
    text = text.strip().upper()
    
    # 解析性別
    gender = None
    if text in ["男", "M", "MALE", "MAN"]:
        gender = "M"
    elif text in ["女", "F", "FEMALE", "WOMAN"]:
        gender = "F"
    
    if not gender:
        return """❓ 請輸入有效的性別：
• 回覆「男」或「M」代表男性  
• 回覆「女」或「F」代表女性"""
    
    # 執行占卜
    try:
        current_time = get_current_taipei_time()
        result = divination_logic.perform_divination(gender, current_time, db)
        
        if result["success"]:
            # 嘗試保存占卜記錄（如果數據庫可用）
            try:
                if db:
                    divination_record = DivinationHistory(
                        user_id=user.id,
                        gender=gender,
                        divination_time=current_time,
                        taichi_palace=result["taichi_palace"],
                        minute_dizhi=result["minute_dizhi"],
                        sihua_results=json.dumps(result["sihua_results"], ensure_ascii=False)
                    )
                    
                    db.add(divination_record)
                    db.commit()
                    logger.info("占卜記錄已保存到數據庫")
            except Exception as db_error:
                logger.warning(f"無法保存占卜記錄到數據庫: {db_error}")
                logger.info("占卜將繼續進行，但不會保存記錄")
            
            # 清除會話狀態
            session.clear()
            
            # 檢查用戶是否為管理員（如果數據庫不可用，默認為非管理員）
            is_admin = False
            try:
                if db:
                    is_admin = permission_manager.check_admin_access(user.line_user_id, db)
            except Exception as perm_error:
                logger.warning(f"無法檢查管理員權限: {perm_error}")
            
            # 使用新的Flex Message生成器
            flex_generator = DivinationFlexMessageGenerator()
            flex_messages = flex_generator.generate_divination_messages(result, is_admin)
            
            if flex_messages:
                # 發送Flex Messages
                success = send_line_flex_messages(user.line_user_id, flex_messages)
                if success:
                    return ""  # 已經發送Flex訊息，不需要返回文字
                else:
                    # Flex訊息發送失敗，使用備用文字格式
                    return format_divination_result_text(result, is_admin)
            else:
                # 沒有生成Flex訊息，使用備用文字格式
                return format_divination_result_text(result, is_admin)
        else:
            session.clear()
            return "🔮 占卜過程發生錯誤，請稍後再試。"
            
    except Exception as e:
        logger.error(f"占卜過程錯誤: {e}")
        session.clear()
        return "🔮 占卜系統暫時無法使用，請稍後再試。"

def format_divination_result_text(result: Dict, is_admin: bool = False) -> str:
    """格式化占卜結果為文字訊息（備用格式）"""
    if not result.get("success"):
        return "🔮 占卜過程發生錯誤，請稍後再試。"
    
    # 基本資訊
    gender_text = "男性" if result["gender"] == "M" else "女性"
    
    # 解析時間字符串並轉換為台北時間
    divination_time_str = result["divination_time"]
    if divination_time_str.endswith('+08:00'):
        divination_time = datetime.fromisoformat(divination_time_str)
    else:
        divination_time = datetime.fromisoformat(divination_time_str.replace('Z', '+00:00'))
        if divination_time.tzinfo is None:
            divination_time = divination_time.replace(tzinfo=timezone.utc)
        divination_time = divination_time.astimezone(TAIPEI_TZ)
    
    time_str = divination_time.strftime("%Y-%m-%d %H:%M")
    
    message = f"""🔮 **紫微斗數占卜結果** ✨

📅 占卜時間：{time_str} (台北時間)
👤 性別：{gender_text}
🏰 太極點命宮：{result["taichi_palace"]}
🕰️ 分鐘地支：{result["minute_dizhi"]}
⭐ 宮干：{result["palace_tiangan"]}

"""
    
    # 管理員可見的基本命盤資訊
    if is_admin:
        message += "━━━━━━━━━━━━━━━━━\n"
        message += "📊 **基本命盤資訊** (管理員)\n\n"
        
        basic_chart = result.get("basic_chart", {})
        if basic_chart:
            for palace_name, info in basic_chart.items():
                message += f"【{palace_name}】\n"
                message += f"天干：{info.get('tiangan', '未知')} 地支：{info.get('dizhi', '未知')}\n"
                stars = info.get('stars', [])
                if stars:
                    message += f"星曜：{', '.join(stars[:5])}\n"  # 最多顯示5顆星
                message += "\n"
        
        message += "━━━━━━━━━━━━━━━━━\n"
        message += "🎯 **太極點命宮資訊** (管理員)\n\n"
        
        taichi_mapping = result.get("taichi_palace_mapping", {})
        if taichi_mapping:
            message += "宮位重新分佈：\n"
            for branch, palace in taichi_mapping.items():
                message += f"• {branch} → {palace}\n"
            message += "\n"
    
    message += "━━━━━━━━━━━━━━━━━\n"
    message += "🔮 **四化解析**\n\n"
    message += "💰 祿：有利的事情（好運、財運、順利、機會）\n"
    message += "👑 權：有主導權的事情（領導力、決策權、掌控力）\n"
    message += "🌟 科：提升地位名聲（受人重視、被看見、受表揚）\n"
    message += "⚡ 忌：可能困擾的事情（阻礙、困難、需要注意）\n"
    
    # 添加四化結果
    for i, sihua in enumerate(result["sihua_results"], 1):
        emoji_map = {"忌": "⚡", "祿": "💰", "權": "👑", "科": "🌟"}
        emoji = emoji_map.get(sihua["type"], "⭐")
        
        # 在每個四化星前加分隔線
        message += "\n━━━━━━━━━━━━━━━━━━━━\n"
        message += f"{emoji} **{sihua['type']}星 - {sihua['star']}**\n"
        message += f"   落宮：{sihua['palace']}\n\n"
        
        # 簡化解釋內容（文字版本）
        explanation = sihua.get('explanation', '')
        if explanation:
            # 只取前200字
            short_explanation = explanation[:200] + "..." if len(explanation) > 200 else explanation
            message += f"{short_explanation}\n"
    
    message += "━━━━━━━━━━━━━━━━━\n"
    message += "✨ 願星空指引您的方向 ✨"
    
    return message

def handle_chart_binding(db: Optional[Session], user: LineBotUser, session: MemoryUserSession) -> str:
    """處理命盤綁定請求"""
    # 檢查是否已經綁定
    existing_binding = db.query(ChartBinding).filter(ChartBinding.user_id == user.id).first()
    
    if existing_binding:
        birth_date = f"{existing_binding.birth_year}/{existing_binding.birth_month}/{existing_binding.birth_day}"
        birth_time = f"{existing_binding.birth_hour:02d}:{existing_binding.birth_minute:02d}"
        gender_text = "男性" if existing_binding.gender == "M" else "女性"
        calendar_text = "農曆" if existing_binding.calendar_type == "lunar" else "國曆"
        
        return f"""⭐ **您的命盤綁定資訊** ✨

📅 出生日期：{birth_date} ({calendar_text})
🕐 出生時間：{birth_time}
👤 性別：{gender_text}
📅 綁定時間：{existing_binding.created_at.strftime("%Y-%m-%d %H:%M")}

如需重新綁定，請聯繫管理員。"""
    
    # 開始綁定流程
    session.set_state("chart_binding_year")
    return """⭐ **命盤綁定** ✨

請依序提供您的出生資訊：

📅 **第一步：出生年份**
請輸入您的出生年份（例如：1990）"""

def handle_chart_binding_process(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理命盤綁定過程"""
    text = text.strip()
    
    if session.state == "chart_binding_year":
        try:
            year = int(text)
            if year < 1900 or year > get_current_taipei_time().year:
                return "請輸入有效的年份（1900年之後）"
            
            session.set_data("birth_year", year)
            session.set_state("chart_binding_month")
            return "📅 **第二步：出生月份**\n請輸入月份（1-12）："
            
        except ValueError:
            return "請輸入有效的數字年份"
    
    elif session.state == "chart_binding_month":
        try:
            month = int(text)
            if month < 1 or month > 12:
                return "請輸入有效的月份（1-12）"
            
            session.set_data("birth_month", month)
            session.set_state("chart_binding_day")
            return "📅 **第三步：出生日期**\n請輸入日期（1-31）："
            
        except ValueError:
            return "請輸入有效的數字月份"
    
    elif session.state == "chart_binding_day":
        try:
            day = int(text)
            if day < 1 or day > 31:
                return "請輸入有效的日期（1-31）"
            
            session.set_data("birth_day", day)
            session.set_state("chart_binding_hour")
            return "🕐 **第四步：出生時間**\n請輸入小時（0-23）："
            
        except ValueError:
            return "請輸入有效的數字日期"
    
    elif session.state == "chart_binding_hour":
        try:
            hour = int(text)
            if hour < 0 or hour > 23:
                return "請輸入有效的小時（0-23）"
            
            session.set_data("birth_hour", hour)
            session.set_state("chart_binding_minute")
            return "🕐 **第五步：出生分鐘**\n請輸入分鐘（0-59）："
            
        except ValueError:
            return "請輸入有效的數字小時"
    
    elif session.state == "chart_binding_minute":
        try:
            minute = int(text)
            if minute < 0 or minute > 59:
                return "請輸入有效的分鐘（0-59）"
            
            session.set_data("birth_minute", minute)
            session.set_state("chart_binding_gender")
            return """👤 **第六步：性別**
請選擇您的性別：
• 回覆「男」或「M」代表男性
• 回覆「女」或「F」代表女性"""
            
        except ValueError:
            return "請輸入有效的數字分鐘"
    
    elif session.state == "chart_binding_gender":
        text_upper = text.upper()
        gender = None
        
        if text_upper in ["男", "M", "MALE", "MAN"]:
            gender = "M"
        elif text_upper in ["女", "F", "FEMALE", "WOMAN"]:
            gender = "F"
        
        if not gender:
            return """請輸入有效的性別：
• 回覆「男」或「M」代表男性
• 回覆「女」或「F」代表女性"""
        
        session.set_data("gender", gender)
        session.set_state("chart_binding_calendar")
        return """📅 **第七步：曆法**
請選擇出生日期的曆法：
• 回覆「國曆」或「陽曆」
• 回覆「農曆」或「陰曆」"""
    
    elif session.state == "chart_binding_calendar":
        text_lower = text.lower()
        calendar_type = None
        
        if text in ["國曆", "陽曆", "solar"] or "國" in text or "陽" in text:
            calendar_type = "solar"
        elif text in ["農曆", "陰曆", "lunar"] or "農" in text or "陰" in text:
            calendar_type = "lunar"
        
        if not calendar_type:
            return """請選擇有效的曆法：
• 回覆「國曆」或「陽曆」
• 回覆「農曆」或「陰曆」"""
        
        # 保存命盤綁定
        try:
            chart_binding = ChartBinding(
                user_id=user.id,
                birth_year=session.get_data("birth_year"),
                birth_month=session.get_data("birth_month"),
                birth_day=session.get_data("birth_day"),
                birth_hour=session.get_data("birth_hour"),
                birth_minute=session.get_data("birth_minute"),
                gender=session.get_data("gender"),
                calendar_type=calendar_type
            )
            
            db.add(chart_binding)
            db.commit()
            
            # 清除會話狀態
            session.clear()
            
            birth_date = f"{chart_binding.birth_year}/{chart_binding.birth_month}/{chart_binding.birth_day}"
            birth_time = f"{chart_binding.birth_hour:02d}:{chart_binding.birth_minute:02d}"
            gender_text = "男性" if chart_binding.gender == "M" else "女性"
            calendar_text = "農曆" if chart_binding.calendar_type == "lunar" else "國曆"
            
            return f"""✅ **命盤綁定成功** ✨

📅 出生日期：{birth_date} ({calendar_text})
🕐 出生時間：{birth_time}
👤 性別：{gender_text}

現在您可以使用流年、流月、流日運勢查詢功能了！"""
            
        except Exception as e:
            logger.error(f"保存命盤綁定失敗: {e}")
            session.clear()
            return "❌ 命盤綁定失敗，請稍後再試。"
    
    return "❓ 綁定流程發生錯誤，請重新開始。"

def handle_fortune_request(db: Optional[Session], user: LineBotUser, fortune_type: str) -> str:
    """處理運勢查詢請求"""
    # 檢查權限
    permission = permission_manager.check_fortune_permission(db, user, fortune_type)
    if not permission["allowed"]:
        return permission_manager.format_permission_message(permission, f"{fortune_type}運勢")
    
    # 檢查是否已綁定命盤
    chart_binding = db.query(ChartBinding).filter(ChartBinding.user_id == user.id).first()
    if not chart_binding:
        return LineBotConfig.Messages.CHART_BINDING_REQUIRED
    
    # 暫時返回佔位符訊息（實際運勢計算邏輯可後續完善）
    fortune_names = {
        "yearly": "流年運勢",
        "monthly": "流月運勢",
        "daily": "流日運勢"
    }
    
    return f"""📊 **{fortune_names[fortune_type]}** ✨

🏷️ 此功能正在開發中...
📅 您的命盤已綁定，運勢計算功能即將上線！

期待為您提供更精準的運勢分析。"""

def handle_admin_authentication(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理管理員認證"""
    if session.state == "admin_auth_phrase":
        if text.strip() == LineBotConfig.ADMIN_SECRET_PHRASE:
            session.set_state("admin_auth_password")
            return "🔑 請輸入管理員密碼："
        else:
            session.clear()
            return "❌ 密語錯誤，認證失敗。"
    
    elif session.state == "admin_auth_password":
        if text.strip() == LineBotConfig.ADMIN_PASSWORD:
            # 提升為管理員
            if permission_manager.promote_to_admin(db, user.line_user_id):
                session.clear()
                return "✅ 管理員認證成功！您已獲得管理員權限。"
            else:
                session.clear()
                return "❌ 權限提升失敗，請稍後再試。"
        else:
            session.clear()
            return "❌ 密碼錯誤，認證失敗。"
    
    return "❓ 認證流程錯誤。"

def handle_nickname_setting(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理暱稱設定"""
    if session.state == "setting_nickname":
        nickname = text.strip()
        
        if not nickname:
            session.clear()
            return "❌ 暱稱不能為空，設定取消。"
        
        if len(nickname) > 50:
            return "❌ 暱稱長度不能超過50個字元，請重新輸入："
        
        # 更新暱稱
        if permission_manager.update_user_nickname(db, user.line_user_id, nickname):
            session.clear()
            return f"✅ 暱稱已更新為：{nickname}"
        else:
            session.clear()
            return "❌ 暱稱更新失敗，請稍後再試。"
    
    return "❓ 暱稱設定流程錯誤。"

@router.post("/webhook")
async def line_webhook(request: Request, background_tasks: BackgroundTasks):
    """處理 LINE Webhook 事件（支持可選數據庫）"""
    try:
        body = await request.body()
        signature = request.headers.get('X-Line-Signature', '')
        
        # 驗證簽名
        if not verify_line_signature(body, signature):
            logger.error("LINE簽名驗證失敗")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析事件
        events_data = json.loads(body.decode('utf-8'))
        events = events_data.get('events', [])
        
        logger.info(f"收到 {len(events)} 個LINE事件")
        
        # 獲取可選的數據庫會話
        db = get_optional_db()
        
        try:
            # 處理每個事件
            for event in events:
                background_tasks.add_task(handle_line_event, event, db)
            
            return {"status": "ok"}
            
        finally:
            # 清理數據庫會話
            if db:
                db.close()
        
    except Exception as e:
        logger.error(f"Webhook處理錯誤：{e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def handle_line_event(event: dict, db: Optional[Session]):
    """處理LINE事件（支持可選數據庫）"""
    try:
        event_type = event.get("type")
        user_id = event.get("source", {}).get("userId", "unknown")
        
        logger.info(f"處理事件：{event_type}，用戶：{user_id}，數據庫：{'有' if db else '無'}")
        
        if event_type == "message":
            handle_message_event(event, db)
        elif event_type == "follow":
            handle_follow_event(event, db)
        elif event_type == "unfollow":
            handle_unfollow_event(event, db)
        else:
            logger.info(f"忽略事件類型：{event_type}")
            
    except Exception as e:
        logger.error(f"處理LINE事件錯誤：{e}")

def handle_message_event(event: dict, db: Optional[Session]):
    """處理訊息事件（支持可選數據庫）"""
    try:
        message = event.get("message", {})
        message_type = message.get("type")
        user_id = event.get("source", {}).get("userId")
        
        if message_type == "text":
            text = message.get("text", "").strip()
            
            # 處理占卜請求
            if any(keyword in text for keyword in ["占卜", "算命", "紫微", "運勢"]):
                # 創建臨時用戶對象（如果沒有數據庫）
                if db is None:
                    logger.info("簡化模式：創建臨時用戶對象")
                    gender = "男"  # 默認性別，占卜時不重要
                else:
                    # 嘗試從數據庫獲取用戶信息
                    try:
                        user = get_or_create_user(db, user_id)
                        gender = user.gender if user and user.gender else "男"
                    except Exception as e:
                        logger.warning(f"獲取用戶信息失敗，使用默認性別：{e}")
                        gender = "男"
                
                # 執行占卜
                divination_result = get_divination_result(db, gender)
                
                if divination_result.get("success"):
                    # 發送占卜結果
                    send_divination_result(user_id, divination_result)
                else:
                    # 發送錯誤訊息
                    error_message = divination_result.get("message", "占卜服務暫時不可用")
                    send_line_message(user_id, error_message)
            else:
                # 其他文字訊息處理
                send_line_message(user_id, "歡迎使用紫微斗數占卜系統！\n請輸入「占卜」開始您的占卜之旅。")
                
    except Exception as e:
        logger.error(f"處理訊息事件錯誤：{e}")

def handle_follow_event(event: dict, db: Optional[Session]):
    """處理加好友事件（支持可選數據庫）"""
    try:
        user_id = event.get("source", {}).get("userId")
        
        if db is not None:
            try:
                # 嘗試創建用戶記錄
                user = get_or_create_user(db, user_id)
                logger.info(f"用戶加入：{user_id}")
            except Exception as e:
                logger.warning(f"創建用戶記錄失敗：{e}")
        else:
            logger.info(f"簡化模式：用戶加入 {user_id}")
        
        # 發送歡迎訊息
        welcome_message = """歡迎使用紫微斗數占卜系統！ 🌟

請輸入「占卜」開始您的占卜之旅。

本系統提供：
✨ 即時占卜解析
🔮 四化星曜詳解
📊 太極點轉換分析

願紫微斗數為您指引人生方向！"""
        
        send_line_message(user_id, welcome_message)
        
    except Exception as e:
        logger.error(f"處理加好友事件錯誤：{e}")

def handle_unfollow_event(event: dict, db: Optional[Session]):
    """處理取消好友事件（支持可選數據庫）"""
    try:
        user_id = event.get("source", {}).get("userId")
        
        if db is not None:
            try:
                # 清理用戶會話
                clear_user_session(db, user_id)
                logger.info(f"用戶離開，已清理會話：{user_id}")
            except Exception as e:
                logger.warning(f"清理用戶會話失敗：{e}")
        else:
            logger.info(f"簡化模式：用戶離開 {user_id}")
        
    except Exception as e:
        logger.error(f"處理取消好友事件錯誤：{e}")

# 健康檢查端點
@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "LINE Bot Webhook"}

# Rich Menu 管理端點（管理員使用）
@router.post("/admin/setup-rich-menu")
async def setup_rich_menu_endpoint():
    """設定 Rich Menu（管理員端點）"""
    try:
        menu_id = rich_menu_manager.ensure_default_rich_menu()
        if menu_id:
            return {"success": True, "rich_menu_id": menu_id}
        else:
            return {"success": False, "error": "Rich Menu 設定失敗"}
    except Exception as e:
        logger.error(f"設定 Rich Menu 錯誤: {e}")
        return {"success": False, "error": str(e)}

@router.post("/admin/force-recreate-rich-menu")
async def force_recreate_rich_menu_endpoint():
    """強制重新創建 Rich Menu（管理員端點）"""
    try:
        # 先清理舊的 Rich Menu
        deleted_count = rich_menu_manager.cleanup_old_rich_menus()
        logger.info(f"清理了 {deleted_count} 個舊的 Rich Menu")
        
        # 強制重新創建
        menu_id = rich_menu_manager.setup_complete_rich_menu(force_recreate=True)
        if menu_id:
            return {
                "success": True, 
                "rich_menu_id": menu_id,
                "message": f"已強制重新創建 Rich Menu，清理了 {deleted_count} 個舊菜單"
            }
        else:
            return {"success": False, "error": "Rich Menu 重新創建失敗"}
    except Exception as e:
        logger.error(f"強制重新創建 Rich Menu 錯誤: {e}")
        return {"success": False, "error": str(e)}

@router.post("/admin/set-user-rich-menu")
async def set_user_rich_menu_endpoint(request: Request):
    """為特定用戶設置 Rich Menu（管理員端點）"""
    try:
        body = await request.json()
        user_id = body.get("user_id")
        
        if not user_id:
            return {"success": False, "error": "缺少 user_id 參數"}
        
        # 1. 確保有預設Rich Menu
        menu_id = rich_menu_manager.get_default_rich_menu_id()
        if not menu_id:
            logger.info("沒有預設Rich Menu，正在創建...")
            menu_id = rich_menu_manager.setup_complete_rich_menu(force_recreate=True)
        
        if not menu_id:
            return {"success": False, "error": "無法獲取或創建預設Rich Menu"}
        
        # 2. 先取消用戶現有的Rich Menu連結
        try:
            rich_menu_manager.unlink_user_rich_menu(user_id)
            logger.info(f"已取消用戶 {user_id} 的舊Rich Menu連結")
        except Exception as unlink_error:
            logger.warning(f"取消舊Rich Menu連結時發生錯誤: {unlink_error}")
        
        # 3. 為用戶設置新的Rich Menu
        success = rich_menu_manager.set_user_rich_menu(user_id, menu_id)
        
        if success:
            # 4. 驗證設置
            user_menu_id = rich_menu_manager.get_user_rich_menu_id(user_id)
            return {
                "success": True,
                "message": f"成功為用戶 {user_id} 設置 Rich Menu",
                "rich_menu_id": menu_id,
                "user_menu_id": user_menu_id
            }
        else:
            return {"success": False, "error": f"為用戶 {user_id} 設置 Rich Menu 失敗"}
            
    except Exception as e:
        logger.error(f"設置用戶 Rich Menu 錯誤: {e}")
        return {"success": False, "error": str(e)}

# 測試特定時間的占卜結果端點
@router.get("/test-divination")
async def test_divination(db: Session = Depends(get_db)):
    """測試特定時間的占卜結果"""
    test_time = datetime(2025, 6, 30, 22, 51)
    gender = "M"
    
    result = divination_logic.perform_divination(gender, test_time, db)
    
    if result["success"]:
        return {
            "success": True,
            "message": "測試成功",
            "result": result
        }
    else:
        return {
            "success": False,
            "message": "測試失敗",
            "error": result.get("error")
        }

# 測試 Flex Message 發送端點
@router.post("/test-flex-message")
async def test_flex_message_endpoint(request: Request):
    """測試 Flex Message 發送（測試用）"""
    try:
        body = await request.json()
        user_id = body.get("user_id")
        
        if not user_id:
            return {"success": False, "error": "缺少 user_id 參數"}
        
        # 創建測試用的占卜結果
        test_result = {
            "success": True,
            "gender": "M",
            "divination_time": "2024-01-15T14:30:00+08:00",
            "taichi_palace": "命宮",
            "minute_dizhi": "午",
            "palace_tiangan": "甲",
            "basic_chart": {
                "命宮": {
                    "tiangan": "甲",
                    "dizhi": "子",
                    "stars": ["紫微（廟旺）", "七殺（平和）", "文昌", "左輔"]
                },
                "兄弟宮": {
                    "tiangan": "乙",
                    "dizhi": "丑",
                    "stars": ["天機（廟旺）", "天梁（廟旺）", "文曲"]
                }
            },
            "taichi_palace_mapping": {
                "子": "命宮",
                "丑": "兄弟宮"
            },
            "sihua_results": [
                {
                    "type": "祿",
                    "star": "廉貞",
                    "palace": "命宮",
                    "explanation": "今天格外渴望出頭，競爭力強，敢於展現自我，容易因主動爭取而獲得好處或被看見。"
                },
                {
                    "type": "權",
                    "star": "破軍",
                    "palace": "財帛宮",
                    "explanation": "財務決策能力增強，善於把握投資機會，容易在金錢方面展現主導權。"
                }
            ]
        }
        
        # 生成 Flex Messages
        flex_generator = DivinationFlexMessageGenerator()
        is_admin = body.get("is_admin", False)
        flex_messages = flex_generator.generate_divination_messages(test_result, is_admin)
        
        if flex_messages:
            # 發送 Flex Messages
            success = send_line_flex_messages(user_id, flex_messages)
            if success:
                return {
                    "success": True,
                    "message": f"成功發送 {len(flex_messages)} 個 Flex 訊息",
                    "message_count": len(flex_messages),
                    "is_admin": is_admin
                }
            else:
                return {
                    "success": False,
                    "error": "Flex 訊息發送失敗"
                }
        else:
            return {
                "success": False,
                "error": "無法生成 Flex 訊息"
            }
            
    except Exception as e:
        logger.error(f"測試 Flex 訊息錯誤: {e}")
        return {"success": False, "error": str(e)}

# 清理用戶會話端點
@router.post("/clear-user-session")
async def clear_user_session_endpoint(request: Request):
    """清理用戶會話（管理員用）"""
    try:
        body = await request.json()
        user_id = body.get("user_id")
        
        if not user_id:
            return {"success": False, "error": "缺少 user_id 參數"}
        
        # 清理用戶會話
        if user_id in user_sessions:
            del user_sessions[user_id]
            return {
                "success": True,
                "message": f"已清理用戶 {user_id} 的會話"
            }
        else:
            return {
                "success": True,
                "message": f"用戶 {user_id} 沒有活動會話"
            }
            
    except Exception as e:
        logger.error(f"清理用戶會話錯誤: {e}")
        return {"success": False, "error": str(e)}

def get_or_create_user(db: Session, user_id: str) -> LineBotUser:
    """獲取或創建用戶"""
    try:
        from app.models.linebot_models import LineBotUser
        
        # 查找現有用戶
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
        
        if not user:
            # 創建新用戶
            user = LineBotUser(
                line_user_id=user_id,
                display_name="新用戶",
                membership_level="free",
                gender="男"  # 默認性別
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"創建新用戶：{user_id}")
        
        return user
        
    except Exception as e:
        logger.error(f"獲取或創建用戶失敗：{e}")
        raise

def clear_user_session(db: Session, user_id: str):
    """清理用戶會話"""
    try:
        # 這裡可以添加清理數據庫中會話記錄的邏輯
        # 目前主要是記錄日誌
        logger.info(f"清理用戶會話：{user_id}")
        
    except Exception as e:
        logger.error(f"清理用戶會話失敗：{e}")

def send_divination_result(user_id: str, divination_result: dict):
    """發送占卜結果"""
    try:
        # 格式化占卜結果為訊息
        if divination_result.get("success"):
            sihua_results = divination_result.get("sihua_results", [])
            taichi_palace = divination_result.get("taichi_palace", "")
            
            message_parts = [f"🔮 占卜結果 - 太極點：{taichi_palace}\n"]
            
            for result in sihua_results:
                trans_type = result.get("transformation_type", "")
                star_name = result.get("star_name", "")
                taichi_palace_name = result.get("taichi_palace", "")
                explanation = result.get("explanation", "")
                
                message_parts.append(f"✨ {star_name}化{trans_type} 在 {taichi_palace_name}")
                if explanation:
                    message_parts.append(f"{explanation}\n")
            
            message = "\n".join(message_parts)
        else:
            message = "占卜過程發生錯誤，請稍後重試"
        
        send_line_message(user_id, message)
        
    except Exception as e:
        logger.error(f"發送占卜結果失敗：{e}")
        send_line_message(user_id, "發送占卜結果時發生錯誤")

def verify_line_signature(body: bytes, signature: str) -> bool:
    """驗證LINE簽名"""
    try:
        # 這裡應該實現LINE簽名驗證邏輯
        # 目前簡化處理，總是返回True
        logger.info("簽名驗證（簡化模式）")
        return True
        
    except Exception as e:
        logger.error(f"簽名驗證失敗：{e}")
        return False

# 導出路由器
__all__ = ["router"] 