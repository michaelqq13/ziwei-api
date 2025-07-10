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
from sqlalchemy import create_engine, text

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
from slowapi import Limiter
from slowapi.util import get_remote_address

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter()

# 記憶體中的用戶會話管理
user_sessions: Dict[str, MemoryUserSession] = {}

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

# 在文件頂部添加速率限制器
limiter = Limiter(key_func=get_remote_address)

def get_optional_db() -> Optional[Session]:
    """獲取可選的數據庫會話"""
    try:
        # 嘗試創建數據庫會話
        database_url = DatabaseConfig.get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        # 測試數據庫連接
        db.execute(text("SELECT 1"))
        logger.info("數據庫連接成功")
        return db
    except Exception as e:
        logger.warning(f"數據庫連接失敗，使用簡化模式: {e}")
        return None

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

def get_or_create_session(user_id: str) -> MemoryUserSession:
    """獲取或創建用戶會話"""
    if user_id not in user_sessions:
        user_sessions[user_id] = MemoryUserSession(user_id)
    return user_sessions[user_id]

def send_line_message(user_id: str, message: str, quick_reply_items: List[Dict] = None) -> bool:
    """發送LINE訊息，支援可選 Quick Reply"""
    try:
        from app.config.linebot_config import LineBotConfig
        import requests

        # 構建訊息物件
        text_message = {
            'type': 'text',
            'text': message
        }
        # 如果有 Quick Reply items，加入 quickReply 欄位
        if quick_reply_items:
            text_message['quickReply'] = {'items': quick_reply_items}

        # 構建 push 請求資料
        headers = {
            'Authorization': f'Bearer {LineBotConfig.CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'to': user_id,
            'messages': [text_message]
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
    return None  # 返回 None 表示訊息已經發送，不需要再次發送

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
            
            # 修正：只保存必要的識別資訊，不保存完整的占卜結果
            session.set_data("last_divination_id", result.get("divination_id"))
            session.set_data("last_divination_time", result.get("divination_time"))
            # 根據用戶權限決定用戶類型
            user_type = "admin" if user.is_admin else ("premium" if user.is_premium else "free")
            session.set_data("user_type", user_type)  # 保存用戶類型用於權限控制
            
            # 檢查管理員權限
            is_admin = False
            try:
                if db:
                    is_admin = permission_manager.check_admin_access(user.line_user_id, db)
            except Exception as perm_error:
                logger.warning(f"無法檢查管理員權限: {perm_error}")
            
            # 獲取用戶類型
            user_type = "free"  # 默認免費會員
            try:
                if db:
                    user_stats = permission_manager.get_user_stats(db, user)
                    user_type = "admin" if user_stats["user_info"]["is_admin"] else ("premium" if user_stats["membership_info"]["is_premium"] else "free")
            except Exception as perm_error:
                logger.warning(f"無法獲取用戶權限: {perm_error}")
            
            # 使用新的Flex Message生成器
            flex_generator = DivinationFlexMessageGenerator()
            flex_messages = flex_generator.generate_divination_messages(result, is_admin, user_type)
            
            if flex_messages:
                # 發送Flex Messages
                success = send_line_flex_messages(user.line_user_id, flex_messages)
                if success:
                    return None  # 已經發送Flex訊息，不需要返回文字
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

def parse_time_input(time_text: str) -> Optional[datetime]:
    """
    解析用戶輸入的時間格式
    支持多種時間格式：
    - "2024-01-15 14:30"
    - "今天 14:30"
    - "昨天 09:15"
    - "1小時前"
    - "30分鐘前"
    """
    try:
        time_text = time_text.strip()
        current_time = get_current_taipei_time()
        
        # 格式1: 完整日期時間 "2024-01-15 14:30"
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', time_text):
            return datetime.strptime(time_text, "%Y-%m-%d %H:%M").replace(tzinfo=TAIPEI_TZ)
        
        # 格式2: 今天/昨天 + 時間
        if time_text.startswith("今天"):
            time_part = time_text.replace("今天", "").strip()
            if re.match(r'\d{2}:\d{2}', time_part):
                hour, minute = map(int, time_part.split(':'))
                return current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if time_text.startswith("昨天"):
            time_part = time_text.replace("昨天", "").strip()
            if re.match(r'\d{2}:\d{2}', time_part):
                hour, minute = map(int, time_part.split(':'))
                yesterday = current_time - timedelta(days=1)
                return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # 格式3: 相對時間 "1小時前", "30分鐘前"
        if "小時前" in time_text:
            hours = int(re.search(r'(\d+)小時前', time_text).group(1))
            return current_time - timedelta(hours=hours)
        
        if "分鐘前" in time_text:
            minutes = int(re.search(r'(\d+)分鐘前', time_text).group(1))
            return current_time - timedelta(minutes=minutes)
        
        # 格式4: 只有時間 "14:30"
        if re.match(r'\d{2}:\d{2}', time_text):
            hour, minute = map(int, time_text.split(':'))
            target_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果時間已經過了，假設是昨天
            if target_time > current_time:
                target_time = target_time - timedelta(days=1)
            
            return target_time
        
        return None
        
    except Exception as e:
        logger.error(f"解析時間輸入錯誤: {e}")
        return None

def handle_time_divination_request(db: Optional[Session], user: LineBotUser, session: MemoryUserSession) -> str:
    """處理指定時間占卜請求（僅限管理員）"""
    
    # 檢查管理員權限
    try:
        if db:
            user_stats = permission_manager.get_user_stats(db, user)
            is_admin = user_stats["user_info"]["is_admin"]
            
            if not is_admin:
                return """🔒 **指定時間占卜** 

此功能僅限管理員使用！

👑 **管理員專屬功能：**
• 指定時間占卜分析
• 回溯特定時刻運勢
• 事件時間點解析
• 詳細占卜歷史記錄

✨ 請聯繫系統管理員獲取權限！"""
    except Exception as e:
        logger.warning(f"檢查管理員權限失敗: {e}")
        return "系統暫時無法使用，請稍後再試。"
    
    # 開始指定時間占卜流程
    session.set_state("waiting_for_time_divination_gender")
    
    quick_reply_items = [
        {"type": "action", "action": {"type": "message", "label": "👨 男性", "text": "男"}},
        {"type": "action", "action": {"type": "message", "label": "👩 女性", "text": "女"}}
    ]
    
    message = """🕐 **指定時間占卜** ✨ (管理員專用)

可以針對特定時間點進行占卜分析

⚡ **請選擇性別：**"""
    
    # 發送帶有Quick Reply按鈕的訊息
    send_line_message(user.line_user_id, message, quick_reply_items)
    return None

def handle_time_divination_gender_input(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理指定時間占卜的性別輸入"""
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
    
    # 保存性別，進入時間選擇階段
    session.set_data("time_divination_gender", gender)
    session.set_state("waiting_for_time_selection")
    
    # 提供時間選擇的快速按鈕
    current_time = get_current_taipei_time()
    
    quick_reply_items = [
        {"type": "action", "action": {"type": "message", "label": "🕐 1小時前", "text": "1小時前"}},
        {"type": "action", "action": {"type": "message", "label": "🕑 2小時前", "text": "2小時前"}},
        {"type": "action", "action": {"type": "message", "label": "🕒 3小時前", "text": "3小時前"}},
        {"type": "action", "action": {"type": "message", "label": "🕓 6小時前", "text": "6小時前"}},
        {"type": "action", "action": {"type": "message", "label": "📅 昨天同時", "text": "昨天同時"}},
        {"type": "action", "action": {"type": "message", "label": "⏰ 自訂時間", "text": "自訂時間"}}
    ]
    
    message = f"""⏰ **選擇目標時間** 

當前時間：{current_time.strftime('%Y-%m-%d %H:%M')}

🚀 **快速選擇：**
• 點擊下方按鈕快速選擇時間
• 或選擇「自訂時間」手動輸入"""
    
    send_line_message(user.line_user_id, message, quick_reply_items)
    return None

def handle_time_selection(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理時間選擇"""
    text = text.strip()
    current_time = get_current_taipei_time()
    target_time = None
    
    # 快速時間選擇
    if text == "1小時前":
        target_time = current_time - timedelta(hours=1)
    elif text == "2小時前":
        target_time = current_time - timedelta(hours=2)
    elif text == "3小時前":
        target_time = current_time - timedelta(hours=3)
    elif text == "6小時前":
        target_time = current_time - timedelta(hours=6)
    elif text == "昨天同時":
        target_time = current_time - timedelta(days=1)
    elif text == "自訂時間":
        # 進入自訂時間模式
        session.set_state("waiting_for_custom_time_input")
        
        # 提供更多自訂選項
        quick_reply_items = [
            {"type": "action", "action": {"type": "message", "label": "📅 今天 09:00", "text": "今天 09:00"}},
            {"type": "action", "action": {"type": "message", "label": "📅 今天 12:00", "text": "今天 12:00"}},
            {"type": "action", "action": {"type": "message", "label": "📅 今天 15:00", "text": "今天 15:00"}},
            {"type": "action", "action": {"type": "message", "label": "📅 今天 18:00", "text": "今天 18:00"}},
            {"type": "action", "action": {"type": "message", "label": "📅 昨天 12:00", "text": "昨天 12:00"}},
            {"type": "action", "action": {"type": "message", "label": "✏️ 手動輸入", "text": "手動輸入"}}
        ]
        
        message = """📝 **自訂時間選擇**

🚀 **常用時間：**
• 點擊下方按鈕快速選擇
• 或選擇「手動輸入」自由輸入

✏️ **手動輸入格式：**
• 今天 14:30
• 昨天 09:15
• 2024-01-15 14:30
• 1小時前
• 30分鐘前

請輸入您的目標時間："""
        
        send_line_message(user.line_user_id, message, quick_reply_items)
        return None
    else:
        # 嘗試解析其他時間格式
        target_time = parse_time_input(text)
        if not target_time:
            return """❓ 時間格式不正確，請重新選擇：

🚀 **請點擊上方按鈕選擇時間**
或輸入以下格式：
• 今天 14:30
• 昨天 09:15
• 1小時前
• 30分鐘前"""
    
    # 如果成功解析時間，執行占卜
    if target_time:
        return execute_time_divination(db, user, session, target_time, text)
    
    return "時間解析失敗，請重新選擇。"

def handle_custom_time_input(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理自訂時間輸入"""
    text = text.strip()
    current_time = get_current_taipei_time()
    
    # 處理預設時間選項
    if text == "今天 09:00":
        target_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    elif text == "今天 12:00":
        target_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    elif text == "今天 15:00":
        target_time = current_time.replace(hour=15, minute=0, second=0, microsecond=0)
    elif text == "今天 18:00":
        target_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)
    elif text == "昨天 12:00":
        yesterday = current_time - timedelta(days=1)
        target_time = yesterday.replace(hour=12, minute=0, second=0, microsecond=0)
    elif text == "手動輸入":
        # 進入完全手動輸入模式
        session.set_state("waiting_for_manual_time_input")
        return """✏️ **手動輸入時間**

請輸入目標時間，支持以下格式：

📝 **格式範例：**
• 今天 14:30
• 昨天 09:15
• 2024-01-15 14:30
• 1小時前
• 30分鐘前

請輸入您的目標時間："""
    else:
        # 嘗試解析用戶輸入
        target_time = parse_time_input(text)
        if not target_time:
            return """❓ 時間格式不正確，請重新輸入：

📝 **支持格式：**
• 今天 14:30
• 昨天 09:15
• 2024-01-15 14:30
• 1小時前
• 30分鐘前

請重新輸入目標時間："""
    
    # 執行占卜
    return execute_time_divination(db, user, session, target_time, text)

def execute_time_divination(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, target_time: datetime, original_input: str) -> str:
    """執行指定時間占卜"""
    
    # 檢查時間範圍
    current_time = get_current_taipei_time()
    time_diff = current_time - target_time
    
    if time_diff.days > 30:
        return "⚠️ 目標時間不能超過 30 天前，請重新選擇。"
    
    if time_diff.days < -7:
        return "⚠️ 目標時間不能超過 7 天後，請重新選擇。"
    
    # 執行占卜
    try:
        gender = session.get_data("time_divination_gender")
        
        logger.info(f"執行指定時間占卜 - 管理員: {user.line_user_id}, 時間: {target_time}, 性別: {gender}")
        
        result = divination_logic.perform_divination(gender, target_time, db)
        
        if result["success"]:
            # 保存指定時間占卜記錄
            try:
                if db:
                    from app.models.divination import TimeDivinationHistory
                    
                    time_divination_record = TimeDivinationHistory(
                        user_id=user.id,
                        target_time=target_time,
                        current_time=current_time,
                        gender=gender,
                        purpose=f"管理員指定時間占卜: {original_input}",
                        taichi_palace=result["taichi_palace"],
                        minute_dizhi=result["minute_dizhi"],
                        sihua_results=json.dumps(result["sihua_results"], ensure_ascii=False)
                    )
                    
                    db.add(time_divination_record)
                    db.commit()
                    logger.info("指定時間占卜記錄已保存")
            except Exception as db_error:
                logger.warning(f"保存指定時間占卜記錄失敗: {db_error}")
            
            # 清除會話狀態
            session.clear()
            
            # 管理員使用，直接設為 admin 類型
            user_type = "admin"
            
            # 使用 Flex Message 生成器
            flex_generator = DivinationFlexMessageGenerator()
            
            # 修改結果標題，顯示是指定時間占卜
            result["divination_title"] = f"🕐 指定時間占卜結果 (管理員)"
            result["time_note"] = f"目標時間: {target_time.strftime('%Y-%m-%d %H:%M')}"
            
            flex_messages = flex_generator.generate_divination_messages(result, True, user_type)
            
            if flex_messages:
                # 發送Flex Messages
                success = send_line_flex_messages(user.line_user_id, flex_messages)
                if success:
                    return None  # 已經發送Flex訊息
                else:
                    return format_time_divination_result_text(result, target_time, True)
            else:
                return format_time_divination_result_text(result, target_time, True)
        else:
            session.clear()
            return "🔮 指定時間占卜過程發生錯誤，請稍後再試。"
            
    except Exception as e:
        logger.error(f"指定時間占卜過程錯誤: {e}")
        session.clear()
        return "🔮 指定時間占卜系統暫時無法使用，請稍後再試。"

def format_time_divination_result_text(result: Dict, target_time: datetime, is_admin: bool = False) -> str:
    """格式化指定時間占卜結果為文字訊息"""
    if not result.get("success"):
        return "🔮 指定時間占卜過程發生錯誤，請稍後再試。"
    
    # 基本資訊
    gender_text = "男性" if result["gender"] == "M" else "女性"
    time_str = target_time.strftime("%Y-%m-%d %H:%M")
    
    message = f"""🕐 **指定時間占卜結果** ✨

📅 目標時間：{time_str} (台北時間)
👤 性別：{gender_text}
🏰 太極點命宮：{result["taichi_palace"]}
🕰️ 分鐘地支：{result["minute_dizhi"]}
⭐ 宮干：{result["palace_tiangan"]}

━━━━━━━━━━━━━━━━━
🔮 **四化解析**

💰 祿：有利的事情（好運、財運、順利、機會）
👑 權：有主導權的事情（領導力、決策權、掌控力）
🌟 科：提升地位名聲（受人重視、被看見、受表揚）
⚡ 忌：可能困擾的事情（阻礙、困難、需要注意）

"""
    
    # 添加四化結果
    for i, sihua in enumerate(result["sihua_results"], 1):
        emoji_map = {"忌": "⚡", "祿": "💰", "權": "👑", "科": "🌟"}
        emoji = emoji_map.get(sihua["type"], "⭐")
        
        message += f"\n━━━━━━━━━━━━━━━━━━━━\n"
        message += f"{emoji} **{sihua['type']}星 - {sihua['star']}**\n"
        message += f"   落宮：{sihua['palace']}\n\n"
        
        explanation = sihua.get('explanation', '')
        if explanation:
            short_explanation = explanation[:200] + "..." if len(explanation) > 200 else explanation
            message += f"{short_explanation}\n"
    
    message += "\n━━━━━━━━━━━━━━━━━\n"
    message += "🕐 指定時間占卜完成 ✨"
    
    return message

@router.post("/webhook")
@limiter.limit("100/minute")  # LINE webhook 速率限制
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
            # 清理數據庫會話（如果存在）
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.warning(f"關閉數據庫會話時發生錯誤: {e}")
        
    except Exception as e:
        logger.error(f"Webhook處理錯誤：{e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_line_event(event: dict, db: Optional[Session]):
    """處理LINE事件（支持可選數據庫）"""
    try:
        event_type = event.get("type")
        user_id = event.get("source", {}).get("userId")
        
        logger.info(f"處理事件：{event_type}，用戶：{user_id}，數據庫：{'有' if db else '無'}")
        
        if event_type == "message":
            await handle_message_event(event, db)
        elif event_type == "postback":
            await handle_postback_event(event, db)
        elif event_type == "follow":
            handle_follow_event(event, db)
        elif event_type == "unfollow":
            handle_unfollow_event(event, db)
        else:
            logger.info(f"忽略事件類型：{event_type}")
        
    except Exception as e:
        logger.error(f"處理LINE事件錯誤：{e}")

async def handle_postback_event(event: dict, db: Optional[Session]):
    """處理PostBack事件（分頁切換等）"""
    try:
        postback = event.get("postback", {})
        postback_data = postback.get("data", "")
        user_id = event.get("source", {}).get("userId")
        
        logger.info(f"收到PostBack事件 - 用戶: {user_id}, 數據: {postback_data}")
        
        # 處理駕駛視窗分頁切換
        if postback_data.startswith("tab_"):
            try:
                from app.utils.driver_view_rich_menu_handler import driver_view_handler
                
                # 使用駕駛視窗處理器處理分頁切換
                success = driver_view_handler.handle_postback_event(user_id, postback_data)
                
                if success:
                    # 靜默切換 - 不發送確認訊息，只記錄日誌
                    tab_name = postback_data.replace("tab_", "")
                    tab_info = driver_view_handler.get_tab_info(tab_name)
                    tab_display_name = tab_info.get("name", tab_name)
                    
                    logger.info(f"✅ 用戶 {user_id} 靜默切換到分頁: {tab_display_name}")
                else:
                    logger.error(f"❌ 用戶 {user_id} 分頁切換失敗: {postback_data}")
                    
            except ImportError as e:
                logger.warning(f"⚠️ 駕駛視窗處理器未找到，使用備用處理: {e}")
                # 備用處理邏輯
                await handle_legacy_tab_switch(user_id, postback_data, db)
            except Exception as e:
                logger.error(f"❌ 處理駕駛視窗分頁切換失敗: {e}")
                # 分頁切換失敗時也不發送錯誤訊息，保持靜默
                logger.warning(f"⚠️ 分頁切換失敗，但保持靜默: {user_id}")
        
        # 處理其他 PostBack 事件
        else:
            logger.info(f"📥 收到其他 PostBack 事件: {postback_data}")
            # 這裡可以添加其他 PostBack 事件的處理邏輯
            
    except Exception as e:
        logger.error(f"❌ 處理PostBack事件失敗: {e}")

async def handle_legacy_tab_switch(user_id: str, postback_data: str, db: Optional[Session]):
    """備用分頁切換處理（當駕駛視窗處理器不可用時）"""
    try:
        tab_mapping = {
            "tab_basic": "基本功能",
            "tab_fortune": "運勢", 
            "tab_advanced": "進階選項"
        }
        
        tab_name = tab_mapping.get(postback_data, "未知分頁")
        # 備用處理也保持靜默，不發送訊息
        logger.info(f"使用備用處理靜默切換分頁: {user_id} -> {tab_name}")
        
    except Exception as e:
        logger.error(f"❌ 備用分頁切換處理失敗: {e}")

async def handle_message_event(event: dict, db: Optional[Session]):
    """處理訊息事件（支持可選數據庫）"""
    try:
        message = event.get("message", {})
        message_type = message.get("type")
        user_id = event.get("source", {}).get("userId")
        
        if message_type == "text":
            text = message.get("text", "").strip()
            
            # 完整模式：使用數據庫和會話管理
            try:
                user = get_or_create_user(db, user_id)
                session = get_or_create_session(user_id)
                
                # 處理不同的指令
                if text in ["會員資訊", "個人資訊", "我的資訊"]:
                    try:
                        user_stats = permission_manager.get_user_stats(db, user)
                        response = format_user_info(user_stats)
                        if response:
                            send_line_message(user_id, response)
                        else:
                            send_line_message(user_id, "⚠️ 無法獲取會員資訊，請稍後再試。")
                    except Exception as member_error:
                        logger.error(f"獲取會員資訊失敗 - 用戶: {user_id}, 錯誤: {member_error}")
                        # 提供更具體的錯誤訊息
                        if "database" in str(member_error).lower() or "connection" in str(member_error).lower():
                            send_line_message(user_id, "🔧 資料庫連線問題，正在修復中\n\n請稍後再嘗試查看會員資訊。")
                        elif "permission" in str(member_error).lower():
                            send_line_message(user_id, "🔒 權限驗證失敗\n\n請重新加入好友或聯繫客服。")
                        else:
                            send_line_message(user_id, f"⚠️ 會員資訊暫時無法顯示\n\n錯誤類型: {type(member_error).__name__}\n請聯繫客服或稍後再試。")
                    return  # 重要：防止觸發默認歡迎訊息
                    
                elif text in ["占卜", "算命", "紫微斗數", "開始占卜", "本週占卜"]:
                    response = handle_divination_request(db, user, session)
                    if response:
                        send_line_message(user_id, response)
                    return  # 重要：防止觸發默認歡迎訊息
                
                # 處理流年流月流日運勢按鈕
                elif text in ["流年運勢"]:
                    # 檢查用戶權限
                    user_stats = permission_manager.get_user_stats(db, user)
                    is_premium = user_stats["membership_info"]["is_premium"]
                    is_admin = user_stats["user_info"]["is_admin"]
                    
                    if is_admin or is_premium:
                        send_line_message(user_id, """🌍 流年運勢功能
                        
✨ 此功能正在開發中，敬請期待！

🔮 **即將推出：**
• 詳細的年度運勢分析
• 事業、財運、感情運勢預測
• 關鍵時間點提醒
• 個人化建議指引

💫 感謝您的耐心等待，我們正在為您準備更精準的流年運勢分析！""")
                    else:
                        send_line_message(user_id, """🌍 流年運勢功能
                        
🔒 此功能為付費會員專屬功能

💎 **升級付費會員即可享有：**
• 詳細的年度運勢分析
• 事業、財運、感情運勢預測
• 關鍵時間點提醒
• 個人化建議指引

✨ 讓紫微斗數為您提供更深入的人生指引！""")
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif text in ["流月運勢"]:
                    # 檢查用戶權限
                    user_stats = permission_manager.get_user_stats(db, user)
                    is_premium = user_stats["membership_info"]["is_premium"]
                    is_admin = user_stats["user_info"]["is_admin"]
                    
                    if is_admin or is_premium:
                        send_line_message(user_id, """🌙 流月運勢功能
                        
✨ 此功能正在開發中，敬請期待！

🔮 **即將推出：**
• 每月運勢變化分析
• 月度重點事件預測
• 最佳行動時機建議
• 注意事項提醒

💫 感謝您的耐心等待，我們正在為您準備更精準的流月運勢分析！""")
                    else:
                        send_line_message(user_id, """🌙 流月運勢功能
                        
🔒 此功能為付費會員專屬功能

💎 **升級付費會員即可享有：**
• 每月運勢變化分析
• 月度重點事件預測
• 最佳行動時機建議
• 注意事項提醒

✨ 讓紫微斗數為您提供更深入的人生指引！""")
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif text in ["流日運勢"]:
                    # 檢查用戶權限
                    user_stats = permission_manager.get_user_stats(db, user)
                    is_premium = user_stats["membership_info"]["is_premium"]
                    is_admin = user_stats["user_info"]["is_admin"]
                    
                    if is_admin or is_premium:
                        send_line_message(user_id, """🪐 流日運勢功能
                        
✨ 此功能正在開發中，敬請期待！

🔮 **即將推出：**
• 每日運勢詳細分析
• 當日吉凶時辰提醒
• 重要決策建議
• 日常生活指引

💫 感謝您的耐心等待，我們正在為您準備更精準的流日運勢分析！""")
                    else:
                        send_line_message(user_id, """🪐 流日運勢功能
                        
🔒 此功能為付費會員專屬功能

💎 **升級付費會員即可享有：**
• 每日運勢詳細分析
• 當日吉凶時辰提醒
• 重要決策建議
• 日常生活指引

✨ 讓紫微斗數為您提供更深入的人生指引！""")
                    return  # 重要：防止觸發默認歡迎訊息
                    
                elif session.state == "waiting_for_gender":
                    response = handle_gender_input(db, user, session, text)
                    if response:
                        send_line_message(user_id, response)
                    return  # 重要：防止觸發默認歡迎訊息
                
                # 新增指定時間占卜指令（僅限管理員）
                elif text in ["指定時間占卜", "時間占卜", "指定時間"]:
                    response = handle_time_divination_request(db, user, session)
                    if response:
                        send_line_message(user_id, response)
                    return  # 重要：防止觸發默認歡迎訊息
                
                # 處理分頁切換請求 - 靜默切換，不發送訊息
                elif text in ["切換到基本功能", "基本功能", "切換到基本"]:
                    from app.utils.dynamic_rich_menu import handle_tab_switch_request
                    success = handle_tab_switch_request(user_id, "basic")
                    # 靜默切換，不發送訊息
                    logger.info(f"用戶 {user_id} 切換到基本功能分頁: {'成功' if success else '失敗'}")
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif text in ["切換到運勢", "運勢", "切換到運勢分頁"]:
                    from app.utils.dynamic_rich_menu import handle_tab_switch_request
                    success = handle_tab_switch_request(user_id, "fortune")
                    # 靜默切換，不發送訊息
                    logger.info(f"用戶 {user_id} 切換到運勢分頁: {'成功' if success else '失敗'}")
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif text in ["切換到進階選項", "進階選項", "管理員選項", "切換到進階"]:
                    from app.utils.dynamic_rich_menu import handle_tab_switch_request
                    success = handle_tab_switch_request(user_id, "admin")
                    # 靜默切換，不發送訊息
                    logger.info(f"用戶 {user_id} 切換到進階選項分頁: {'成功' if success else '失敗'}")
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif session.state == "waiting_for_time_divination_gender":
                    response = handle_time_divination_gender_input(db, user, session, text)
                    if response:
                        send_line_message(user_id, response)
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif session.state == "waiting_for_time_selection":
                    response = handle_time_selection(db, user, session, text)
                    if response:
                        send_line_message(user_id, response)
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif session.state == "waiting_for_custom_time_input":
                    response = handle_custom_time_input(db, user, session, text)
                    if response:
                        send_line_message(user_id, response)
                    return  # 重要：防止觸發默認歡迎訊息
                
                elif session.state == "waiting_for_manual_time_input":
                    # 手動輸入時間，直接使用原來的解析邏輯
                    target_time = parse_time_input(text)
                    if target_time:
                        response = execute_time_divination(db, user, session, target_time, text)
                        if response:
                            send_line_message(user_id, response)
                    else:
                        send_line_message(user_id, """❓ 時間格式不正確，請重新輸入：

📝 **支持格式：**
• 今天 14:30
• 昨天 09:15  
• 2024-01-15 14:30
• 1小時前
• 30分鐘前

請重新輸入目標時間：""")
                    return  # 重要：防止觸發默認歡迎訊息

                # 檢查是否為四化更多解釋請求  
                elif "查看" in text and ("星更多解釋" in text or "星完整解釋" in text):
                    # 檢查用戶權限
                    from app.logic.permission_manager import permission_manager
                    user_stats = permission_manager.get_user_stats(db, user)
                    user_type = "admin" if user_stats["user_info"]["is_admin"] else ("premium" if user_stats["membership_info"]["is_premium"] else "free")
                    
                    # 解析四化類型
                    sihua_type = None
                    for st in ["祿", "權", "科", "忌"]:
                        if f"查看{st}星更多解釋" in text or f"查看{st}星完整解釋" in text:
                            sihua_type = st
                            break
                    
                    # 管理員和付費會員可以查看更多解釋
                    if user_type not in ["admin", "premium"]:
                        send_line_message(user_id, "🔒 詳細解釋功能需要升級會員\n\n💎 **升級會員享有：**\n• 查看四化完整解釋\n• 獲得詳細運勢分析\n• 專業命理詳細解讀\n\n✨ 升級即可享受更深度的紫微斗數解析！")
                        return  # 重要：防止觸發默認歡迎訊息
                    
                    if sihua_type:
                        # 處理四化更多解釋查看請求（僅限管理員）
                        try:
                            # 獲取用戶最近的占卜結果
                            from app.models.linebot_models import DivinationHistory
                            from app.utils.divination_flex_message import DivinationFlexMessageGenerator
                            
                            # 查找用戶最近的占卜記錄
                            recent_divination = db.query(DivinationHistory).filter(
                                DivinationHistory.user_id == user.id
                            ).order_by(DivinationHistory.divination_time.desc()).first()
                            
                            if not recent_divination:
                                send_line_message(user_id, "🔮 請先進行占卜，才能查看四化詳細解釋喔！\n\n💫 點擊「本週占卜」開始您的占卜之旅。")
                                return
                            
                            # 解析占卜結果 - 從 sihua_results 字段解析
                            import json
                            if recent_divination.sihua_results:
                                # 構建占卜結果數據結構
                                divination_result = {
                                    "sihua_results": json.loads(recent_divination.sihua_results),
                                    "gender": recent_divination.gender,
                                    "divination_time": recent_divination.divination_time.isoformat(),
                                    "taichi_palace": recent_divination.taichi_palace,
                                    "minute_dizhi": recent_divination.minute_dizhi
                                }
                            else:
                                send_line_message(user_id, "🔮 找不到完整的占卜資料，請重新進行占卜。")
                                return
                            
                            # 生成四化詳細解釋訊息（管理員看完整資訊，付費會員看隱藏資訊）
                            message_generator = DivinationFlexMessageGenerator()
                            detail_message = message_generator.generate_sihua_detail_message(
                                divination_result, 
                                sihua_type, 
                                user_type
                            )
                            
                            if detail_message:
                                # 發送詳細解釋訊息
                                send_line_flex_messages(user_id, [detail_message])
                            else:
                                send_line_message(user_id, f"🔮 {sihua_type}星詳細解釋暫時無法顯示，請稍後再試。")
                                
                        except Exception as e:
                            logger.error(f"獲取四化詳細解釋失敗: {e}")
                            send_line_message(user_id, f"🔮 {sihua_type}星詳細解釋 ✨\n\n⚠️ 系統暫時無法獲取詳細解釋，請稍後再試。\n\n💫 如果問題持續，請聯繫客服。")
                        return  # 重要：防止觸發默認歡迎訊息

                # 管理員功能
                if "更新選單" in text or "refresh menu" in text.lower():
                    try:
                        from app.utils.drive_view_rich_menu_manager import set_user_drive_view_menu
                        user_stats = permission_manager.get_user_stats(db, user)
                        user_level = "admin" if user_stats["user_info"]["is_admin"] else ("premium" if user_stats["membership_info"]["is_premium"] else "user")
                        
                        success = set_user_drive_view_menu(user_id, user_level, "basic")
                        
                        if success:
                            send_line_message(user_id, f"✅ 駕駛視窗選單更新成功！\n\n用戶等級: {user_level}\n分頁: 基本功能\n\n如果選單沒有立即更新，請：\n1. 關閉並重新開啟 LINE 應用\n2. 或者重新進入本聊天室")
                        else:
                            send_line_message(user_id, "❌ 駕駛視窗選單更新失敗，請稍後再試")
                    except Exception as e:
                        logger.error(f"❌ 更新駕駛視窗選單失敗: {e}")
                        send_line_message(user_id, "❌ 更新選單時發生錯誤")
                    return
                
                # 管理員功能
                if "創建選單" in text or "create menu" in text.lower():
                    try:
                        from app.utils.drive_view_rich_menu_manager import drive_view_manager
                        
                        # 清理舊選單並創建新的駕駛視窗選單
                        drive_view_manager.cleanup_old_menus()
                        menu_ids = drive_view_manager.setup_all_menus()
                        
                        if menu_ids:
                            menu_list = '\n'.join([f"   - {tab}: {menu_id[:8]}..." for tab, menu_id in menu_ids.items()])
                            send_line_message(user_id, f"✅ 新的駕駛視窗選單創建成功！\n\n創建的選單:\n{menu_list}\n\n所有新用戶將使用此選單系統")
                        else:
                            send_line_message(user_id, "❌ 創建駕駛視窗選單失敗")
                    except Exception as e:
                        logger.error(f"❌ 創建駕駛視窗選單失敗: {e}")
                        send_line_message(user_id, "❌ 創建選單時發生錯誤")
                    return
                
                else:
                    # 默認回覆
                    # 檢查是否為管理員用戶
                    is_admin = False
                    try:
                        if db:
                            user_stats = permission_manager.get_user_stats(db, user)
                            is_admin = user_stats["user_info"]["is_admin"]
                    except Exception as e:
                        logger.warning(f"檢查管理員權限失敗: {e}")
                    
                    if is_admin:
                        # 管理員專用訊息
                        send_line_message(user_id, """🌟 歡迎使用星空紫微斗數系統！ ✨ (管理員)

🔮 **主要功能：**
• 本週占卜 - 根據當下時間占卜運勢
• 會員資訊 - 查看個人資訊和使用統計

👑 **管理員專屬功能：**
• 指定時間占卜 - 回溯特定時間點運勢

💫 **使用方式：**
• 點擊下方星球按鈕快速操作
• 或直接輸入指令文字：
  - 「本週占卜」或「占卜」
  - 「指定時間占卜」或「時間占卜」
  - 「會員資訊」

⭐ 願紫微斗數為您指引人生方向！""")
                    else:
                        # 一般用戶訊息
                        send_line_message(user_id, """🌟 歡迎使用星空紫微斗數系統！ ✨

🔮 **主要功能：**
• 本週占卜 - 根據當下時間占卜運勢
• 會員資訊 - 查看個人資訊和使用統計

💫 **使用方式：**
• 點擊下方星球按鈕快速操作
• 或直接輸入指令文字

⭐ 願紫微斗數為您指引人生方向！""")
                    
            except Exception as e:
                logger.error(f"處理用戶請求失敗：{e}")
                send_line_message(user_id, "系統暫時忙碌，請稍後再試。")
                
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
                
                # 檢查用戶角色並設置對應的 Rich Menu
                try:
                    from app.utils.drive_view_rich_menu_manager import set_user_drive_view_menu
                    user_stats = permission_manager.get_user_stats(db, user)
                    
                    # 使用新的駕駛視窗選單系統
                    user_level = "admin" if user_stats["user_info"]["is_admin"] else ("premium" if user_stats["membership_info"]["is_premium"] else "user")
                    success = set_user_drive_view_menu(user_id, user_level, "basic")
                    
                    if success:
                        logger.info(f"✅ 成功為用戶 {user_id} 設置駕駛視窗選單 - 等級: {user_level}")
                    else:
                        logger.warning(f"❌ 為用戶 {user_id} 設置駕駛視窗選單失敗")
                        
                except Exception as menu_error:
                    logger.warning(f"❌ 設置用戶駕駛視窗選單失敗: {menu_error}")
                    
            except Exception as e:
                logger.warning(f"創建用戶記錄失敗：{e}")
        else:
            logger.info(f"簡化模式：用戶加入 {user_id}")

        # 發送歡迎訊息
        welcome_message = """🌟 歡迎使用星空紫微斗數系統！ ✨

請點擊下方星球按鈕「本週占卜」開始您的占卜之旅。

🔮 **系統特色：**
• 即時占卜解析 - 根據當下時間占卜
• 四化星曜詳解 - 深度解析運勢變化
• 太極點轉換分析 - 專業命理技術
• 星空主題介面 - 美觀易用的操作體驗

⭐ 願紫微斗數為您指引人生方向！"""
        
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
    
    return message

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

def verify_line_signature(body: bytes, signature: str) -> bool:
    """驗證LINE簽名"""
    try:
        import hmac
        import hashlib
        import base64
        
        # 驗證配置是否正確載入
        LineBotConfig._validate_line_config()
        
        # 使用配置中的 LINE Channel Secret
        channel_secret = LineBotConfig.CHANNEL_SECRET
        
        # 詳細的配置檢查
        if not channel_secret:
            logger.error("❌ LINE_CHANNEL_SECRET 環境變數為空")
            logger.error("請確認在 Railway 環境變數中設定了 LINE_CHANNEL_SECRET")
            return False
            
        if channel_secret == "your_channel_secret_here":
            logger.error("❌ LINE_CHANNEL_SECRET 仍為預設值，簽名驗證將失敗")
            logger.error("正確的 Channel Secret 應為: 611969a2b460d46e71648a2c3a6d54fb")
            logger.error("請在 Railway 專案設定中添加環境變數：")
            logger.error("變數名: LINE_CHANNEL_SECRET")
            logger.error("變數值: 611969a2b460d46e71648a2c3a6d54fb")
            return False
        
        # 計算預期的簽名
        expected_signature = base64.b64encode(
            hmac.new(
                channel_secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # 比較簽名
        if signature == expected_signature:
            logger.info("✅ LINE 簽名驗證成功")
            return True
        else:
            logger.error("❌ LINE 簽名驗證失敗")
            logger.error(f"預期簽名: {expected_signature[:20]}...")
            logger.error(f"實際簽名: {signature[:20]}...")
            logger.error(f"使用的 Channel Secret: {channel_secret[:8]}...")
            logger.error(f"請求主體長度: {len(body)} bytes")
            
            # 如果是預期的 Channel Secret，提供詳細的除錯資訊
            if channel_secret == "611969a2b460d46e71648a2c3a6d54fb":
                logger.info("Channel Secret 正確，但簽名不匹配 - 可能是請求主體差異")
                logger.debug(f"請求主體內容: {body.decode('utf-8', errors='replace')[:200]}...")
            else:
                logger.error("Channel Secret 不正確，請檢查環境變數設定")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ LINE 簽名驗證過程發生錯誤: {e}")
        logger.error(f"錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"完整錯誤追蹤: {traceback.format_exc()}")
        return False

# 健康檢查端點
@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "LINE Bot Webhook"}

# 導出路由器
__all__ = ["router"] 