"""
LINE Bot Webhook 處理器
處理來自 LINE Platform 的 Webhook 事件
"""
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.config.linebot_config import LineBotConfig, validate_config
from app.models.linebot_models import LineBotUser, DivinationHistory, ChartBinding, MemoryUserSession
from app.logic.permission_manager import permission_manager, get_user_with_permissions
from app.logic.divination_logic import divination_logic
from app.utils.rich_menu_manager import rich_menu_manager

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter()

# 記憶體中的用戶會話管理
user_sessions: Dict[str, MemoryUserSession] = {}

def get_or_create_session(user_id: str) -> MemoryUserSession:
    """獲取或創建用戶會話"""
    if user_id not in user_sessions:
        user_sessions[user_id] = MemoryUserSession(user_id)
    return user_sessions[user_id]

def send_line_message(user_id: str, message: str, quick_reply_items: List = None) -> bool:
    """
    發送 LINE 訊息給用戶
    
    Args:
        user_id: 用戶ID
        message: 訊息內容
        quick_reply_items: Quick Reply按鈕列表
    """
    import requests
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LineBotConfig.CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    message_object = {
        "type": "text",
        "text": message
    }
    
    # 如果有Quick Reply按鈕，添加到訊息中
    if quick_reply_items:
        message_object["quickReply"] = {
            "items": quick_reply_items
        }
    
    data = {
        "to": user_id,
        "messages": [message_object]
    }
    
    try:
        logger.info("=== 開始發送 LINE 訊息 ===")
        logger.info(f"目標用戶ID: {user_id}")
        logger.info(f"訊息內容: {message}")
        logger.info(f"請求URL: {url}")
        logger.info(f"請求標頭: {headers}")
        logger.info(f"請求數據: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data)
        
        logger.info("=== LINE API 回應 ===")
        logger.info(f"回應狀態碼: {response.status_code}")
        logger.info(f"回應內容: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ 訊息發送成功")
            return True
        else:
            logger.error(f"❌ 訊息發送失敗 (HTTP {response.status_code})")
            logger.error(f"錯誤詳情: {response.text}")
            return False
            
    except Exception as e:
        logger.error("=== 發送訊息時發生異常 ===")
        logger.error(f"異常類型: {type(e).__name__}")
        logger.error(f"異常訊息: {str(e)}")
        logger.error(f"堆疊追蹤:\n{traceback.format_exc()}")
        return False

def format_divination_result(result: Dict) -> str:
    """格式化占卜結果為用戶友好的訊息"""
    if not result.get("success"):
        return "🔮 占卜過程發生錯誤，請稍後再試。"
    
    # 基本資訊
    gender_text = "男性" if result["gender"] == "M" else "女性"
    time_str = datetime.fromisoformat(result["divination_time"]).strftime("%Y-%m-%d %H:%M")
    
    message = f"""🔮 **紫微斗數占卜結果** ✨

📅 占卜時間：{time_str}
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

def handle_divination_request(db: Session, user: LineBotUser, session: MemoryUserSession) -> str:
    """處理占卜請求"""
    # 檢查權限
    permission = permission_manager.check_divination_permission(db, user)
    if not permission["allowed"]:
        return permission_manager.format_permission_message(permission, "占卜")
    
    # 如果用戶還沒有提供性別，請求性別資訊
    if session.state != "waiting_for_gender":
        session.set_state("waiting_for_gender")
        
        # 創建性別選擇按鈕
        quick_reply_items = [
            {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": "👨 男性",
                    "text": "男"
                },
                "imageUrl": "https://cdn-icons-png.flaticon.com/128/4080/4080288.png"
            },
            {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": "👩 女性",
                    "text": "女"
                },
                "imageUrl": "https://cdn-icons-png.flaticon.com/128/4080/4080292.png"
            }
        ]
        
        message = """🔮 **開始占卜** ✨

請選擇您的性別：
• 點擊下方按鈕選擇性別
• 這將用於計算您的專屬命盤"""
        
        # 發送帶有Quick Reply按鈕的訊息
        send_line_message(user.line_user_id, message, quick_reply_items)
        return None  # 返回None因為訊息已經直接發送

    return "❓ 占卜流程發生錯誤，請重新開始。"

def handle_gender_input(db: Session, user: LineBotUser, session: MemoryUserSession, text: str) -> str:
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
        current_time = datetime.now()
        result = divination_logic.perform_divination(gender, current_time, db)
        
        if result["success"]:
            # 保存占卜記錄
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
            
            # 清除會話狀態
            session.clear()
            
            # 格式化並返回結果
            return format_divination_result(result)
        else:
            session.clear()
            return "🔮 占卜過程發生錯誤，請稍後再試。"
            
    except Exception as e:
        logger.error(f"占卜過程錯誤: {e}")
        session.clear()
        return "🔮 占卜系統暫時無法使用，請稍後再試。"

def handle_chart_binding(db: Session, user: LineBotUser, session: MemoryUserSession) -> str:
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

def handle_chart_binding_process(db: Session, user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理命盤綁定過程"""
    text = text.strip()
    
    if session.state == "chart_binding_year":
        try:
            year = int(text)
            if year < 1900 or year > datetime.now().year:
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

def handle_fortune_request(db: Session, user: LineBotUser, fortune_type: str) -> str:
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

def handle_admin_authentication(db: Session, user: LineBotUser, session: MemoryUserSession, text: str) -> str:
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

def handle_nickname_setting(db: Session, user: LineBotUser, session: MemoryUserSession, text: str) -> str:
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
async def line_webhook(request: Request, db: Session = Depends(get_db)):
    """LINE Bot Webhook 端點"""
    try:
        # 驗證配置
        validate_config()
        logger.info("=== 收到新的 Webhook 請求 ===")
        
        # 獲取請求內容
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # 獲取請求標頭
        headers = dict(request.headers)
        logger.info("=== 請求詳情 ===")
        logger.info(f"請求路徑: {request.url}")
        logger.info(f"請求方法: {request.method}")
        logger.info(f"請求標頭:\n{json.dumps(headers, indent=2)}")
        logger.info(f"請求內容:\n{json.dumps(json.loads(body_str), ensure_ascii=False, indent=2)}")
        
        events = json.loads(body_str)
        
        # 處理每個事件
        for event in events.get("events", []):
            event_type = event.get("type")
            logger.info(f"\n=== 處理事件 ===")
            logger.info(f"事件類型: {event_type}")
            logger.info(f"事件詳情:\n{json.dumps(event, ensure_ascii=False, indent=2)}")
            
            if event_type == "message":
                logger.info("開始處理訊息事件")
                await handle_message_event(db, event)
                logger.info("訊息事件處理完成")
            elif event_type == "follow":
                logger.info("開始處理關注事件")
                await handle_follow_event(db, event)
                logger.info("關注事件處理完成")
            elif event_type == "unfollow":
                logger.info("開始處理取消關注事件")
                await handle_unfollow_event(db, event)
                logger.info("取消關注事件處理完成")
            elif event_type == "postback":
                logger.info("開始處理 postback 事件")
                await handle_postback_event(db, event)
                logger.info("postback 事件處理完成")
            else:
                logger.warning(f"⚠️ 未處理的事件類型: {event_type}")
        
        logger.info("=== Webhook 請求處理完成 ===")
        return {"status": "ok"}
        
    except Exception as e:
        logger.error("=== Webhook 處理發生錯誤 ===")
        logger.error(f"錯誤類型: {type(e).__name__}")
        logger.error(f"錯誤訊息: {str(e)}")
        logger.error(f"堆疊追蹤:\n{traceback.format_exc()}")
        if hasattr(e, 'response'):
            logger.error(f"錯誤回應: {e.response.text if e.response else 'No response'}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_message_event(db: Session, event: Dict[str, Any]):
    """處理訊息事件"""
    message = event.get("message", {})
    message_type = message.get("type")
    
    logger.info(f"收到訊息事件，類型: {message_type}, 訊息內容: {message}")
    
    if message_type != "text":
        logger.info(f"非文字訊息，忽略處理")
        return
    
    text = message.get("text", "").strip()
    user_id = event["source"]["userId"]
    
    logger.info(f"處理文字訊息，用戶: {user_id}, 文字: '{text}'")
    
    # 獲取或創建用戶
    user, user_stats = get_user_with_permissions(db, user_id)
    session = get_or_create_session(user_id)
    
    # 處理訊息
    response_message = await process_user_message(db, user, session, text)
    
    logger.info(f"生成回應訊息: {response_message}")
    
    # 發送回應（如果有）
    if response_message is not None:  # 修改這裡，只在response_message不是None時發送
        success = send_line_message(user_id, response_message)
        logger.info(f"發送訊息結果: {success}")

async def process_user_message(db: Session, user: LineBotUser, session: MemoryUserSession, text: str) -> str:
    """處理用戶訊息並返回回應"""
    
    # 檢查是否在對話流程中
    if session.state == "waiting_for_gender":
        return handle_gender_input(db, user, session, text)
    
    elif session.state.startswith("chart_binding"):
        return handle_chart_binding_process(db, user, session, text)
    
    elif session.state.startswith("admin_auth"):
        return handle_admin_authentication(db, user, session, text)
    
    elif session.state == "setting_nickname":
        return handle_nickname_setting(db, user, session, text)
    
    # 處理主要功能請求
    text_lower = text.lower()
    
    if text in ["本週占卜", "占卜"]:
        return handle_divination_request(db, user, session)
    
    elif text in ["流年運勢"]:
        return handle_fortune_request(db, user, "yearly")
    
    elif text in ["流月運勢"]:
        return handle_fortune_request(db, user, "monthly")
    
    elif text in ["流日運勢"]:
        return handle_fortune_request(db, user, "daily")
    
    elif text in ["命盤綁定"]:
        return handle_chart_binding(db, user, session)
    
    elif text in ["會員資訊"]:
        user_stats = permission_manager.get_user_stats(db, user)
        return format_user_info(user_stats)
    
    elif text in ["設定暱稱", "修改暱稱", "暱稱設定"]:
        session.set_state("setting_nickname")
        current_nickname = user.display_name or "未設定"
        return f"📝 暱稱設定\n\n目前暱稱：{current_nickname}\n\n請輸入新的暱稱（最多50個字元）："
    
    elif text == "管理員認證":
        session.set_state("admin_auth_phrase")
        return "🔑 請輸入管理員密語："
    
    elif text_lower in ["help", "幫助", "說明"]:
        return LineBotConfig.Messages.WELCOME
    
    else:
        # 未知指令
        return """❓ 不認識的指令

🌟 請使用下方選單按鈕，或輸入「說明」查看功能介紹。

📝 額外功能：
• 輸入「設定暱稱」可修改顯示名稱"""

async def handle_follow_event(db: Session, event: Dict[str, Any]):
    """處理用戶加入事件"""
    user_id = event["source"]["userId"]
    
    # 創建用戶記錄
    user, _ = get_user_with_permissions(db, user_id)
    
    # 發送歡迎訊息
    welcome_message = LineBotConfig.Messages.WELCOME
    send_line_message(user_id, welcome_message)
    
    logger.info(f"新用戶加入: {user_id}")

async def handle_unfollow_event(db: Session, event: Dict[str, Any]):
    """處理用戶離開事件"""
    user_id = event["source"]["userId"]
    
    # 清理用戶會話
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    logger.info(f"用戶離開: {user_id}")

async def handle_postback_event(db: Session, event: Dict[str, Any]):
    """處理 postback 事件（Rich Menu 按鈕點擊）"""
    try:
        postback = event.get("postback", {})
        data = postback.get("data", "")
        user_id = event["source"]["userId"]
        
        logger.info(f"收到 postback 事件，用戶: {user_id}, 數據: {data}")
        
        # 獲取或創建用戶
        user, user_stats = get_user_with_permissions(db, user_id)
        session = get_or_create_session(user_id)
        
        # 根據 postback data 處理不同功能
        response_message = await process_postback_data(db, user, session, data)
        
        # 發送回應
        if response_message:
            send_line_message(user_id, response_message)
            
    except Exception as e:
        logger.error(f"處理 postback 事件錯誤: {e}")

async def process_postback_data(db: Session, user: LineBotUser, session: MemoryUserSession, data: str) -> str:
    """處理 postback 數據並返回回應"""
    logger.info(f"處理 postback 數據: {data}")
    
    # 根據 data 值處理不同功能
    if data == "divination" or "占卜" in data:
        return handle_divination_request(db, user, session)
    elif data == "yearly_fortune" or "流年" in data:
        return handle_fortune_request(db, user, "yearly")
    elif data == "monthly_fortune" or "流月" in data:
        return handle_fortune_request(db, user, "monthly")
    elif data == "daily_fortune" or "流日" in data:
        return handle_fortune_request(db, user, "daily")
    elif data == "chart_binding" or "命盤" in data:
        return handle_chart_binding(db, user, session)
    elif data == "member_info" or "會員" in data:
        user_stats = permission_manager.get_user_stats(db, user)
        return format_user_info(user_stats)
    else:
        logger.warning(f"未知的 postback 數據: {data}")
        return "❓ 未知的功能請求"

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

# 導出路由器
__all__ = ["router"] 