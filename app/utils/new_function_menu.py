"""
全新功能選單生成器
- 免費會員：升級提示
- 付費會員：進階功能 Image Carousel
- 管理員：所有功能 Quick Reply
"""

import logging
from typing import Dict, Optional, Any, Union
from linebot.v3.messaging import (
    TemplateMessage, ImageCarouselTemplate, ImageCarouselColumn, 
    PostbackAction, TextMessage, QuickReply, QuickReplyItem
)

logger = logging.getLogger(__name__)

class NewFunctionMenuGenerator:
    """全新功能選單生成器"""
    
    def __init__(self):
        pass

    def generate_function_menu(self, user_stats: Dict[str, Any]) -> Optional[Union[TextMessage, TemplateMessage]]:
        """
        生成功能選單
        - 免費會員：升級提示
        - 付費會員：進階功能 Image Carousel  
        - 管理員：所有功能 Quick Reply
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            TextMessage 或 TemplateMessage 物件或 None
        """
        try:
            # 獲取用戶權限
            user_info = user_stats.get("user_info", {})
            membership_info = user_stats.get("membership_info", {})
            
            is_admin = user_info.get("is_admin", False)
            is_premium = membership_info.get("is_premium", False)
            
            # 免費會員：顯示升級提示
            if not is_premium and not is_admin:
                return TextMessage(
                    text="""💎 升級解鎖更多功能

🔮 基本功能：
Rich Menu 下方已提供基本功能
• 會員資訊
• 本週占卜  
• 使用說明

✨ 升級付費會員可解鎖：
• 💎 進階功能：大限運勢、小限運勢、流年運勢、流月運勢
• 🎯 專屬功能與更多占卜選項

📞 聯繫管理員升級會員，享受完整功能！"""
                )
            
            # 付費會員(非管理員)：直接顯示進階功能 Carousel
            if is_premium and not is_admin:
                return self._create_advanced_functions_carousel()
            
            # 管理員：顯示所有功能的快速回覆按鈕
            if is_admin:
                quick_reply_buttons = [
                    # 進階功能
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🌟 大限運勢",
                            data="function=daxian_fortune",
                            displayText="🌟 大限運勢"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🎯 小限運勢",
                            data="function=xiaoxian_fortune",
                            displayText="🎯 小限運勢"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="📅 流年運勢",
                            data="function=yearly_fortune",
                            displayText="📅 流年運勢"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🌙 流月運勢",
                            data="function=monthly_fortune",
                            displayText="🌙 流月運勢"
                        )
                    ),
                    # 管理員功能
                    QuickReplyItem(
                        action=PostbackAction(
                            label="⏰ 指定時間占卜",
                            data="admin_function=time_divination",
                            displayText="⏰ 指定時間占卜"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="📊 系統監控",
                            data="admin_function=system_monitor",
                            displayText="📊 系統監控"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="👥 用戶管理",
                            data="admin_function=user_management",
                            displayText="👥 用戶管理"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="⚙️ 選單管理",
                            data="admin_function=menu_management",
                            displayText="⚙️ 選單管理"
                        )
                    ),
                    # 測試功能
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🧪 測試免費",
                            data="test_function=test_free",
                            displayText="🧪 測試免費"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="💎 測試付費",
                            data="test_function=test_premium",
                            displayText="💎 測試付費"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="👑 回復管理員",
                            data="test_function=restore_admin",
                            displayText="👑 回復管理員"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="📋 檢查狀態",
                            data="test_function=check_status",
                            displayText="📋 檢查狀態"
                        )
                    )
                ]
                
                # 創建快速回覆
                quick_reply = QuickReply(items=quick_reply_buttons)
                
                return TextMessage(
                    text="👑 管理員功能選單\n\n📝 直接點擊下方按鈕執行功能",
                    quickReply=quick_reply
                )
            
        except Exception as e:
            logger.error(f"生成功能選單失敗: {e}", exc_info=True)
            return None

    def generate_category_menu(self, category: str, user_stats: Dict[str, Any]) -> Optional[TemplateMessage]:
        """
        生成特定分類的功能選單 (保留兼容性，實際上管理員已改用 Quick Reply)
        """
        try:
            user_info = user_stats.get("user_info", {})
            membership_info = user_stats.get("membership_info", {})
            
            is_admin = user_info.get("is_admin", False)
            is_premium = membership_info.get("is_premium", False)
            
            if category == "advanced_functions" and (is_premium or is_admin):
                return self._create_advanced_functions_carousel()
            else:
                logger.warning(f"無權限訪問分類: {category}")
                return None
                
        except Exception as e:
            logger.error(f"生成分類選單失敗: {e}", exc_info=True)
            return None

    def _create_advanced_functions_carousel(self) -> TemplateMessage:
        """創建進階功能的 Image Carousel"""
        columns = [
            ImageCarouselColumn(
                imageUrl="https://web-production-c5424.up.railway.app/static/2-1.png",
                action=PostbackAction(
                    data="function=daxian_fortune",
                    displayText="🌟 大限運勢"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://web-production-c5424.up.railway.app/static/2-2.png",
                action=PostbackAction(
                    data="function=xiaoxian_fortune",
                    displayText="🎯 小限運勢"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://web-production-c5424.up.railway.app/static/2-3.png",
                action=PostbackAction(
                    data="function=yearly_fortune",
                    displayText="📅 流年運勢"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://web-production-c5424.up.railway.app/static/2-4.png",
                action=PostbackAction(
                    data="function=monthly_fortune",
                    displayText="🌙 流月運勢"
                )
            )
        ]
        
        template = ImageCarouselTemplate(columns=columns)
        return TemplateMessage(
            altText="💎 進階功能選單",
            template=template
        )


# 全局實例
new_function_menu_generator = NewFunctionMenuGenerator()


def generate_new_function_menu(user_stats: Dict[str, Any]) -> Optional[Union[TextMessage, TemplateMessage]]:
    """
    生成新的功能選單
    
    Args:
        user_stats: 用戶統計資訊
        
    Returns:
        TextMessage 或 TemplateMessage 物件或 None
    """
    return new_function_menu_generator.generate_function_menu(user_stats) 