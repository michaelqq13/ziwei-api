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
from app.utils.driver_view_rich_menu_handler import driver_view_handler
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
        result = divination_logic.perform_divination(user, gender, current_time, db)
        
        if result["success"]:
            # 獲取用戶權限等級
            is_admin = False
            if db:
                user_stats = permission_manager.get_user_stats(db, user)
                is_admin = user_stats["user_info"]["is_admin"]

            # 使用 Flex Message產生器
            message_generator = DivinationFlexMessageGenerator()
            flex_messages = message_generator.generate_divination_messages(result, is_admin)
            
            # 發送 Flex 訊息
            if flex_messages:
                send_line_flex_messages(user.line_user_id, flex_messages)
            else:
                return "占卜結果生成失敗，請稍後再試。"
        else:
            return result.get("error", "占卜失敗，請稍後再試。")
            
    except Exception as e:
        logger.error(f"執行占卜時發生錯誤: {e}", exc_info=True)
        return "執行占卜時發生未預期的錯誤，請聯繫管理員。"
    finally:
        session.clear()
        
    return None # 表示已經發送了 Flex 訊息

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

    # 優先處理駕駛視窗的分頁切換
    if postback_data.startswith("tab_"):
        logger.info(f"偵測到駕駛視窗分頁切換: {postback_data}")
        success = driver_view_handler.handle_postback_event(user_id, postback_data)
        if success:
            logger.info(f"成功處理分頁切換 for {user_id}")
        else:
            logger.error(f"處理分頁切換失敗 for {user_id}")
        return # 處理完畢，直接返回

    # (可選) 在這裡保留或添加其他 postback 邏輯
    # 例如：處理時間選擇器的 postback
    if "params" in event["postback"]:
        params = event["postback"]["params"]
        if "datetime" in params:
            # 這是來自 datetime picker 的回調
            logger.info(f"處理 datetime picker 回調: {params['datetime']}")
            # 在這裡添加處理 datetime picker 的邏輯
            # ...
            return

    logger.warning(f"收到未知的 Postback 資料格式: {postback_data}")

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
                logger.error(f"處理用戶請求失敗：{e}", exc_info=True)
                send_line_message(user_id, "系統暫時忙碌，請稍後再試。")
    
    # 這個 except 是用來捕捉 message_type 檢查或 user_id 提取的錯誤
    except Exception as e:
        logger.error(f"處理訊息事件的初始階段出錯: {e}", exc_info=True)


def handle_follow_event(event: dict, db: Optional[Session]):
    """處理關注事件"""
    user_id = event["source"]["userId"]
    logger.info(f"用戶 {user_id} 觸發關注事件，將強制刷新 Rich Menu...")

    # 強制清理所有舊的 DriverView 選單
    try:
        cleaned_count = driver_view_handler.cleanup_old_driver_menus()
        logger.info(f"強制清理了 {cleaned_count} 個舊的 DriverView 選單。")
    except Exception as e:
        logger.error(f"清理舊選單時發生錯誤: {e}", exc_info=True)

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
        # 使用 setup_default_tab 並設定 force_refresh=True
        success = driver_view_handler.setup_default_tab(user_id, tab_name="basic", force_refresh=True)
        if success:
            logger.info(f"✅ 成功為用戶 {user_id} 強制設定了全新的預設 Rich Menu。")
        else:
            logger.error(f"❌ 為用戶 {user_id} 強制設定預設 Rich Menu 失敗。")
        
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

@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}

# 導出路由器
__all__ = ["router"] 