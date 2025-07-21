"""
LINE Bot Webhook API
處理來自 LINE 的所有訊息和事件
"""
import os
import json
import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, PushMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, PostbackEvent, FollowEvent, UnfollowEvent
)

from ..config.linebot_config import LineBotConfig
from ..logic.divination_logic import get_divination_result
from ..logic.permission_manager import permission_manager
from ..utils.divination_flex_message import DivinationFlexMessageGenerator
from ..utils.flex_carousel_control_panel import generate_carousel_control_panel
from ..utils.flex_instructions import FlexInstructionsGenerator
from ..utils.time_picker_flex_message import TimePickerFlexMessageGenerator
from ..utils.flex_admin_panel import FlexAdminPanelGenerator
import traceback
from ..models.linebot_models import LineBotUser, DivinationHistory
from ..db.database import get_db
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# 簡單的數據庫操作函數
async def get_user_by_line_id(line_user_id: str, db) -> LineBotUser:
    """根據 LINE 用戶 ID 獲取用戶"""
    return db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()

async def create_divination_record(user_id: str, divination_result: dict, db) -> int:
    """創建占卜記錄"""
    try:
        user = await get_user_by_line_id(user_id, db)
        if not user:
            logger.warning(f"用戶 {user_id} 不存在，無法創建占卜記錄")
            return None
        
        # 根據 DivinationHistory 模型的實際字段創建記錄
        record = DivinationHistory(
            user_id=user.id,
            gender=divination_result.get('gender', 'M'),
            divination_time=datetime.utcnow(),
            taichi_palace=divination_result.get('taichi_palace', ''),
            minute_dizhi=divination_result.get('minute_dizhi', ''),
            sihua_results=json.dumps(divination_result.get('sihua_results', [])),
            taichi_palace_mapping=json.dumps(divination_result.get('taichi_palace_mapping', {})),
            taichi_chart_data=json.dumps(divination_result.get('taichi_chart_data', {}))
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        logger.error(f"創建占卜記錄失敗: {e}")
        db.rollback()
        return None

async def update_user_last_interaction(user_id: str, db):
    """更新用戶最後互動時間"""
    try:
        user = await get_user_by_line_id(user_id, db)
        if user:
            user.last_active_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"更新用戶最後互動時間失敗: {e}")
        db.rollback()

# 初始化 LINE Bot SDK
configuration = Configuration(access_token=LineBotConfig.CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
parser = WebhookParser(LineBotConfig.CHANNEL_SECRET)

# 初始化服務
time_picker_generator = TimePickerFlexMessageGenerator()
instructions_generator = FlexInstructionsGenerator()
admin_panel_generator = FlexAdminPanelGenerator()

# 初始化 Flex 消息生成器
divination_flex_generator = DivinationFlexMessageGenerator()


def reply_text(reply_token: str, text: str):
    """發送純文字回覆訊息"""
    try:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )
    except Exception as e:
        logger.error(f"回覆文字訊息失敗: {e}")

def send_line_flex_messages(user_id: str, messages: list, reply_token: str = None):
    """
    發送多個 LINE Flex 訊息給用戶
    
    Args:
        user_id: 用戶ID
        messages: FlexMessage列表
        reply_token: 回覆 token（如果提供，使用 reply API；否則使用 push API）
    """
    try:
        from linebot.v3.messaging import ReplyMessageRequest, PushMessageRequest
        
        if reply_token:
            # 使用 reply API
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=messages
                )
            )
            logger.info(f"使用 reply API 發送 {len(messages)} 個 Flex 訊息")
        else:
            # 使用 push API
            line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=messages
                )
            )
            logger.info(f"使用 push API 發送 {len(messages)} 個 Flex 訊息")
            
    except Exception as e:
        logger.error(f"發送Flex訊息時發生異常: {e}", exc_info=True)

@router.post("/webhook", include_in_schema=False)
async def line_bot_webhook(request: Request, db: Session = Depends(get_db)):
    """LINE Bot Webhook 端點"""
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode(), signature)
    except InvalidSignatureError:
        logger.error("無效的 LINE Signature")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    for event in events:
        user_id = event.source.user_id
        await update_user_last_interaction(user_id, db)
        
        if isinstance(event, FollowEvent):
            reply_token = event.reply_token
            logger.info(f"用戶 {user_id} 關注了機器人")
            # 簡單回應，歡迎用戶
            reply_text(reply_token, "歡迎使用星空紫微斗數！請輸入「功能選單」開始探索。")

        elif isinstance(event, UnfollowEvent):
            logger.info(f"用戶 {user_id} 取消關注了機器人")

        elif isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            text = event.message.text.strip().lower()
            reply_token = event.reply_token

            if text == "功能選單":
                # 獲取或創建用戶物件
                user = await get_user_by_line_id(user_id, db)
                if not user:
                    # 自動創建新用戶
                    user = LineBotUser(
                        line_user_id=user_id,
                        display_name="LINE用戶",
                        is_active=True
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    logger.info(f"自動創建新用戶: {user_id}")
                
                user_stats = permission_manager.get_user_stats(db, user)
                control_panel = generate_carousel_control_panel(user_stats)
                if control_panel:
                    send_line_flex_messages(user_id, [control_panel], reply_token=reply_token)
                else:
                    reply_text(reply_token, "無法生成功能面板，請稍後再試。")
            
            elif text.startswith("占卜"):
                gender = "M" if "男" in text else "F"
                # 獲取或創建用戶物件
                user = await get_user_by_line_id(user_id, db)
                if not user:
                    # 自動創建新用戶
                    user = LineBotUser(
                        line_user_id=user_id,
                        display_name="LINE用戶",
                        is_active=True
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    logger.info(f"自動創建新用戶: {user_id}")
                
                divination_result = get_divination_result(db, user, gender)
                if divination_result.get('success'):
                    record_id = await create_divination_record(user_id, divination_result, db)
                    # 根據用戶等級設定 user_type
                    user_type = "admin" if user.is_admin() else ("premium" if user.is_premium() else "free")
                    # 使用正確的函數生成占卜結果訊息
                    flex_messages = divination_flex_generator.generate_divination_messages(divination_result, user_type=user_type)
                    if flex_messages:
                        send_line_flex_messages(user_id, flex_messages, reply_token=reply_token)
                    else:
                        reply_text(reply_token, "占卜結果生成失敗，請稍後再試。")
                else:
                    reply_text(reply_token, divination_result.get('message', '占卜失敗，請稍後再試。'))

            elif text.startswith("查看"):
                parts = text.split(" ")
                if len(parts) > 1:
                    sihua_type = parts[1].replace("星更多解釋", "")
                    # 使用正確的函數生成四化詳細資訊
                    # detail_message = generate_sihua_detail_message(sihua_type, user_type="free")
                    # if detail_message:
                    #     send_line_flex_messages(user_id, [detail_message])
                    # else:
                    reply_text(reply_token, "四化詳細解釋功能開發中，敬請期待。")

            else:
                reply_text(reply_token, "您好！請點擊下方選單或輸入「功能選單」開始使用。")

        elif isinstance(event, PostbackEvent):
            data = event.postback.data
            reply_token = event.reply_token
            logger.info(f"收到 Postback 事件: {data}")
            
            # 處理不同的 Postback 動作
            if data == "action=show_member_info":
                # 獲取用戶資訊
                user = await get_user_by_line_id(user_id, db)
                if user:
                    user_stats = permission_manager.get_user_stats(db, user)
                    membership_level = user_stats.get("user_info", {}).get("membership_level", "free")
                    total_divinations = user_stats.get("statistics", {}).get("total_divinations", 0)
                    weekly_divinations = user_stats.get("statistics", {}).get("weekly_divinations", 0)
                    
                    member_info = f"""👤 會員資訊
                    
🏷️ 會員等級: {membership_level}
🔮 總占卜次數: {total_divinations}
📅 本週占卜: {weekly_divinations}
✨ 帳號狀態: 正常"""
                    
                    reply_text(reply_token, member_info)
                else:
                    reply_text(reply_token, "無法獲取會員資訊，請稍後再試。")
                    
            elif data == "action=show_instructions":
                # 使用說明
                instructions = """📖 使用說明
                
🔮 基本占卜：輸入「占卜」或「占卜男」/「占卜女」
⭐ 功能選單：輸入「功能選單」查看所有功能
👤 會員資訊：查看您的會員狀態和使用記錄
💎 升級會員：聯繫管理員升級為付費會員

✨ 更多功能正在開發中，敬請期待！"""
                
                reply_text(reply_token, instructions)
                
            elif data == "control_panel=basic_divination":
                # 基本占卜功能 - 所有用戶都可以使用
                reply_text(reply_token, "請輸入「占卜」開始占卜，或輸入「占卜男」/「占卜女」指定性別。")
                
            elif data == "action=weekly_fortune":
                # 週運勢功能
                user = await get_user_by_line_id(user_id, db)
                if user and (user.is_admin() or user.is_premium()):
                    reply_text(reply_token, "週運勢功能開發中，敬請期待。")
                else:
                    reply_text(reply_token, "此功能需要付費會員才能使用，請聯繫管理員升級會員。")
                    
            elif data.startswith("control_panel=yearly_fortune") or data.startswith("control_panel=monthly_fortune") or data.startswith("control_panel=daily_fortune"):
                # 進階占卜功能
                user = await get_user_by_line_id(user_id, db)
                if user and (user.is_admin() or user.is_premium()):
                    reply_text(reply_token, "進階占卜功能開發中，敬請期待。")
                else:
                    reply_text(reply_token, "此功能需要付費會員才能使用，請聯繫管理員升級會員。")
                    
            elif data.startswith("control_panel=member_upgrade"):
                # 會員升級
                user = await get_user_by_line_id(user_id, db)
                if user and user.is_admin():
                    reply_text(reply_token, "您已經是管理員，擁有所有權限。")
                elif user and user.is_premium():
                    reply_text(reply_token, "您已經是付費會員，感謝您的支持！")
                else:
                    reply_text(reply_token, "請聯繫管理員升級為付費會員，享受更多功能。")
                    
            elif data.startswith("admin_action="):
                # 管理員功能
                user = await get_user_by_line_id(user_id, db)
                if user and user.is_admin():
                    reply_text(reply_token, "管理員功能開發中，敬請期待。")
                else:
                    reply_text(reply_token, "此功能僅限管理員使用。")
                    
            else:
                # 未知的 Postback 事件
                logger.warning(f"未處理的 Postback 事件: {data}")
                reply_text(reply_token, "功能開發中，敬請期待。")

    return {"status": "ok"}

