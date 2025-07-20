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
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, PostbackEvent, FollowEvent, UnfollowEvent
)

from ..config.linebot_config import LineBotConfig
from ..services.divination_service import DivinationService
from ..services.user_service import UserService, get_user_stats_from_db
from ..utils.flex_message_generators import (
    generate_divination_result_flex,
    generate_sihua_detail_flex,
    generate_basic_chart_flex,
    generate_taichi_palace_flex
)
from ..utils.flex_carousel_control_panel import generate_carousel_control_panel
from ..utils.flex_instructions import FlexInstructionsGenerator
from ..utils.time_picker_flex_message import TimePickerFlexMessageGenerator
from ..utils.flex_admin_panel import FlexAdminPanelGenerator
import traceback
from ..database.crud import get_user_by_line_id, create_divination_record, get_user_stats, update_user_last_interaction
from ..database.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化 LINE Bot SDK
configuration = Configuration(access_token=LineBotConfig.CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
parser = WebhookParser(LineBotConfig.CHANNEL_SECRET)

# 初始化服務
divination_service = DivinationService()
user_service = UserService()
time_picker_generator = TimePickerFlexMessageGenerator()
instructions_generator = FlexInstructionsGenerator()
admin_panel_generator = FlexAdminPanelGenerator()


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

def send_line_flex_messages(user_id: str, messages: list):
    """發送多個 LINE Flex 訊息給用戶"""
    # ... (此處省略函式實作，因為它在您的原始程式碼中)
    pass # 您需要將原本的 send_line_flex_messages 函式實作放在這裡

@router.post("/callback", include_in_schema=False)
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
            await user_service.handle_follow_event(user_id, reply_token, db)

        elif isinstance(event, UnfollowEvent):
            await user_service.handle_unfollow_event(user_id, db)

        elif isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            text = event.message.text.strip().lower()
            reply_token = event.reply_token

            if text == "功能選單":
                user_stats = await get_user_stats_from_db(user_id, db)
                control_panel = generate_carousel_control_panel(user_stats)
                if control_panel:
                    send_line_flex_messages(user_id, [control_panel])
                else:
                    reply_text(reply_token, "無法生成功能面板，請稍後再試。")
            
            elif text.startswith("占卜"):
                gender = "M" if "男" in text else "F"
                divination_result = divination_service.get_divination_result(gender=gender)
                record_id = await create_divination_record(user_id, divination_result, db)
                flex_message = generate_divination_result_flex(divination_result)
                send_line_flex_messages(user_id, [flex_message])

            elif text.startswith("查看"):
                parts = text.split(" ")
                if len(parts) > 1:
                    sihua_type = parts[1].replace("星更多解釋", "")
                    # ... 處理查看四化解釋的邏輯

            else:
                reply_text(reply_token, "您好！請點擊下方選單或輸入「功能選單」開始使用。")

        elif isinstance(event, PostbackEvent):
            data = event.postback.data
            # ... 處理 Postback 事件的邏輯
    
    return {"status": "ok"}

# 重新實作 send_line_flex_messages 函式
def send_line_flex_messages(user_id: str, messages: list):
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
        message_objects = []
        for msg in messages:
            try:
                if hasattr(msg, 'to_dict'):
                    msg_dict = msg.to_dict()
                    message_objects.append(msg_dict)
                elif isinstance(msg, dict):
                    message_objects.append(msg)
                else:
                    logger.warning(f"無法轉換的訊息格式: {type(msg)}")
            except Exception as convert_error:
                logger.error(f"轉換訊息時發生錯誤: {convert_error}")

        if not message_objects:
            logger.error("沒有成功轉換的訊息")
            return

        data = {
            "to": user_id,
            "messages": message_objects
        }
        
        import requests
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"Flex訊息發送失敗 (HTTP {response.status_code}): {response.text}")
            
    except Exception as e:
        logger.error(f"發送Flex訊息時發生異常: {e}", exc_info=True)

