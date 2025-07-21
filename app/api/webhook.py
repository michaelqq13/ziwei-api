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

def create_gender_selection_message():
    """創建性別選擇 Flex Message"""
    try:
        from linebot.v3.messaging import FlexMessage, FlexBubble, FlexBox, FlexText, FlexButton, PostbackAction
        
        bubble = FlexBubble(
            size="micro",
            header=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="🔮 開始占卜",
                        weight="bold",
                        size="lg",
                        color="#FFD700",
                        align="center"
                    ),
                    FlexText(
                        text="請選擇性別",
                        size="sm",
                        color="#B0C4DE",
                        align="center",
                        margin="xs"
                    )
                ],
                paddingAll="12px",
                backgroundColor="#1A1A2E"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexButton(
                                action=PostbackAction(
                                    label="👨 男性",
                                    data="divination_gender=M",
                                    displayText="選擇男性"
                                ),
                                style="primary",
                                color="#4A90E2",
                                height="md",
                                flex=1
                            ),
                            FlexButton(
                                action=PostbackAction(
                                    label="👩 女性", 
                                    data="divination_gender=F",
                                    displayText="選擇女性"
                                ),
                                style="primary",
                                color="#E67E22",
                                height="md",
                                flex=1,
                                margin="sm"
                            )
                        ],
                        spacing="sm"
                    ),
                    FlexText(
                        text="✨ 選擇後立即開始占卜",
                        size="xs",
                        color="#87CEEB",
                        align="center",
                        margin="md"
                    )
                ],
                spacing="sm",
                paddingAll="16px"
            )
        )
        
        return FlexMessage(
            alt_text="🔮 性別選擇",
            contents=bubble
        )
        
    except Exception as e:
        logger.error(f"創建性別選擇訊息失敗: {e}")
        return None

# 測試模式相關輔助函數
async def _is_original_admin(user_id: str, db) -> bool:
    """檢查是否為原始管理員（忽略測試模式）"""
    user = await get_user_by_line_id(user_id, db)
    return user and user.membership_level == LineBotConfig.MembershipLevel.ADMIN

async def _handle_test_mode_command(text: str, user_id: str, reply_token: str, db):
    """處理測試模式指令"""
    user = await get_user_by_line_id(user_id, db)
    if not user:
        reply_text(reply_token, "用戶不存在")
        return
    
    # 解析指令
    if text == "測試免費":
        user.set_test_mode(LineBotConfig.MembershipLevel.FREE, 10)
        db.commit()
        reply_text(reply_token, """🧪 已切換為免費會員身份
        
⏰ 將在 10 分鐘後自動恢復管理員身份
💡 所有功能都會以免費會員視角運作
🔄 輸入「測試管理員」可立即恢復""")
        
    elif text == "測試付費":
        user.set_test_mode(LineBotConfig.MembershipLevel.PREMIUM, 10)
        db.commit()
        reply_text(reply_token, """🧪 已切換為付費會員身份
        
⏰ 將在 10 分鐘後自動恢復管理員身份  
💡 所有功能都會以付費會員視角運作
🔄 輸入「測試管理員」可立即恢復""")
        
    elif text == "測試管理員":
        user.clear_test_mode()
        db.commit()
        reply_text(reply_token, """✅ 已恢復管理員身份
        
👑 歡迎回來，管理員！
💫 所有管理員功能已恢復""")
        
    else:
        reply_text(reply_token, """🧪 測試模式指令：
        
• 測試免費 - 切換為免費會員（10分鐘）
• 測試付費 - 切換為付費會員（10分鐘）  
• 測試管理員 - 立即恢復管理員身份
• 查看測試狀態 - 查看當前測試狀態""")

async def _handle_test_status_command(user_id: str, reply_token: str, db):
    """處理查看測試狀態指令"""
    user = await get_user_by_line_id(user_id, db)
    if not user:
        reply_text(reply_token, "用戶不存在")
        return
    
    if user.is_in_test_mode():
        test_info = user.get_test_mode_info()
        role_name = {
            LineBotConfig.MembershipLevel.FREE: "免費會員",
            LineBotConfig.MembershipLevel.PREMIUM: "付費會員",
            LineBotConfig.MembershipLevel.ADMIN: "管理員"
        }.get(test_info["test_role"], test_info["test_role"])
        
        reply_text(reply_token, f"""🧪 當前測試狀態
        
🎭 測試身份: {role_name}
⏰ 剩餘時間: {test_info['remaining_minutes']} 分鐘
📅 過期時間: {test_info['expires_at'].strftime('%H:%M:%S')}
🔄 輸入「測試管理員」可立即恢復""")
    else:
        reply_text(reply_token, """✅ 當前狀態：管理員身份
        
👑 您目前使用管理員身份
🧪 輸入測試指令可切換測試身份：
• 測試免費
• 測試付費""")


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
                # 檢查是否指定了性別
                if "男" in text or "女" in text:
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
                else:
                    # 沒有指定性別，顯示性別選擇選單
                    gender_selection = create_gender_selection_message()
                    if gender_selection:
                        send_line_flex_messages(user_id, [gender_selection], reply_token=reply_token)
                    else:
                        reply_text(reply_token, "請輸入「占卜男」或「占卜女」開始占卜。")

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

            # 管理員測試模式指令
            elif text.startswith("測試") and await _is_original_admin(user_id, db):
                await _handle_test_mode_command(text, user_id, reply_token, db)
            
            elif text == "查看測試狀態" and await _is_original_admin(user_id, db):
                await _handle_test_status_command(user_id, reply_token, db)

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
                    
                    # 檢查測試模式
                    test_prefix = ""
                    if user.is_in_test_mode():
                        test_info = user.get_test_mode_info()
                        test_prefix = f"🧪 [測試模式 - 剩餘{test_info['remaining_minutes']}分鐘]\n"
                        membership_level = test_info["test_role"]
                    
                    member_info = f"""{test_prefix}👤 會員資訊
                    
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
                
            elif data == "action=show_control_panel":
                # 顯示功能選單
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
                    
            elif data.startswith("divination_gender="):
                # 處理性別選擇的 Postback
                gender = data.split("=")[1]
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
                
                # 直接進行占卜
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
                    
            else:
                # 未知的 Postback 事件
                logger.warning(f"未處理的 Postback 事件: {data}")
                reply_text(reply_token, "功能開發中，敬請期待。")
    
    return {"status": "ok"}

