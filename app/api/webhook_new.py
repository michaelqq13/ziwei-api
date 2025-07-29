"""
全新 LINE Bot Webhook API
重構版本，配合新的功能選單系統
"""
import os
import json
import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, 
    TextMessage, PushMessageRequest, QuickReply, QuickReplyItem, PostbackAction
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, PostbackEvent, FollowEvent, UnfollowEvent
)

from ..config.linebot_config import LineBotConfig
from ..logic.divination_logic import get_divination_result
from ..logic.permission_manager import permission_manager
from ..utils.divination_flex_message import DivinationFlexMessageGenerator
from ..utils.new_function_menu import new_function_menu_generator
from ..utils.flex_instructions import FlexInstructionsGenerator
from ..models.linebot_models import LineBotUser, DivinationHistory
from ..db.database import get_db
from datetime import datetime
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

# LINE Bot SDK 初始化
configuration = Configuration(access_token=LineBotConfig.CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
parser = WebhookParser(LineBotConfig.CHANNEL_SECRET)

# 初始化服務
divination_flex_generator = DivinationFlexMessageGenerator()
instructions_generator = FlexInstructionsGenerator()

class WebhookHandler:
    """新版 Webhook 處理器"""
    
    def __init__(self):
        self.db = None
        self.user_id = None
        self.reply_token = None
    
    async def get_or_create_user(self, user_id: str, db: Session) -> LineBotUser:
        """獲取或創建用戶"""
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
        if not user:
            user = LineBotUser(
                line_user_id=user_id,
                display_name="LINE用戶",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"自動創建新用戶: {user_id}")
        return user
    
    async def update_user_activity(self, user_id: str, db: Session):
        """更新用戶活動時間"""
        try:
            user = await self.get_or_create_user(user_id, db)
            user.last_active_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            logger.error(f"更新用戶活動時間失敗: {e}")
            db.rollback()
    
    def reply_text(self, text: str):
        """回覆文字訊息"""
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
        except Exception as e:
            logger.error(f"回覆文字訊息失敗: {e}")
    
    def send_flex_message(self, flex_message):
        """發送 Flex 訊息"""
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[flex_message]
                )
            )
        except Exception as e:
            logger.error(f"發送 Flex 訊息失敗: {e}")
    
    def create_gender_selection(self):
        """創建性別選擇 Quick Reply"""
        quick_reply = QuickReply(
            items=[
                QuickReplyItem(
                    action=PostbackAction(
                        label="👨 男性",
                        data="gender=M",
                        displayText="選擇男性"
                    )
                ),
                QuickReplyItem(
                    action=PostbackAction(
                        label="👩 女性",
                        data="gender=F",
                        displayText="選擇女性"
                    )
                )
            ]
        )
        
        return TextMessage(
            text="🔮 開始占卜\n\n請選擇您的性別：",
            quickReply=quick_reply
        )
    
    async def handle_divination(self, gender: str):
        """處理占卜邏輯"""
        try:
            user = await self.get_or_create_user(self.user_id, self.db)
            
            # 執行占卜
            divination_result = get_divination_result(self.db, user, gender)
            
            if divination_result.get('success'):
                # 從占卜結果中獲取記錄 ID (不重複創建)
                record_id = divination_result.get('divination_id')
                logger.info(f"使用占卜結果中的記錄 ID: {record_id}")
                
                # 根據用戶等級設定 user_type
                user_type = "admin" if user.is_admin() else ("premium" if user.is_premium() else "free")
                
                # 生成占卜結果訊息 (使用全局變量)
                flex_messages = divination_flex_generator.generate_divination_messages(divination_result, user_type=user_type)
                
                if flex_messages:
                    # 發送結果
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=self.reply_token,
                            messages=flex_messages
                        )
                    )
                    
                    # 管理員額外功能
                    if user.is_admin():
                        await self.send_admin_quick_buttons(record_id)
                else:
                    self.reply_text("占卜結果生成失敗，請稍後再試。")
            else:
                self.reply_text(divination_result.get('message', '占卜失敗，請稍後再試。'))
                
        except Exception as e:
            logger.error(f"處理占卜失敗: {e}")
            self.reply_text("占卜過程發生錯誤，請稍後再試。")
    
    async def send_admin_quick_buttons(self, record_id: int = None):
        """發送管理員快速按鈕"""
        try:
            quick_reply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🏛️ 太極十二宮",
                            data=f"admin_taichi={record_id or 'latest'}",
                            displayText="查看太極十二宮"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="📊 基本命盤",
                            data=f"admin_chart={record_id or 'latest'}",
                            displayText="查看基本命盤"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🌌 功能選單",
                            data="action=function_menu",
                            displayText="返回功能選單"
                        )
                    )
                ]
            )
            
            message = TextMessage(
                text="👑 管理員快速功能",
                quickReply=quick_reply
            )
            
            # 延遲發送避免衝突
            import asyncio
            await asyncio.sleep(0.5)
            
            line_bot_api.push_message(
                PushMessageRequest(
                    to=self.user_id,
                    messages=[message]
                )
            )
        except Exception as e:
            logger.error(f"發送管理員快速按鈕失敗: {e}")
    
    async def handle_follow_event(self):
        """處理關注事件"""
        logger.info(f"用戶 {self.user_id} 關注了機器人")
        self.reply_text("🌟 歡迎使用星空紫微斗數！\n\n請點擊下方選單開始探索，或輸入「功能選單」查看所有功能。")
    
    async def handle_text_message(self, text: str):
        """處理文字訊息"""
        text = text.strip().lower()
        
        if text == "功能選單":
            await self.show_function_menu()
        
        elif text == "本週占卜" or text == "占卜":
            gender_selection = self.create_gender_selection()
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[gender_selection]
                )
            )
        
        elif text.startswith("占卜"):
            if "男" in text:
                await self.handle_divination("M")
            elif "女" in text:
                await self.handle_divination("F")
            else:
                gender_selection = self.create_gender_selection()
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=self.reply_token,
                        messages=[gender_selection]
                    )
                )
        
        # 管理員測試指令
        elif text.startswith("測試") and await self.is_admin():
            await self.handle_test_commands(text)
        
        elif text == "查看測試狀態" and await self.is_admin():
            await self.show_test_status()
        
        else:
            self.reply_text("您好！請點擊下方選單或輸入「功能選單」開始使用。")
    
    async def handle_postback_event(self, data: str):
        """處理 Postback 事件"""
        logger.info(f"收到 Postback: {data}")
        
        if data == "action=member_info":
            logger.info("處理會員資訊請求")
            await self.show_member_info()
        elif data == "action=function_menu":
            logger.info("處理功能選單請求")
            await self.show_function_menu()
        elif data == "action=weekly_divination":
            logger.info("處理本週占卜請求")
            gender_selection = self.create_gender_selection()
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[gender_selection]
                )
            )
        elif data == "action=instructions":
            logger.info("處理使用說明請求")
            await self.show_instructions()
        elif data.startswith("category="):
            logger.info("處理功能分類請求")
            await self.handle_category_selection(data)
        elif data.startswith("function="):
            await self.handle_function_action(data)
        elif data.startswith("admin_function="):
            await self.handle_admin_function(data)
        elif data.startswith("test_function="):
            await self.handle_test_function(data)
        elif data.startswith("gender="):
            await self.handle_gender_selection(data)
        elif data.startswith("chart="):
            await self.handle_chart_request(data)
        elif data.startswith("admin_chart="):
            await self.handle_admin_chart_request(data)
        elif data.startswith("admin_taichi="):
            await self.handle_admin_taichi_request(data)
        elif data.startswith("time_select="):
            await self.handle_time_divination_selection(data)
        elif data.startswith("time_gender="):
            await self.handle_time_divination_execution(data)
        else:
            logger.warning(f"未知的 Postback 數據: {data}")
            self.reply_text("未知的操作，請重新選擇。")

    async def handle_gender_selection(self, data: str):
        """處理性別選擇並進行占卜"""
        try:
            gender = data.split("=")[1]
            logger.info(f"用戶選擇性別: {gender}")
            
            user = await self.get_or_create_user(self.user_id, self.db)
            
            # 直接進行占卜
            divination_result = get_divination_result(self.db, user, gender)
            logger.info(f"占卜結果獲取完成，成功：{divination_result.get('success')}")
            
            if divination_result.get('success'):
                # 從占卜結果中獲取記錄 ID (不重複創建)
                record_id = divination_result.get('divination_id')
                logger.info(f"使用占卜結果中的記錄 ID: {record_id}")
                
                # 根據用戶等級設定 user_type
                user_type = "admin" if user.is_admin() else ("premium" if user.is_premium() else "free")
                
                # 生成占卜結果訊息 (使用全局變量)
                flex_messages = divination_flex_generator.generate_divination_messages(divination_result, user_type=user_type)
                
                if flex_messages:
                    logger.info("發送占卜結果")
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=self.reply_token,
                            messages=flex_messages
                        )
                    )
                    
                    # 如果是管理員，發送快速按鈕
                    if user.is_admin():
                        await self.send_admin_quick_buttons(record_id)
                else:
                    logger.error("生成占卜結果訊息失敗")
                    self.reply_text("占卜結果生成失敗，請稍後再試。")
            else:
                error_msg = divination_result.get('message', '占卜失敗')
                logger.error(f"占卜失敗: {error_msg}")
                self.reply_text(f"占卜失敗：{error_msg}")
                
        except Exception as e:
            logger.error(f"處理性別選擇失敗: {e}", exc_info=True)
            self.reply_text("占卜過程發生錯誤，請稍後再試。")

    async def handle_category_selection(self, data: str):
        """處理功能分類選擇 (第二層選單)"""
        try:
            category = data.split("=")[1]
            logger.info(f"用戶選擇功能分類: {category}")
            
            user = await self.get_or_create_user(self.user_id, self.db)
            user_stats = permission_manager.get_user_stats(self.db, user)
            
            category_menu = new_function_menu_generator.generate_category_menu(category, user_stats)
            
            if category_menu:
                logger.info(f"成功生成 {category} 分類選單")
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=self.reply_token,
                        messages=[category_menu]
                    )
                )
                logger.info("分類選單發送成功")
            else:
                logger.error(f"無法生成 {category} 分類選單")
                self.reply_text("無法生成該分類選單，請檢查權限或稍後再試。")
                
        except Exception as e:
            logger.error(f"處理分類選擇失敗: {e}", exc_info=True)
            self.reply_text("分類選單載入失敗，請稍後再試。")
    
    async def show_function_menu(self):
        """顯示功能選單"""
        try:
            logger.info("開始生成功能選單")
            user = await self.get_or_create_user(self.user_id, self.db)
            logger.info(f"獲取用戶成功: {user.line_user_id}")
            
            user_stats = permission_manager.get_user_stats(self.db, user)
            logger.info(f"獲取用戶統計成功: {user_stats}")
            
            function_menu = new_function_menu_generator.generate_function_menu(user_stats)
            logger.info(f"生成功能選單結果: {function_menu is not None}")
            
            if function_menu:
                logger.info("準備發送功能選單 Flex Message")
                self.send_flex_message(function_menu)
                logger.info("功能選單發送成功")
            else:
                logger.error("功能選單生成失敗，返回 None")
                self.reply_text("無法生成功能選單，請稍後再試。")
        except Exception as e:
            logger.error(f"顯示功能選單失敗: {e}", exc_info=True)
            self.reply_text("功能選單載入失敗，請稍後再試。")
    
    async def show_member_info(self):
        """顯示會員資訊"""
        try:
            user = await self.get_or_create_user(self.user_id, self.db)
            user_stats = permission_manager.get_user_stats(self.db, user)
            
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
✨ 帳號狀態: 正常

💫 感謝您使用星空紫微斗數！"""
            
            self.reply_text(member_info)
        except Exception as e:
            logger.error(f"顯示會員資訊失敗: {e}")
            self.reply_text("無法獲取會員資訊，請稍後再試。")
    
    async def show_instructions(self):
        """顯示使用說明"""
        instructions = """📖 使用說明

🔮 基本功能：
• 本週占卜 - 根據當下時間進行觸機占卜
• 會員資訊 - 查看個人使用記錄和權限
• 功能選單 - 智能控制面板，權限感知

💫 操作方式：
1. 點擊下方選單按鈕快速進入功能
2. 或直接輸入文字指令（如「占卜」）
3. 依照系統提示完成操作

💎 升級會員：
聯繫管理員升級為付費會員，享受更多功能

✨ 更多功能正在開發中，敬請期待！"""
        
        self.reply_text(instructions)
    
    async def handle_function_action(self, data: str):
        """處理功能選單中的動作"""
        action = data.split("=")[1]
        
        if action == "weekly_divination":
            gender_selection = self.create_gender_selection()
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[gender_selection]
                )
            )
        
        elif action == "member_info":
            await self.show_member_info()
        
        elif action == "instructions":
            await self.show_instructions()
        
        elif action in ["daxian_fortune", "xiaoxian_fortune", "yearly_fortune", "monthly_fortune"]:
            user = await self.get_or_create_user(self.user_id, self.db)
            if user.is_admin() or user.is_premium():
                self.reply_text("進階占卜功能開發中，敬請期待。")
            else:
                self.reply_text("此功能需要付費會員才能使用，請聯繫管理員升級會員。")
        
        else:
            self.reply_text("功能開發中，敬請期待。")
    
    async def handle_admin_function(self, data: str):
        """處理管理員功能"""
        user = await self.get_or_create_user(self.user_id, self.db)
        if not user.is_admin():
            self.reply_text("此功能僅限管理員使用。")
            return
        
        action = data.split("=")[1]
        
        function_map = {
            "time_divination": None,  # 使用專門的處理邏輯
            "system_monitor": "系統監控功能開發中，敬請期待。",
            "user_management": "用戶管理功能開發中，敬請期待。",
            "menu_management": "選單管理功能開發中，敬請期待。"
        }
        
        if action == "time_divination":
            await self.handle_time_divination()
        else:
            message = function_map.get(action, "管理員功能開發中，敬請期待。")
            self.reply_text(message)
    
    async def handle_test_function(self, data: str):
        """處理測試功能"""
        user = await self.get_or_create_user(self.user_id, self.db)
        if not user.membership_level == LineBotConfig.MembershipLevel.ADMIN:
            self.reply_text("此功能僅限原始管理員使用。")
            return
        
        action = data.split("=")[1]
        
        if action == "test_free":
            user.set_test_mode(LineBotConfig.MembershipLevel.FREE, 10)
            self.db.commit()
            self.reply_text("🧪 已切換為免費會員身份\n⏰ 將在 10 分鐘後自動恢復管理員身份")
        
        elif action == "test_premium":
            user.set_test_mode(LineBotConfig.MembershipLevel.PREMIUM, 10)
            self.db.commit()
            self.reply_text("🧪 已切換為付費會員身份\n⏰ 將在 10 分鐘後自動恢復管理員身份")
        
        elif action == "restore_admin":
            user.clear_test_mode()
            self.db.commit()
            self.reply_text("✅ 已恢復管理員身份\n👑 歡迎回來，管理員！")
        
        elif action == "check_status":
            await self.show_test_status()
    
    async def show_test_status(self):
        """顯示測試狀態"""
        user = await self.get_or_create_user(self.user_id, self.db)
        
        if user.is_in_test_mode():
            test_info = user.get_test_mode_info()
            role_name = {
                LineBotConfig.MembershipLevel.FREE: "免費會員",
                LineBotConfig.MembershipLevel.PREMIUM: "付費會員",
                LineBotConfig.MembershipLevel.ADMIN: "管理員"
            }.get(test_info["test_role"], test_info["test_role"])
            
            message = f"""🧪 當前測試狀態

🎭 測試身份: {role_name}
⏰ 剩餘時間: {test_info['remaining_minutes']} 分鐘
📅 過期時間: {test_info['expires_at'].strftime('%H:%M:%S')}
🔄 可透過測試功能立即恢復"""
        else:
            message = """✅ 當前狀態：管理員身份

👑 您目前使用管理員身份
🧪 可透過測試功能切換測試身份"""
        
        self.reply_text(message)
    
    async def show_taichi_info(self, data: str):
        """顯示太極十二宮資訊"""
        user = await self.get_or_create_user(self.user_id, self.db)
        if not user.is_admin():
            self.reply_text("此功能僅限管理員使用。")
            return
        
        record_id = data.split("=")[1]
        logger.info(f"查看太極十二宮，record_id: {record_id}")
        
        target_record = None
        
        if record_id == "latest":
            # 獲取最新占卜記錄
            target_record = self.db.query(DivinationHistory).filter(
                DivinationHistory.user_id == user.id
            ).order_by(DivinationHistory.divination_time.desc()).first()
        else:
            # 獲取指定 ID 的占卜記錄
            try:
                record_id_int = int(record_id)
                target_record = self.db.query(DivinationHistory).filter(
                    DivinationHistory.id == record_id_int,
                    DivinationHistory.user_id == user.id
                ).first()
            except (ValueError, TypeError):
                logger.error(f"無效的記錄 ID: {record_id}")
                self.reply_text("無效的記錄 ID，請重新進行占卜。")
                return
        
        if target_record:
            try:
                # 解析太極宮對映
                taichi_palace_mapping = json.loads(target_record.taichi_palace_mapping or "{}")
                # 解析太極盤數據 (注意：這裡存儲的是 palaces 數據，不是 basic_chart)
                taichi_chart_palaces = json.loads(target_record.taichi_chart_data or "{}")
                
                logger.info(f"太極宮對映數據: {len(taichi_palace_mapping)} 個宮位")
                logger.info(f"太極盤宮位數據: {len(taichi_chart_palaces)} 個宮位")
                
                # 重構占卜結果數據 - 正確的數據結構
                divination_result = {
                    "taichi_palace_mapping": taichi_palace_mapping,
                    "basic_chart": taichi_chart_palaces,  # 使用 taichi_chart_data 作為 basic_chart
                    "divination_time": target_record.divination_time.strftime('%Y-%m-%d %H:%M'),
                    "taichi_palace": target_record.taichi_palace,
                    "minute_dizhi": target_record.minute_dizhi,
                    "record_id": target_record.id
                }
                
                # 檢查必要數據
                if not divination_result["taichi_palace_mapping"]:
                    logger.error("太極宮對映數據為空")
                    self.reply_text("太極宮對映數據為空，請重新進行占卜。")
                    return
                    
                if not divination_result["basic_chart"]:
                    logger.error("太極盤宮位數據為空")
                    self.reply_text("太極盤宮位數據為空，請重新進行占卜。")
                    return
                
                logger.info("開始生成太極十二宮 Flex Message")
                
                # 生成太極十二宮 Flex Message
                taichi_flex_message = divination_flex_generator.generate_taichi_palace_message(divination_result)
                
                if taichi_flex_message:
                    logger.info("成功生成太極十二宮 Flex Message")
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=self.reply_token,
                            messages=[taichi_flex_message]
                        )
                    )
                else:
                    logger.error("生成太極十二宮 Flex Message 失敗")
                    self.reply_text("太極十二宮資訊生成失敗，請稍後再試。")
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失敗: {e}")
                self.reply_text("太極宮數據格式錯誤，請重新進行占卜。")
            except Exception as e:
                logger.error(f"處理太極宮資訊失敗: {e}", exc_info=True)
                self.reply_text("太極宮資訊處理失敗，請重新進行占卜。")
        else:
            self.reply_text("未找到指定的占卜記錄，請確認記錄是否存在。")
    
    async def show_chart_info(self, data: str):
        """顯示基本命盤資訊"""
        user = await self.get_or_create_user(self.user_id, self.db)
        if not user.is_admin():
            self.reply_text("此功能僅限管理員使用。")
            return
        
        self.reply_text("基本命盤查看功能開發中，敬請期待。")
    
    async def is_admin(self) -> bool:
        """檢查是否為管理員"""
        user = await self.get_or_create_user(self.user_id, self.db)
        return user.membership_level == LineBotConfig.MembershipLevel.ADMIN
    
    async def handle_test_commands(self, text: str):
        """處理測試指令"""
        if not await self.is_admin():
            return
        
        user = await self.get_or_create_user(self.user_id, self.db)
        
        if text == "測試免費":
            user.set_test_mode(LineBotConfig.MembershipLevel.FREE, 10)
            self.db.commit()
            self.reply_text("🧪 已切換為免費會員身份\n⏰ 將在 10 分鐘後自動恢復管理員身份")
        
        elif text == "測試付費":
            user.set_test_mode(LineBotConfig.MembershipLevel.PREMIUM, 10)
            self.db.commit()
            self.reply_text("🧪 已切換為付費會員身份\n⏰ 將在 10 分鐘後自動恢復管理員身份")
        
        elif text == "測試管理員":
            user.clear_test_mode()
            self.db.commit()
            self.reply_text("✅ 已恢復管理員身份\n👑 歡迎回來，管理員！")

    async def handle_chart_request(self, data: str):
        """處理命盤請求"""
        try:
            # 解析請求數據
            chart_type = data.split("=")[1] if "=" in data else "basic"
            logger.info(f"處理命盤請求: {chart_type}")
            
            user = await self.get_or_create_user(self.user_id, self.db)
            
            # 檢查權限
            if not (user.is_admin() or user.is_premium()):
                self.reply_text("命盤功能需要付費會員才能使用，請聯繫管理員升級會員。")
                return
            
            # 功能開發中
            self.reply_text("命盤功能開發中，敬請期待。")
            
        except Exception as e:
            logger.error(f"處理命盤請求失敗: {e}")
            self.reply_text("命盤請求處理失敗，請稍後再試。")

    async def handle_admin_chart_request(self, data: str):
        """處理管理員命盤請求"""
        try:
            user = await self.get_or_create_user(self.user_id, self.db)
            
            # 檢查管理員權限
            if not user.is_admin():
                self.reply_text("此功能僅限管理員使用。")
                return
            
            # 解析請求數據
            chart_data = data.split("=")[1] if "=" in data else "latest"
            logger.info(f"管理員命盤請求: {chart_data}")
            
            if chart_data == "latest":
                # 獲取最新占卜記錄
                latest_record = self.db.query(DivinationHistory).filter(
                    DivinationHistory.user_id == user.id
                ).order_by(DivinationHistory.divination_time.desc()).first()
                
                if latest_record:
                    chart_info = f"""📊 基本命盤資訊

⏰ 占卜時間: {latest_record.divination_time.strftime('%Y-%m-%d %H:%M')}
🔮 太極宮: {latest_record.taichi_palace}
🌟 分鐘地支: {latest_record.minute_dizhi}
👤 性別: {'男性' if latest_record.gender == 'M' else '女性'}

💫 更詳細的命盤功能開發中..."""
                    self.reply_text(chart_info)
                else:
                    self.reply_text("未找到占卜記錄，請先進行占卜。")
            else:
                self.reply_text("指定記錄命盤功能開發中。")
                
        except Exception as e:
            logger.error(f"處理管理員命盤請求失敗: {e}")
            self.reply_text("管理員命盤請求處理失敗，請稍後再試。")

    async def handle_admin_taichi_request(self, data: str):
        """處理管理員太極十二宮請求"""
        try:
            logger.info(f"處理太極十二宮請求: {data}")
            await self.show_taichi_info(data)
        except Exception as e:
            logger.error(f"處理太極十二宮請求失敗: {e}")
            self.reply_text("太極十二宮請求處理失敗，請稍後再試。")

    async def handle_time_divination_selection(self, data: str):
        """處理指定時間占卜選擇"""
        try:
            time_value = data.split("=")[1]
            logger.info(f"用戶選擇指定時間占卜: {time_value}")
            
            if time_value == "custom":
                self.reply_text("請輸入您想要占卜的時間（格式：YYYY-MM-DD HH:MM），例如：2025-01-15 14:30\n\n輸入後我會請您選擇性別。")
                return
            else:
                # 保存選擇的時間，然後請求性別選擇
                # 這裡我們需要一個臨時存儲機制，或者直接在 postback 中包含時間信息
                gender_selection = self.create_time_divination_gender_selection(time_value)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=self.reply_token,
                        messages=[gender_selection]
                    )
                )
                
        except Exception as e:
            logger.error(f"處理指定時間占卜選擇失敗: {e}", exc_info=True)
            self.reply_text("時間選擇處理錯誤，請稍後再試。")

    def create_time_divination_gender_selection(self, time_value: str):
        """創建指定時間占卜的性別選擇 Quick Reply"""
        quick_reply = QuickReply(
            items=[
                QuickReplyItem(
                    action=PostbackAction(
                        label="👨 男性",
                        data=f"time_gender=M&time={time_value}",
                        displayText="選擇男性"
                    )
                ),
                QuickReplyItem(
                    action=PostbackAction(
                        label="👩 女性", 
                        data=f"time_gender=F&time={time_value}",
                        displayText="選擇女性"
                    )
                )
            ]
        )
        
        # 顯示選擇的時間
        if time_value == "now":
            time_display = "現在"
        else:
            time_display = time_value
            
        return TextMessage(
            text=f"⏰ 指定時間占卜\n\n選擇的時間：{time_display}\n\n請選擇您的性別：",
            quickReply=quick_reply
        )

    async def handle_time_divination_execution(self, data: str):
        """處理指定時間占卜的執行"""
        try:
            # 解析數據：time_gender=M&time=2025-01-15 14:30
            parts = data.split("=")[1]  # 獲取 "M&time=2025-01-15 14:30"
            gender_and_time = parts.split("&time=")  # 分割為 ["M", "2025-01-15 14:30"]
            gender = gender_and_time[0]
            time_value = gender_and_time[1] if len(gender_and_time) > 1 else "now"
            
            logger.info(f"用戶選擇指定時間占卜，性別: {gender}, 時間: {time_value}")
            
            user = await self.get_or_create_user(self.user_id, self.db)
            
            # 解析指定時間
            target_time = None
            if time_value != "now":
                try:
                    from datetime import datetime
                    target_time = datetime.strptime(time_value, "%Y-%m-%d %H:%M")
                    logger.info(f"解析指定時間成功: {target_time}")
                except ValueError:
                    logger.error(f"時間格式解析失敗: {time_value}")
                    self.reply_text("時間格式錯誤，將使用當前時間進行占卜。")
                    target_time = None
            
            # 執行占卜（關鍵：傳遞指定時間）
            divination_result = get_divination_result(self.db, user, gender, target_time)
            logger.info(f"占卜結果獲取完成，成功：{divination_result.get('success')}")
            
            if divination_result.get('success'):
                # 從占卜結果中獲取記錄 ID (不重複創建)
                record_id = divination_result.get('divination_id')
                logger.info(f"使用占卜結果中的記錄 ID: {record_id}")
                
                # 根據用戶等級設定 user_type
                user_type = "admin" if user.is_admin() else ("premium" if user.is_premium() else "free")
                
                # 生成占卜結果訊息 (使用全局變量)
                flex_messages = divination_flex_generator.generate_divination_messages(divination_result, user_type=user_type)
                
                if flex_messages:
                    logger.info("發送占卜結果")
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=self.reply_token,
                            messages=flex_messages
                        )
                    )
                    
                    # 如果是管理員，發送快速按鈕
                    if user.is_admin():
                        await self.send_admin_quick_buttons(record_id)
                else:
                    logger.error("生成占卜結果訊息失敗")
                    self.reply_text("占卜結果生成失敗，請稍後再試。")
            else:
                error_msg = divination_result.get('message', '占卜失敗')
                logger.error(f"占卜失敗: {error_msg}")
                self.reply_text(f"占卜失敗：{error_msg}")
                
        except Exception as e:
            logger.error(f"處理指定時間占卜執行失敗: {e}", exc_info=True)
            self.reply_text("占卜過程發生錯誤，請稍後再試。")


@router.post("/webhook-new", include_in_schema=False)
async def line_bot_webhook_new(request: Request, db: Session = Depends(get_db)):
    """全新 LINE Bot Webhook 端點"""
    try:
        # 解析請求
        signature = request.headers.get("X-Line-Signature")
        body = await request.body()
        events = parser.parse(body.decode(), signature)
        
    except InvalidSignatureError:
        logger.error("無效的 LINE Signature")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    except Exception as e:
        logger.error(f"解析 LINE 事件失敗: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="事件解析失敗")
    
    # 處理每個事件
    for event in events:
        handler = WebhookHandler()
        handler.db = db
        handler.user_id = event.source.user_id
        
        try:
            # 更新用戶活動時間
            await handler.update_user_activity(handler.user_id, db)
            
            if isinstance(event, FollowEvent):
                handler.reply_token = event.reply_token
                await handler.handle_follow_event()
                
            elif isinstance(event, UnfollowEvent):
                logger.info(f"用戶 {handler.user_id} 取消關注了機器人")
                
            elif isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                handler.reply_token = event.reply_token
                await handler.handle_text_message(event.message.text)
                
            elif isinstance(event, PostbackEvent):
                handler.reply_token = event.reply_token
                await handler.handle_postback_event(event.postback.data)
                
        except Exception as e:
            logger.error(f"處理事件時發生錯誤 (用戶: {handler.user_id}): {e}")
            logger.error(traceback.format_exc())
            
            # 嘗試回復錯誤訊息
            if hasattr(handler, 'reply_token') and handler.reply_token:
                try:
                    handler.reply_text("處理您的請求時發生錯誤，請稍後再試。")
                except:
                    pass
    
    return {"status": "ok"} 