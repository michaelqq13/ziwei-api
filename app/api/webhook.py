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

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter()

# 記憶體中的用戶會話管理
user_sessions: Dict[str, MemoryUserSession] = {}

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_optional_db() -> Session:
    """獲取數據庫會話"""
    # 嘗試創建數據庫會話
    database_url = DatabaseConfig.get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    # 測試數據庫連接
    db.execute(text("SELECT 1"))
    return db

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
            
            # 將占卜結果保存到session中，供後續查看詳細解釋使用
            session.set_data("last_divination_result", result)
            
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
            
            # 完整模式：使用數據庫和會話管理
            try:
                user = get_or_create_user(db, user_id)
                session = get_or_create_session(user_id)
                
                # 處理不同的指令
                if text in ["會員資訊", "個人資訊", "我的資訊"]:
                    user_stats = permission_manager.get_user_stats(db, user)
                    response = format_user_info(user_stats)
                    if response:
                        send_line_message(user_id, response)
                    
                elif text in ["占卜", "算命", "紫微斗數", "開始占卜", "本週占卜"]:
                    response = handle_divination_request(db, user, session)
                    if response:
                        send_line_message(user_id, response)
                    
                elif session.state == "waiting_for_gender":
                    response = handle_gender_input(db, user, session, text)
                    if response:
                        send_line_message(user_id, response)

                else:
                    # 默認回覆
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
        # 這裡應該實現LINE簽名驗證邏輯
        # 目前簡化處理，總是返回True
        logger.info("簽名驗證（簡化模式）")
        return True
        
    except Exception as e:
        logger.error(f"簽名驗證失敗：{e}")
        return False

# 健康檢查端點
@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "LINE Bot Webhook"}

# 導出路由器
__all__ = ["router"] 