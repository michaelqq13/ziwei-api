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
from linebot.v3.messaging import FlexBubble, FlexBox, FlexText, FlexSeparator, FlexMessage

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
    
    # 檢查是否為指定時間占卜
    target_time_str = session.get_data("target_time")
    if target_time_str:
        # 指定時間占卜流程
        try:
            target_time = datetime.fromisoformat(target_time_str)
            original_input = session.get_data("original_input", "")
            
            result = divination_logic.perform_divination(user, gender, target_time, db)
            
            if result["success"]:
                # 獲取用戶權限等級
                user_stats = permission_manager.get_user_stats(db, user)
                is_admin = user_stats["user_info"]["is_admin"]
                user_type = "admin" if is_admin else ("premium" if user_stats["membership_info"]["is_premium"] else "free")

                # 使用 Flex Message產生器 - 確保管理員看到太極十二宮
                message_generator = DivinationFlexMessageGenerator()
                flex_messages = message_generator.generate_divination_messages(result, is_admin, user_type)
                
                # 發送 Flex 訊息
                if flex_messages:
                    # 附加時間信息
                    time_info_message = f"⏰ **指定時間占卜結果**\n\n📅 查詢時間：{target_time.strftime('%Y年%m月%d日 %H:%M')}\n👤 性別：{'男性' if gender == 'M' else '女性'}\n\n💫 以下是該時間點的詳細分析："
                    send_line_message(user.line_user_id, time_info_message)
                    send_line_flex_messages(user.line_user_id, flex_messages)
                    
                    # 在占卜結果後發送智能 Quick Reply
                    send_smart_quick_reply_after_divination(user.line_user_id, result, user_type)
                else:
                    return "占卜結果生成失敗，請稍後再試。"
            else:
                return result.get("error", "占卜失敗，請稍後再試。")
        except Exception as e:
            logger.error(f"執行指定時間占卜失敗: {e}", exc_info=True)
            return "執行指定時間占卜時發生錯誤。"
        finally:
            session.clear_state()
            session.clear_data()
        
        return None  # 訊息已發送，不需要再次發送
    
    # 一般占卜流程
    try:
        current_time = get_current_taipei_time()
        result = divination_logic.perform_divination(user, gender, current_time, db)
        
        if result["success"]:
            # 獲取用戶權限等級
            is_admin = False
            if db:
                user_stats = permission_manager.get_user_stats(db, user)
                is_admin = user_stats["user_info"]["is_admin"]
                user_type = "admin" if is_admin else ("premium" if user_stats["membership_info"]["is_premium"] else "free")
            else:
                user_type = "free"

            # 使用 Flex Message產生器 - 確保管理員看到太極十二宮
            message_generator = DivinationFlexMessageGenerator()
            flex_messages = message_generator.generate_divination_messages(result, is_admin, user_type)
            
            # 發送 Flex 訊息
            if flex_messages:
                send_line_flex_messages(user.line_user_id, flex_messages)
                
                # 在占卜結果後發送智能 Quick Reply
                send_smart_quick_reply_after_divination(user.line_user_id, result, user_type)
            else:
                return "占卜結果生成失敗，請稍後再試。"
        else:
            return result.get("error", "占卜失敗，請稍後再試。")
            
    except Exception as e:
        logger.error(f"執行占卜失敗: {e}", exc_info=True)
        return "占卜服務暫時不可用，請稍後再試。"
    
    # 清理狀態
    session.clear_state()
    return None  # 返回 None 表示訊息已經發送，不需要再次發送

def send_smart_quick_reply_after_divination(user_id: str, divination_result: Dict[str, Any], user_type: str):
    """在占卜结果后发送智能 Quick Reply"""
    try:
        # 分析占卜结果中的四化类型
        sihua_results = divination_result.get("sihua_results", [])
        sihua_types = set()
        
        for sihua in sihua_results:
            sihua_type = sihua.get("type", "")
            if sihua_type in ["祿", "權", "科", "忌"]:
                sihua_types.add(sihua_type)
        
        # 构建 Quick Reply 按钮
        quick_reply_items = []
        
        # 添加太极十二宫查看选项（管理员专用）
        if user_type == "admin":
            quick_reply_items.append({
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": "🏛️ 太極十二宮",
                    "data": "action=show_taichi_palaces",
                    "displayText": "🏛️ 查看太極十二宮"
                }
            })
        
        # 根据用户类型和四化结果提供不同选项
        if user_type in ["admin", "premium"]:
            # 付费会员和管理员：提供四化详细解释选项
            for sihua_type in sorted(sihua_types):
                if len(quick_reply_items) < 11:  # 限制按钮数量
                    quick_reply_items.append({
                        "type": "action",
                        "action": {
                            "type": "message",
                            "label": f"✨ {sihua_type}星詳解",
                            "text": f"查看{sihua_type}星更多解釋"
                        }
                    })
            
            # 其他功能选项
            quick_reply_items.extend([
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "🔮 重新占卜",
                        "data": "action=weekly_fortune",
                        "displayText": "🔮 重新占卜"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "🌟 功能選單",
                        "data": "action=show_control_panel",
                        "displayText": "🌟 功能選單"
                    }
                }
            ])
        else:
            # 免费会员：提供升级提示和基本选项
            quick_reply_items.extend([
                {
                    "type": "action",
                    "action": {
                        "type": "message",
                        "label": "💎 升級會員看詳解",
                        "text": "如何升級會員"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "🔮 重新占卜",
                        "data": "action=weekly_fortune",
                        "displayText": "🔮 重新占卜"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "🌟 功能選單",
                        "data": "action=show_control_panel",
                        "displayText": "🌟 功能選單"
                    }
                }
            ])
        
        # 添加通用选项
        quick_reply_items.extend([
            {
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": "👤 會員資訊",
                    "data": "action=show_member_info",
                    "displayText": "👤 會員資訊"
                }
            },
            {
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": "📖 使用說明",
                    "data": "action=show_instructions",
                    "displayText": "📖 使用說明"
                }
            }
        ])
        
        # 限制 Quick Reply 按钮数量（LINE 限制最多 13 个）
        quick_reply_items = quick_reply_items[:13]
        
        # 构建情境式引导消息
        if user_type == "admin":
            guidance_message = """🌟 **占卜完成！** ✨

您的紫微斗數分析已經完成。接下來您可以：

🏛️ **專屬功能**
• 查看太極十二宮詳細結構
• 四化完整解釋和深度分析

🎯 **探索更多**  
• 重新占卜或使用其他功能
• 查看管理員專屬的進階分析

💫 請選擇您想要的下一步操作："""
        elif user_type == "premium":
            guidance_message = """🌟 **占卜完成！** ✨

您的紫微斗數分析已經完成。接下來您可以：

💡 **深度了解**
• 點擊下方按鈕查看四化詳細解釋
• 每個四化都有獨特的意義和影響

🎯 **探索更多**  
• 重新占卜或使用其他功能
• 查看會員專屬的進階分析

💫 請選擇您想要的下一步操作："""
        else:
            guidance_message = """🌟 **占卜完成！** ✨

您的基本運勢分析已經完成。

💎 **升級會員享有**
• 四化詳細解釋和深度分析
• 流年、流月、流日運勢
• 專業命理諮詢服務

🎯 **繼續探索**
• 重新占卜或查看其他功能
• 了解會員升級優惠

💫 請選擇您想要的下一步操作："""
        
        # 延迟发送带有 Quick Reply 的引导消息，避免与Flex消息冲突
        import asyncio
        import threading
        
        def delayed_send():
            import time
            time.sleep(2)  # 延迟2秒发送
            send_line_message(user_id, guidance_message, quick_reply_items)
        
        # 在后台线程中发送延迟消息
        thread = threading.Thread(target=delayed_send)
        thread.daemon = True
        thread.start()
        
        logger.info(f"已安排延迟发送智能 Quick Reply 给用户 {user_id}，用户类型: {user_type}")
        
    except Exception as e:
        logger.error(f"发送智能 Quick Reply 失败: {e}", exc_info=True)

def format_divination_result_text(result: Dict, is_admin: bool = False) -> str:
    """格式化占卜結果為純文字（備用）"""
    
    header = "🔮 **占卜結果** ✨\n\n"
    
    # 基本資訊
    gender_text = "男性" if result.get("gender") == "M" else "女性"
    divination_time_text = result.get("divination_time", "未知時間")
    try:
        # 解析ISO格式時間
        dt_object = datetime.fromisoformat(divination_time_text)
        # 轉換為本地時間格式
        divination_time_text = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        pass
        
    base_info = (
        f"👤 **性別：** {gender_text}\n"
        f"📅 **占卜時間：** {divination_time_text}\n"
        f"☯️ **太極點命宮：** {result.get('taichi_palace', '未知')}\n"
        f"🕰️ **分鐘地支：** {result.get('minute_dizhi', '未知')}\n"
        f"🌌 **宮干：** {result.get('palace_tiangan', '未知')}\n\n"
    )
    
    # 四化結果
    sihua_header = "🌟 **四化分析** 🌟\n"
    sihua_text = ""
    sihua_results = result.get("sihua_results", [])
    
    if not sihua_results:
        sihua_text = "  (無四化結果)\n"
    else:
        for sihua in sihua_results:
            sihua_text += (
                f"  - **{sihua['type']}** ({sihua['star']}) -> {sihua['palace']}:\n"
                f"    {sihua['explanation']}\n\n"
            )
            
            # 管理員可見的額外資訊
            if is_admin:
                sihua_text += (
                    f"    **[管理員]**\n"
                    f"    觸機: {sihua.get('trigger_star', 'N/A')}\n"
                    f"    觸機宮位: {sihua.get('trigger_palace', 'N/A')}\n\n"
                )

    full_text = header + base_info + sihua_header + sihua_text
    
    return full_text

def parse_time_input(time_text: str) -> Optional[datetime]:
    """解析多種格式的時間輸入"""
    now = get_current_taipei_time()
    
    # 格式1: "今天 HH:MM"
    match = re.match(r"今天\s*(\d{1,2}):(\d{1,2})", time_text)
    if match:
        hour, minute = map(int, match.groups())
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # 格式2: "昨天 HH:MM"
    match = re.match(r"昨天\s*(\d{1,2}):(\d{1,2})", time_text)
    if match:
        hour, minute = map(int, match.groups())
        yesterday = now - timedelta(days=1)
        return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # 格式3: "YYYY-MM-DD HH:MM"
    try:
        return datetime.strptime(time_text, "%Y-%m-%d %H:%M").replace(tzinfo=TAIPEI_TZ)
    except ValueError:
        pass
    
    # 格式4: "N小時前"
    match = re.match(r"(\d+)\s*小時前", time_text)
    if match:
        hours_ago = int(match.group(1))
        return now - timedelta(hours=hours_ago)
        
    # 格式5: "N分鐘前"
    match = re.match(r"(\d+)\s*分鐘前", time_text)
    if match:
        minutes_ago = int(match.group(1))
        return now - timedelta(minutes=minutes_ago)

    return None

def handle_time_divination_request(db: Optional[Session], user: LineBotUser, session: MemoryUserSession) -> str:
    """處理指定時間占卜請求"""
    # 權限檢查
    is_admin = False
    if db:
        user_stats = permission_manager.get_user_stats(db, user)
        is_admin = user_stats["user_info"]["is_admin"]
    
    if not is_admin:
        return "🔒 **權限不足**\n\n此功能僅限管理員使用。"
    
    # 設置狀態
    session.set_state("waiting_for_time_divination_gender")
    
    # 發送訊息
    quick_reply_items = [
        {"type": "action", "action": {"type": "message", "label": "👨 男性", "text": "男"}},
        {"type": "action", "action": {"type": "message", "label": "👩 女性", "text": "女"}}
    ]
    
    message = """🔮 **指定時間占卜** ✨ (管理員模式)

此功能讓您回溯特定時間點的星盤

⚡ **請先選擇性別：**"""
    
    send_line_message(user.line_user_id, message, quick_reply_items)
    return None

def handle_time_divination_gender_input(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理指定時間占卜的性別輸入"""
    text = text.strip().upper()
    gender = None
    
    if text in ["男", "M"]:
        gender = "M"
    elif text in ["女", "F"]:
        gender = "F"
    
    if not gender:
        return "❓ 請輸入有效的性別：「男」或「女」。"
        
    session.set_data("gender", gender)
    session.set_state("waiting_for_time_selection")
    
    quick_reply_items = [
        {"type": "action", "action": {"type": "message", "label": "現在", "text": "現在"}},
        {"type": "action", "action": {"type": "message", "label": "1小時前", "text": "1小時前"}},
        {"type": "action", "action": {"type": "message", "label": "昨天此時", "text": "昨天此時"}},
        {"type": "action", "action": {"type": "action", "label": "📅 選擇日期和時間", "data": "select_datetime"}},
        {"type": "action", "action": {"type": "message", "label": "✍️ 手動輸入", "text": "手動輸入"}}
    ]
    
    message = """📅 **請選擇占卜時間：**

您可以選擇快速選項，或手動輸入精確時間。"""
    
    send_line_message(user.line_user_id, message, quick_reply_items)
    return None

def handle_time_selection(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理時間選項"""
    now = get_current_taipei_time()
    target_time = None
    original_input = text
    
    if text == "現在":
        target_time = now
    elif text == "1小時前":
        target_time = now - timedelta(hours=1)
    elif text == "昨天此時":
        target_time = now - timedelta(days=1)
    elif text == "手動輸入":
        session.set_state("waiting_for_manual_time_input")
        return """✍️ **請手動輸入時間**

支持格式：
• `今天 14:30`
• `昨天 09:15`
• `2024-01-15 14:30`
• `1小時前`
• `30分鐘前`

請輸入目標時間："""
    else:
        # 嘗試解析其他格式
        target_time = parse_time_input(text)
        if not target_time:
            return "❓ 無法識別的時間格式，請重新選擇或手動輸入。"
    
    if target_time:
        return execute_time_divination(db, user, session, target_time, original_input)
        
    return None

def handle_custom_time_input(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理手動輸入的時間"""
    target_time = parse_time_input(text)
    if target_time:
        return execute_time_divination(db, user, session, target_time, text)
    else:
        return """❓ 時間格式不正確，請重新輸入：

📝 **支持格式：**
• 今天 14:30
• 昨天 09:15  
• 2024-01-15 14:30
• 1小時前
• 30分鐘前

請重新輸入目標時間："""

def execute_time_divination(db: Optional[Session], user: LineBotUser, session: MemoryUserSession, target_time: datetime, original_input: str) -> str:
    """執行指定時間占卜"""
    gender = session.get_data("gender")
    if not gender:
        session.clear_state()
        return "❌ 找不到性別資訊，請重新開始。"
        
    try:
        result = divination_logic.perform_divination(user, gender, target_time, db)
        
        if result["success"]:
            # 使用 Flex Message 產生器
            message_generator = DivinationFlexMessageGenerator()
            flex_messages = message_generator.generate_divination_messages(result, True) # 管理員模式
            
            # 發送 Flex 訊息
            if flex_messages:
                # 附加一個文字訊息，說明這是哪個時間點的占卜
                time_info_message = f"您查詢的時間點為：\n{original_input}\n({target_time.strftime('%Y-%m-%d %H:%M')})"
                send_line_message(user.line_user_id, time_info_message)
                send_line_flex_messages(user.line_user_id, flex_messages)
            else:
                return "占卜結果生成失敗。"
        else:
            return result.get("error", "占卜失敗。")
            
    except Exception as e:
        logger.error(f"執行指定時間占卜時發生錯誤: {e}", exc_info=True)
        return "執行指定時間占卜時發生未預期的錯誤。"
    finally:
        session.clear_state()
        
    return None

def format_time_divination_result_text(result: Dict, target_time: datetime, is_admin: bool = False) -> str:
    """格式化指定時間占卜結果（備用）"""
    
    header = "🔮 **指定時間占卜結果** ✨\n\n"
    
    # 基本資訊
    gender_text = "男性" if result.get("gender") == "M" else "女性"
    divination_time_text = target_time.strftime("%Y-%m-%d %H:%M:%S")
        
    base_info = (
        f"👤 **性別：** {gender_text}\n"
        f"📅 **占卜時間：** {divination_time_text}\n"
        f"☯️ **太極點命宮：** {result.get('taichi_palace', '未知')}\n"
        f"🕰️ **分鐘地支：** {result.get('minute_dizhi', '未知')}\n"
        f"🌌 **宮干：** {result.get('palace_tiangan', '未知')}\n\n"
    )
    
    # 四化結果
    sihua_header = "🌟 **四化分析** 🌟\n"
    sihua_text = ""
    sihua_results = result.get("sihua_results", [])
    
    if not sihua_results:
        sihua_text = "  (無四化結果)\n"
    else:
        for sihua in sihua_results:
            sihua_text += (
                f"  - **{sihua['type']}** ({sihua['star']}) -> {sihua['palace']}:\n"
                f"    {sihua['explanation']}\n"
            )
            
    full_text = header + base_info + sihua_header + sihua_text
    
    return full_text

@router.post("/webhook")
@limiter.limit("100/minute")  # LINE webhook 速率限制
async def line_webhook(request: Request, background_tasks: BackgroundTasks):
    """處理 LINE Webhook 事件（支持可選數據庫）"""
    try:
        # 安全檢查
        body_bytes = await request.body()
        signature = request.headers.get("X-Line-Signature")
        if not verify_line_signature(body_bytes, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

        body_str = body_bytes.decode("utf-8")
        data = json.loads(body_str)
        
        db = get_optional_db()
        
        for event in data["events"]:
            background_tasks.add_task(handle_line_event, event, db)
            
    except HTTPException as http_exc:
        logger.error(f"HTTP 錯誤: {http_exc.detail}")
        raise http_exc
    except json.JSONDecodeError:
        logger.error(f"無效的 JSON 格式: {body_str}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"處理 Webhook 時發生未預期的錯誤: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if 'db' in locals() and db:
            db.close()
            
    return {"status": "ok"}

async def handle_line_event(event: dict, db: Optional[Session]):
    """非同步處理單個 LINE 事件"""
    event_type = event.get("type")
    
    try:
        if event_type == "message":
            await handle_message_event(event, db)
        elif event_type == "postback":
            await handle_postback_event(event, db)
        elif event_type == "follow":
            handle_follow_event(event, db)
        elif event_type == "unfollow":
            handle_unfollow_event(event, db)
        else:
            logger.info(f"收到未處理的事件類型: {event_type}")
    except Exception as e:
        logger.error(f"處理事件 {event_type} 時發生錯誤: {e}", exc_info=True)

async def handle_postback_event(event: dict, db: Optional[Session]):
    """處理 Postback 事件"""
    user_id = event["source"]["userId"]
    postback_data = event["postback"]["data"]
    logger.info(f"收到來自 {user_id} 的 Postback 事件，資料: {postback_data}")

    try:
        # 獲取或創建用戶
        user = get_or_create_user(db, user_id)
        session = get_or_create_session(user_id)

        # 解析 postback data
        if postback_data == "action=show_control_panel":
            # 顯示 Flex Message 控制面板
            await handle_show_control_panel(user_id, user, db)
            
        elif postback_data == "action=show_member_info":
            # 顯示會員資訊
            await handle_show_member_info(user_id, user, db)
            
        elif postback_data == "action=weekly_fortune":
            # 本週占卜
            await handle_weekly_fortune(user_id, user, session, db)
            
        elif postback_data == "action=show_instructions":
            # 顯示使用說明
            await handle_show_instructions(user_id, user, db)
            
        elif postback_data == "action=show_taichi_palaces":
            # 顯示太極十二宮資訊
            await handle_show_taichi_palaces(user_id, user, db)
            
        # 處理來自控制面板的動作
        elif postback_data.startswith("control_panel="):
            action = postback_data.split("=", 1)[1]
            await handle_control_panel_action(user_id, user, session, action, db)
            
        # 處理管理員面板動作
        elif postback_data.startswith("admin_action="):
            action = postback_data.split("=", 1)[1]
            await handle_admin_panel_action(user_id, user, action, db)
            
        # 處理日期時間選擇器的 postback
        elif postback_data.startswith("datetime_picker="):
            action = postback_data.split("=", 1)[1]
            if action == "time_divination" and "params" in event["postback"]:
                params = event["postback"]["params"]
                if "datetime" in params:
                    logger.info(f"處理日期時間選擇器回調: {params['datetime']}")
                    await handle_datetime_picker_callback(user_id, user, session, params["datetime"], db)
                    return
            
        # 處理時間選擇器的 postback（舊版兼容）
        elif "params" in event["postback"]:
            params = event["postback"]["params"]
            if "datetime" in params:
                logger.info(f"處理 datetime picker 回調: {params['datetime']}")
                await handle_datetime_picker_callback(user_id, user, session, params["datetime"], db)
                return
                
        else:
            logger.warning(f"未知的 postback 資料: {postback_data}")
            
    except Exception as e:
        logger.error(f"處理 Postback 事件失敗: {e}", exc_info=True)
        send_line_message(user_id, "處理請求時發生錯誤，請稍後再試。")

async def handle_message_event(event: dict, db: Optional[Session]):
    """處理 Message 事件"""
    try:
        message_type = event["message"]["type"]
        user_id = event["source"]["userId"]
        
        if message_type == "text":
            text = event["message"].get("text", "").strip()
            
            # 完整模式：使用數據庫和會話管理
            try:
                user = get_or_create_user(db, user_id)
                session = get_or_create_session(user_id)
                
                # 處理不同的指令
                if text in ["會員資訊", "個人資訊", "我的資訊"]:
                    try:
                        # 加強用戶驗證
                        if not user:
                            user = get_or_create_user(db, user_id)
                        
                        # 重新獲取最新的用戶資料
                        db.refresh(user)
                        
                        user_stats = permission_manager.get_user_stats(db, user)
                        response = format_user_info(user_stats)
                        if response:
                            send_line_message(user_id, response)
                        else:
                            send_line_message(user_id, "⚠️ 無法獲取會員資訊，請稍後再試。")
                    except Exception as member_error:
                        logger.error(f"獲取會員資訊失敗 - 用戶: {user_id}, 錯誤: {member_error}")
                        import traceback
                        logger.error(f"詳細錯誤: {traceback.format_exc()}")
                        
                        # 嘗試重新創建用戶
                        try:
                            logger.info(f"嘗試重新創建用戶: {user_id}")
                            user = get_or_create_user(db, user_id)
                            user_stats = permission_manager.get_user_stats(db, user)
                            response = format_user_info(user_stats)
                            send_line_message(user_id, response)
                        except Exception as retry_error:
                            logger.error(f"重試獲取會員資訊也失敗: {retry_error}")
                            # 提供更友善的錯誤訊息
                            send_line_message(user_id, "🔄 系統正在重新初始化您的會員資料\n\n請稍等30秒後重試，或重新加入好友。\n\n如問題持續，請聯繫客服。")
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
                
                # 處理指定時間占卜的性別輸入
                elif session.state == "waiting_for_divination_gender":
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

 **支持格式：**
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
                                send_line_message(user_id, f" {sihua_type}星詳細解釋暫時無法顯示，請稍後再試。")
                                
                        except Exception as e:
                            logger.error(f"獲取四化詳細解釋失敗: {e}")
                            send_line_message(user_id, f"🔮 {sihua_type}星詳細解釋 ✨\n\n⚠️ 系統暫時無法獲取詳細解釋，請稍後再試。\n\n💫 如果問題持續，請聯繫客服。")
                        return  # 重要：防止觸發默認歡迎訊息
                
                # 處理會員升級相關查詢
                elif text in ["如何升級會員", "升級會員", "會員升級", "付費會員", "會員方案"]:
                    upgrade_message = """💎 **會員升級方案** ✨

🌟 **付費會員專享功能：**
• 🔮 四化完整詳細解釋
• 🌍 流年運勢深度分析  
• 🌙 流月運勢變化預測
• 🪐 流日運勢每日指引
• 📊 命盤完整專業解析
• 💡 個人化建議與指引

💰 **優惠方案：**
• 月費方案：NT$ 299/月
• 季度方案：NT$ 799/季（省NT$ 98）
• 年度方案：NT$ 2,999/年（省NT$ 588）

🎁 **限時優惠：**
新用戶首月享 5 折優惠！

💫 升級管道即將開放，請關注最新消息！
如有疑問請聯繫客服。"""
                    send_line_message(user_id, upgrade_message)
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
                    # 默認回覆 - 當沒有匹配到任何特定指令時
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
                logger.error(f"處理用戶請求失敗：{e}", exc_info=True)
                send_line_message(user_id, "系統暫時忙碌，請稍後再試。")
    
    # 這個 except 是用來捕捉 message_type 檢查或 user_id 提取的錯誤
    except Exception as e:
        logger.error(f"處理訊息事件的初始階段出錯: {e}", exc_info=True)


def handle_follow_event(event: dict, db: Optional[Session]):
    """處理關注事件"""
    user_id = event["source"]["userId"]
    logger.info(f"用戶 {user_id} 觸發關注事件...")

    # 歡迎訊息
    welcome_message = """🌟 歡迎加入星空紫微斗數！ ✨

我是您的專屬命理小幫手，運用古老的智慧為您提供現代化的指引。

🔮 **主要功能：**
• **本週占卜** - 根據當下的「觸機」，為您占卜本週的關鍵運勢。
• **會員資訊** - 查看您的個人資訊和使用記錄。
• **命盤綁定** - (即將推出) 綁定您的生辰，獲得更個人化的分析。

👇 **開始您的探索之旅**
請點擊下方的「**基本功能**」中的「**本週占卜**」，體驗觸機占卜的奧妙！

⭐ 願紫微斗數為您照亮前行的道路！"""
    
    send_line_message(user_id, welcome_message)
    
    # 為用戶設定全新的預設選單
    try:
        # TODO: 實作設定單一、固定的 Rich Menu 的邏輯
        # success = rich_menu_manager.set_default_rich_menu(user_id)
        logger.info(f"✅ (未來將在此處) 成功為用戶 {user_id} 設定全新的預設 Rich Menu。")
        # if not success:
        #     logger.error(f"❌ 為用戶 {user_id} 設定預設 Rich Menu 失敗。")
        
    except Exception as e:
        logger.error(f"關注事件中設定Rich Menu失敗: {e}", exc_info=True)

def handle_unfollow_event(event: dict, db: Optional[Session]):
    """處理取消關注事件"""
    user_id = event["source"]["userId"]
    logger.info(f"用戶 {user_id} 已取消關注")
    
    if db:
        try:
            user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
            if user:
                user.is_active = False
                db.commit()
                logger.info(f"用戶 {user_id} 在數據庫中已標記為非活躍")
        except Exception as e:
            logger.error(f"更新用戶取消關注狀態失敗: {e}")
            db.rollback()

def format_user_info(user_stats: Dict) -> str:
    """格式化會員資訊"""
    
    user_info = user_stats.get("user_info", {})
    membership_info = user_stats.get("membership_info", {})
    divination_stats = user_stats.get("divination_stats", {})
    
    # 基本資料
    user_id_masked = user_info.get("line_user_id", "未知ID")[:8] + "..."
    status = "活躍" if user_info.get("is_active") else "非活躍"
    
    # 會員等級
    membership_level = "尊貴會員" if membership_info.get("is_premium") else "免費會員"
    if user_info.get("is_admin"):
        membership_level = "👑 管理員"
        
    # 會員到期日
    expiry_date = membership_info.get("expires_at")
    if expiry_date:
        try:
            expiry_date_str = datetime.fromisoformat(expiry_date).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            expiry_date_str = "永久"
    else:
        expiry_date_str = "永久" if membership_info.get("is_premium") else "N/A"
        
    # 占卜統計
    total_divinations = divination_stats.get("total_divinations", 0)
    last_divination_time = divination_stats.get("last_divination_time")
    if last_divination_time:
        try:
            last_divination_time_str = datetime.fromisoformat(last_divination_time).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            last_divination_time_str = "無記錄"
    else:
        last_divination_time_str = "無記錄"
        
    message = (
        f"👤 **會員資訊**\n\n"
        f"**用戶ID:** {user_id_masked}\n"
        f"**狀態:** {status}\n\n"
        f"💎 **會員等級:** {membership_level}\n"
        f"**到期日:** {expiry_date_str}\n\n"
        f"🔮 **占卜統計:**\n"
        f"**總次數:** {total_divinations} 次\n"
        f"**上次占卜:** {last_divination_time_str}"
    )
    
    return message

def get_or_create_user(db: Session, user_id: str) -> LineBotUser:
    """獲取或創建用戶（數據庫模式）"""
    if not db:
        # 簡化模式下，返回一個臨時的 LineBotUser 對象
        return LineBotUser(line_user_id=user_id, is_active=True)
        
    try:
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
        if user:
            # 如果用戶存在但被標記為非活躍，重新激活
            if not user.is_active:
                user.is_active = True
                db.commit()
                db.refresh(user)
                logger.info(f"重新激活用戶: {user_id}")
            return user
        
        # 如果用戶不存在，創建新用戶
        logger.info(f"創建新用戶: {user_id}")
        new_user = LineBotUser(line_user_id=user_id, is_active=True)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except Exception as e:
        logger.error(f"獲取或創建用戶失敗: {e}")
        db.rollback()
        # 發生錯誤時，返回一個臨時用戶對象以避免崩潰
        return LineBotUser(line_user_id=user_id, is_active=True)

def clear_user_session(db: Session, user_id: str):
    """清除用戶會話狀態（數據庫模式）"""
    if user_id in user_sessions:
        del user_sessions[user_id]
        logger.info(f"已清除用戶 {user_id} 的記憶體會話")

def verify_line_signature(body: bytes, signature: str) -> bool:
    """驗證 LINE 簽名"""
    try:
        from app.config.linebot_config import LineBotConfig
        import hmac
        import hashlib
        import base64

        if not LineBotConfig.CHANNEL_SECRET:
            logger.warning("未設定 CHANNEL_SECRET，跳過簽名驗證")
            return True

        hash_obj = hmac.new(
            LineBotConfig.CHANNEL_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
        
        expected_signature = base64.b64encode(hash_obj).decode('utf-8')
        
        return hmac.compare_digest(expected_signature, signature)

    except Exception as e:
        logger.error(f"驗證簽名時發生錯誤: {e}")
        return False

# === 究極混搭方案：Postback 處理函數 ===

async def handle_show_control_panel(user_id: str, user: LineBotUser, db: Optional[Session]):
    """顯示 Flex Message 控制面板"""
    try:
        from app.utils.flex_control_panel import FlexControlPanelGenerator
        
        # 獲取用戶權限資訊
        user_stats = permission_manager.get_user_stats(db, user) if db else {
            "user_info": {"is_admin": False},
            "membership_info": {"is_premium": False}
        }
        
        # 生成控制面板
        panel_generator = FlexControlPanelGenerator()
        control_panel = panel_generator.generate_control_panel(user_stats)
        
        if control_panel:
            send_line_flex_messages(user_id, [control_panel])
        else:
            send_line_message(user_id, "無法載入功能選單，請稍後再試。")
            
    except Exception as e:
        logger.error(f"顯示控制面板失敗: {e}", exc_info=True)
        send_line_message(user_id, "載入功能選單時發生錯誤，請稍後再試。")

async def handle_show_member_info(user_id: str, user: LineBotUser, db: Optional[Session]):
    """顯示會員資訊"""
    try:
        if not db:
            send_line_message(user_id, "會員資訊功能暫時無法使用，請稍後再試。")
            return
            
        # 獲取用戶統計資訊
        user_stats = permission_manager.get_user_stats(db, user)
        response = format_user_info(user_stats)
        
        if response:
            send_line_message(user_id, response)
        else:
            send_line_message(user_id, "⚠️ 無法獲取會員資訊，請稍後再試。")
            
    except Exception as e:
        logger.error(f"顯示會員資訊失敗: {e}", exc_info=True)
        send_line_message(user_id, "獲取會員資訊時發生錯誤，請稍後再試。")

async def handle_weekly_fortune(user_id: str, user: LineBotUser, session: MemoryUserSession, db: Optional[Session]):
    """處理本週占卜"""
    try:
        response = handle_divination_request(db, user, session)
        if response:
            send_line_message(user_id, response)
            
    except Exception as e:
        logger.error(f"本週占卜失敗: {e}", exc_info=True)
        send_line_message(user_id, "占卜服務暫時無法使用，請稍後再試。")

async def handle_show_instructions(user_id: str, user: LineBotUser, db: Optional[Session]):
    """顯示使用說明"""
    try:
        from app.utils.flex_instructions import FlexInstructionsGenerator
        
        # 獲取用戶權限資訊
        user_stats = permission_manager.get_user_stats(db, user) if db else {
            "user_info": {"is_admin": False},
            "membership_info": {"is_premium": False}
        }
        
        # 生成使用說明
        instructions_generator = FlexInstructionsGenerator()
        instructions_message = instructions_generator.generate_instructions(user_stats)
        
        if instructions_message:
            send_line_flex_messages(user_id, [instructions_message])
        else:
            # 備用文字說明
            instructions_text = """📖 **使用說明** ✨

🔮 **主要功能：**
• **本週占卜** - 根據當下時間進行觸機占卜
• **會員資訊** - 查看個人使用記錄和權限
• **功能選單** - 智能控制面板，根據權限顯示功能

💫 **操作方式：**
1. 點擊下方選單按鈕快速進入功能
2. 或直接輸入文字指令
3. 依照系統提示完成操作

🌟 **貼心提醒：**
• 每週只能占卜一次，請珍惜機會
• 升級會員可享受更多功能
• 有問題可隨時聯繫客服

⭐ 願紫微斗數為您指引人生方向！"""
            send_line_message(user_id, instructions_text)
            
    except Exception as e:
        logger.error(f"顯示使用說明失敗: {e}", exc_info=True)
        instructions_text = """📖 **使用說明** ✨

🔮 **主要功能：**
• **本週占卜** - 根據當下時間進行觸機占卜
• **會員資訊** - 查看個人使用記錄
• **功能選單** - 更多功能選項

💫 如需詳細說明，請稍後再試或聯繫客服。"""
        send_line_message(user_id, instructions_text)

async def handle_control_panel_action(user_id: str, user: LineBotUser, session: MemoryUserSession, action: str, db: Optional[Session]):
    """處理控制面板的動作"""
    try:
        logger.info(f"處理控制面板動作: {action}")
        
        if action == "basic_divination":
            # 基本占卜功能
            await handle_weekly_fortune(user_id, user, session, db)
            
        elif action == "yearly_fortune":
            # 流年運勢
            await handle_yearly_fortune(user_id, user, db)
            
        elif action == "monthly_fortune":
            # 流月運勢  
            await handle_monthly_fortune(user_id, user, db)
            
        elif action == "daily_fortune":
            # 流日運勢
            await handle_daily_fortune(user_id, user, db)
            
        elif action == "chart_analysis":
            # 命盤分析（未來功能）
            send_line_message(user_id, """🌟 命盤分析功能

✨ 此功能正在開發中，敬請期待！

🔮 **即將推出：**
• 完整紫微斗數命盤解析
• 十二宮位詳細分析
• 個人特質深度解讀
• 生涯發展建議

💫 感謝您的耐心等待！""")
            
        elif action == "member_upgrade":
            # 會員升級（未來功能）
            send_line_message(user_id, """💎 會員升級功能

✨ 升級管道即將開放！

🌟 **付費會員專享：**
• 流年、流月、流日運勢
• 四化詳細解釋
• 命盤完整分析
• 專業諮詢服務

💫 請關注最新消息！""")
            
        elif action == "admin_functions":
            # 管理員功能
            await handle_admin_functions(user_id, user, db)
            
        else:
            logger.warning(f"未知的控制面板動作: {action}")
            send_line_message(user_id, "此功能暫時無法使用，請稍後再試。")
            
    except Exception as e:
        logger.error(f"處理控制面板動作失敗: {e}", exc_info=True)
        send_line_message(user_id, "處理請求時發生錯誤，請稍後再試。")

async def handle_yearly_fortune(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理流年運勢請求"""
    try:
        if not db:
            send_line_message(user_id, "流年運勢功能暫時無法使用，請稍後再試。")
            return
            
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
            
    except Exception as e:
        logger.error(f"處理流年運勢失敗: {e}", exc_info=True)
        send_line_message(user_id, "流年運勢服務暫時無法使用，請稍後再試。")

async def handle_monthly_fortune(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理流月運勢請求"""
    try:
        if not db:
            send_line_message(user_id, "流月運勢功能暫時無法使用，請稍後再試。")
            return
            
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
            
    except Exception as e:
        logger.error(f"處理流月運勢失敗: {e}", exc_info=True)
        send_line_message(user_id, "流月運勢服務暫時無法使用，請稍後再試。")

async def handle_daily_fortune(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理流日運勢請求"""
    try:
        if not db:
            send_line_message(user_id, "流日運勢功能暫時無法使用，請稍後再試。")
            return
            
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
            
    except Exception as e:
        logger.error(f"處理流日運勢失敗: {e}", exc_info=True)
        send_line_message(user_id, "流日運勢服務暫時無法使用，請稍後再試。")

async def handle_admin_functions(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理管理員功能"""
    try:
        if not db:
            send_line_message(user_id, "管理員功能暫時無法使用，請稍後再試。")
            return
            
        user_stats = permission_manager.get_user_stats(db, user)
        is_admin = user_stats["user_info"]["is_admin"]
        
        if not is_admin:
            send_line_message(user_id, "⚠️ 您沒有管理員權限。")
            return
            
        # 生成管理員功能選單
        from app.utils.flex_admin_panel import FlexAdminPanelGenerator
        
        admin_generator = FlexAdminPanelGenerator()
        admin_panel = admin_generator.generate_admin_panel()
        
        if admin_panel:
            send_line_flex_messages(user_id, [admin_panel])
        else:
            # 備用文字選單
            admin_text = """👑 **管理員功能面板** ✨

🔧 **系統管理：**
• 指定時間占卜 - 輸入「時間占卜」
• 用戶數據統計 - 輸入「用戶統計」
• 系統狀態監控 - 輸入「系統狀態」

📊 **數據管理：**
• 占卜記錄查詢 - 輸入「占卜記錄」
• 用戶權限管理 - 輸入「權限管理」

⚙️ **選單管理：**
• 更新選單 - 輸入「更新選單」
• 創建選單 - 輸入「創建選單」

💫 請輸入對應指令或使用控制面板操作。"""
            send_line_message(user_id, admin_text)
            
    except Exception as e:
        logger.error(f"處理管理員功能失敗: {e}", exc_info=True)
        send_line_message(user_id, "管理員功能暫時無法使用，請稍後再試。")

async def handle_datetime_picker_callback(user_id: str, user: LineBotUser, session: MemoryUserSession, datetime_str: str, db: Optional[Session]):
    """處理來自日期時間選擇器的回調"""
    try:
        logger.info(f"處理日期時間選擇器回調: {datetime_str}")
        
        # 檢查是否為指定時間占卜的回調
        data = session.get_data("callback_type")
        if data != "time_divination":
            # 設置為指定時間占卜模式
            session.set_data("callback_type", "time_divination")
        
        # 解析時間字符串 - 改進时区处理
        try:
            # LINE 的 datetime picker 返回的格式通常是 "YYYY-MM-DDTHH:MM" 
            # 可能没有时区信息，假设用户选择的是台北当地时间
            if 'T' in datetime_str and '+' not in datetime_str and 'Z' not in datetime_str:
                # 没有时区信息，假设是台北时间
                target_time = datetime.fromisoformat(datetime_str)
                target_time = target_time.replace(tzinfo=TAIPEI_TZ)
                logger.info(f"解析为台北时间（无时区信息）: {target_time}")
            else:
                # 有时区信息的情况
                if datetime_str.endswith('Z'):
                    target_time = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                else:
                    target_time = datetime.fromisoformat(datetime_str)
                
                # 如果时区为None，设为UTC然后转为台北时间
                if target_time.tzinfo is None:
                    target_time = target_time.replace(tzinfo=timezone.utc)
                
                # 转换为台北时间
                target_time = target_time.astimezone(TAIPEI_TZ)
                logger.info(f"转换后的台北时间: {target_time}")
        except Exception as parse_error:
            logger.error(f"时间解析失败: {parse_error}")
            send_line_message(user_id, "時間格式解析失敗，請重新選擇時間。")
            return
        
        # 要求選擇性別
        session.set_state("waiting_for_divination_gender")
        session.set_data("target_time", target_time.isoformat())
        session.set_data("original_input", datetime_str)
        
        # 發送性別選擇訊息
        quick_reply_items = [
            {"type": "action", "action": {"type": "message", "label": "👨 男性", "text": "男"}},
            {"type": "action", "action": {"type": "message", "label": "👩 女性", "text": "女"}}
        ]
        
        time_str = target_time.strftime("%Y年%m月%d日 %H:%M")
        message = f"""⏰ **指定時間占卜** ✨

🎯 **選定時間：** {time_str} (台北時間)

請選擇進行占卜的性別："""
        
        send_line_message(user_id, message, quick_reply_items)
            
    except Exception as e:
        logger.error(f"處理日期時間選擇器回調失敗: {e}", exc_info=True)
        send_line_message(user_id, "處理時間選擇失敗，請重新嘗試。")

async def handle_admin_panel_action(user_id: str, user: LineBotUser, action: str, db: Optional[Session]):
    """處理管理員面板動作"""
    try:
        # 驗證管理員權限
        if not db:
            send_line_message(user_id, "管理員功能暫時無法使用，請稍後再試。")
            return
            
        user_stats = permission_manager.get_user_stats(db, user)
        is_admin = user_stats["user_info"]["is_admin"]
        
        if not is_admin:
            send_line_message(user_id, "⚠️ 您沒有管理員權限。")
            return
        
        logger.info(f"處理管理員面板動作: {action}")
        
        if action == "time_divination_start":
            # 使用 datetime picker 開始指定時間占卜
            await handle_time_divination_with_picker(user_id, user, db)
            
        elif action == "time_divination":
            # 舊版處理方式 - 文字輸入
            send_line_message(user_id, """⏰ **指定時間占卜** 

此功能允許您回溯特定時間點的運勢分析。

💫 **使用方式：**
請直接輸入「指定時間占卜」或「時間占卜」開始使用。

⚡ 這是管理員專屬功能，可用於：
• 回溯歷史重要時刻的運勢
• 驗證占卜系統的準確性
• 研究特定時間點的四化影響""")
            
        elif action == "user_stats":
            # 用戶數據統計
            await handle_user_statistics(user_id, user, db)
            
        elif action == "system_status":
            # 系統狀態監控
            await handle_system_status(user_id, user, db)
            
        elif action == "menu_management":
            # 選單管理
            await handle_menu_management(user_id, user, db)
            
        else:
            logger.warning(f"未知的管理員面板動作: {action}")
            send_line_message(user_id, "此功能暫時無法使用，請稍後再試。")
            
    except Exception as e:
        logger.error(f"處理管理員面板動作失敗: {e}", exc_info=True)
        send_line_message(user_id, "管理員功能暫時無法使用，請稍後再試。")

async def handle_time_divination_with_picker(user_id: str, user: LineBotUser, db: Optional[Session]):
    """使用 DateTime Picker 處理指定時間占卜"""
    try:
        # 創建 DateTime Picker 的 Flex Message
        datetime_picker_message = create_datetime_picker_message()
        
        if datetime_picker_message:
            send_line_flex_messages(user_id, [datetime_picker_message])
        else:
            # 備用方案：使用文字說明
            send_line_message(user_id, """⏰ **指定時間占卜** 

🎯 **快速選擇：**
• 現在：查看當前時刻運勢
• 今天：選擇今天的特定時間
• 昨天：查看昨天的運勢
• 本週：選擇本週任一時間
• 自訂：手動輸入特定日期時間

💫 請選擇您想要查詢的時間點，或直接輸入時間格式：
例如：「今天 14:30」、「昨天 09:00」、「2024-01-15 18:30」""")
            
    except Exception as e:
        logger.error(f"創建時間選擇器失敗: {e}", exc_info=True)
        send_line_message(user_id, "時間選擇功能暫時無法使用，請輸入「指定時間占卜」使用文字版本。")

def create_datetime_picker_message() -> Optional[FlexMessage]:
    """創建包含 DateTime Picker 的 Flex Message"""
    try:
        from linebot.v3.messaging import DatetimePickerAction
        from datetime import datetime, timedelta
        
        # 計算預設時間範圍 - 使用台北時間
        now = get_current_taipei_time()  # 使用台北時間而不是本地時間
        min_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")  # 30天前
        max_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")   # 7天後
        initial_datetime = now.strftime("%Y-%m-%dT%H:%M")
        
        bubble = FlexBubble(
            size="kilo",
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 標題
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text="⏰",
                                size="xxl",
                                flex=0
                            ),
                            FlexText(
                                text="指定時間占卜",
                                weight="bold",
                                size="xl",
                                color="#2E86AB",
                                flex=1,
                                margin="md"
                            )
                        ],
                        backgroundColor="#F8F9FA",
                        cornerRadius="md",
                        paddingAll="lg"
                    ),
                    FlexSeparator(margin="lg"),
                    
                    # 說明文字
                    FlexText(
                        text="選擇您想要查詢的日期和時間",
                        size="md",
                        color="#666666",
                        wrap=True,
                        margin="lg"
                    ),
                    FlexText(
                        text=f"💫 可查詢範圍：過去30天至未來7天\n🕰️ 當前台北時間：{now.strftime('%Y-%m-%d %H:%M')}",
                        size="sm",
                        color="#999999",
                        wrap=True,
                        margin="md"
                    ),
                    
                    # DateTime Picker 按鈕
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexBox(
                                layout="horizontal",
                                contents=[
                                    FlexText(
                                        text="📅 選擇日期時間",
                                        size="lg",
                                        color="#FFFFFF",
                                        weight="bold",
                                        align="center",
                                        flex=1
                                    )
                                ],
                                backgroundColor="#2E86AB",
                                cornerRadius="md",
                                paddingAll="lg",
                                margin="lg",
                                action=DatetimePickerAction(
                                    data="datetime_picker=time_divination",
                                    mode="datetime",
                                    initial=initial_datetime,
                                    max=max_date + "T23:59",
                                    min=min_date + "T00:00"
                                )
                            )
                        ]
                    ),
                    
                    # 底部說明
                    FlexSeparator(margin="lg"),
                    FlexText(
                        text="⚡ 這是管理員專屬功能 | 🌏 使用台北時區 (UTC+8)",
                        size="sm",
                        color="#999999",
                        align="center",
                        margin="md"
                    )
                ],
                spacing="none",
                paddingAll="xl"
            ),
            styles={
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        )
        
        return FlexMessage(
            alt_text="⏰ 指定時間占卜 - 選擇日期時間",
            contents=bubble
        )
        
    except Exception as e:
        logger.error(f"創建日期時間選擇器失敗: {e}")
        return None

async def handle_user_statistics(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理用戶數據統計"""
    try:
        from app.models.linebot_models import LineBotUser, DivinationHistory
        from sqlalchemy import func
        
        # 統計用戶數據
        total_users = db.query(LineBotUser).count()
        total_divinations = db.query(DivinationHistory).count()
        admin_users = db.query(LineBotUser).filter(LineBotUser.is_admin == True).count()
        
        # 本週新增用戶
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        new_users_this_week = db.query(LineBotUser).filter(
            LineBotUser.created_at >= week_ago
        ).count()
        
        # 本週占卜次數
        divinations_this_week = db.query(DivinationHistory).filter(
            DivinationHistory.divination_time >= week_ago
        ).count()
        
        stats_message = f"""📊 **用戶數據統計** 

👥 **用戶統計：**
• 總用戶數：{total_users} 人
• 管理員數：{admin_users} 人
• 本週新增：{new_users_this_week} 人

🔮 **占卜統計：**
• 總占卜次數：{total_divinations} 次
• 本週占卜：{divinations_this_week} 次
• 平均每用戶：{total_divinations/total_users:.1f} 次（如果有用戶）

📈 **系統概況：**
• 資料更新時間：{datetime.now().strftime("%Y-%m-%d %H:%M")}
• 系統運行正常 ✅"""
        
        send_line_message(user_id, stats_message)
        
    except Exception as e:
        logger.error(f"獲取用戶統計失敗: {e}")
        send_line_message(user_id, "📊 獲取統計數據時發生錯誤，請稍後再試。")

async def handle_system_status(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理系統狀態監控"""
    try:
        import psutil
        import os
        
        # 系統資源使用情況
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_message = f"""🖥️ **系統狀態監控**

⚡ **CPU 使用率：**
• 當前：{cpu_percent}%
• 狀態：{'正常' if cpu_percent < 80 else '偏高'}

💾 **記憶體使用：**
• 已使用：{memory.percent}%
• 可用：{memory.available // (1024**3)} GB
• 狀態：{'正常' if memory.percent < 80 else '偏高'}

💿 **磁碟使用：**
• 已使用：{disk.percent}%
• 可用：{disk.free // (1024**3)} GB
• 狀態：{'正常' if disk.percent < 85 else '偏高'}

🔍 **應用狀態：**
• LINE Bot 服務：運行中 ✅
• 資料庫連接：正常 ✅
• 更新時間：{datetime.now().strftime("%Y-%m-%d %H:%M")}"""
        
        send_line_message(user_id, status_message)
        
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        send_line_message(user_id, "🖥️ 獲取系統狀態時發生錯誤，可能是權限不足。")

async def handle_menu_management(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理選單管理"""
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

async def handle_show_taichi_palaces(user_id: str, user: LineBotUser, db: Optional[Session]):
    """處理太極十二宮查看請求"""
    try:
        # 檢查權限
        if not db:
            send_line_message(user_id, "太極十二宮功能暫時無法使用，請稍後再試。")
            return
            
        user_stats = permission_manager.get_user_stats(db, user)
        is_admin = user_stats["user_info"]["is_admin"]
        
        if not is_admin:
            send_line_message(user_id, "🔒 太極十二宮資訊僅限管理員查看。")
            return
            
        # 獲取最近的占卜結果
        from app.models.linebot_models import DivinationHistory
        recent_divination = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id
        ).order_by(DivinationHistory.divination_time.desc()).first()
        
        if not recent_divination:
            send_line_message(user_id, "🔮 請先進行占卜，才能查看太極十二宮資訊。\n\n💫 點擊「本週占卜」開始您的占卜之旅。")
            return
            
        # 重新生成占卜結果以獲取太極十二宮資訊
        try:
            import json
            from app.logic.divination_logic import divination_logic
            from app.utils.divination_flex_message import DivinationFlexMessageGenerator
            
            # 重新執行占卜邏輯以獲取完整資訊
            target_time = recent_divination.divination_time
            result = divination_logic.perform_divination(user, recent_divination.gender, target_time, db)
            
            if result["success"]:
                # 生成太極十二宮 Carousel
                message_generator = DivinationFlexMessageGenerator()
                taichi_message = message_generator._create_taichi_palace_carousel(result)
                
                if taichi_message:
                    # 發送說明文字
                    explanation_text = f"""🏛️ **太極十二宮結構** ✨

📅 占卜時間：{target_time.strftime('%Y年%m月%d日 %H:%M')}
🎯 太極點命宮：{result.get('taichi_palace', '未知')}

💫 **太極十二宮說明：**
以太極點命宮為新的命宮，重新分佈十二宮位，展現另一層面的命運結構。每個宮位保持原有星曜配置，但具有新的宮位意義。

👆 請左右滑動查看各宮位詳細資訊："""
                    
                    send_line_message(user_id, explanation_text)
                    send_line_flex_messages(user_id, [taichi_message])
                else:
                    send_line_message(user_id, "❌ 太極十二宮資訊生成失敗，請稍後再試。")
            else:
                send_line_message(user_id, "❌ 無法重新獲取占卜資訊，請重新進行占卜。")
                
        except Exception as detail_error:
            logger.error(f"重新生成太極十二宮資訊失敗: {detail_error}")
            send_line_message(user_id, "❌ 處理太極十二宮資訊時發生錯誤，請重新進行占卜。")
            
    except Exception as e:
        logger.error(f"顯示太極十二宮失敗: {e}", exc_info=True)
        send_line_message(user_id, "太極十二宮功能暫時無法使用，請稍後再試。")

@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}

# 導出路由器
__all__ = ["router"] 