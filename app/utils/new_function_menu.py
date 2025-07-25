"""
全新功能選單生成器
四個 Flex Message 分類：基本功能、進階功能、管理員功能、測試功能
星空背景搭配懸浮半透明按鈕設計
"""

import logging
from typing import Dict, List, Optional, Any
from linebot.v3.messaging import (
    FlexMessage, FlexCarousel, FlexBubble, FlexBox, FlexText,
    FlexSeparator, PostbackAction, FlexImage, TemplateMessage, 
    ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    TextMessage, QuickReply, QuickReplyItem
)
import time

logger = logging.getLogger(__name__)

class NewFunctionMenuGenerator:
    """全新功能選單生成器"""
    
    def __init__(self):
        # 星空主題色彩配置
        self.colors = {
            "primary": "#4A90E2",        # 星空藍
            "secondary": "#FFD700",      # 星光金
            "accent": "#9B59B6",         # 深紫色
            "premium": "#E67E22",        # 橙色
            "admin": "#E74C3C",          # 管理員紅
            "test": "#2ECC71",           # 測試綠
            "background": "#1A1A2E",     # 深夜藍
            "text_primary": "#FFFFFF",   # 主文字白色
            "text_secondary": "#B0C4DE", # 次要文字淺藍
            "text_light": "#87CEEB",     # 淺藍色
            "star_gold": "#FFD700",      # 星星金色
            "disabled": "#6C7B7F"        # 禁用顏色
        }
        
        # 嘗試多種星空背景方案
        # 方案1: 直接的星空圖片URL (不使用快取破壞者)
        self.background_images_v1 = {
            "basic": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=200&fit=crop&auto=format",
            "advanced": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=400&h=200&fit=crop&auto=format", 
            "admin": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=400&h=200&fit=crop&auto=format",
            "test": "https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&h=200&fit=crop&auto=format"
        }
        
        # 方案2: 內建生成的漸變圖案
        self.generated_backgrounds = {
            "basic": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9InN0YXJzIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMEYwRjIzIi8+PHN0b3Agb2Zmc2V0PSI1MCUiIHN0b3AtY29sb3I9IiMxQTFBMkUiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxNjIxM0UiLz48L3JhZGlhbEdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI3N0YXJzKSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmaWxsPSIjRkZENzAwIiBmb250LXNpemU9IjI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+4pyoIOKcqCDimIU8L3RleHQ+PC9zdmc+",
            "advanced": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9InB1cnBsZSIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzJDMTgxMCIvPjxzdG9wIG9mZnNldD0iNTAlIiBzdG9wLWNvbG9yPSIjOUI1OUI2Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMUExMDJFIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNwdXJwbGUpIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZpbGw9IiNGRkQ3MDAiIGZvbnQtc2l6ZT0iMjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7wn5KOIPCfjpEg4pyoPC90ZXh0Pjwvc3ZnPg==",
            "admin": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9InJlZCI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzJFMUExQSIvPjxzdG9wIG9mZnNldD0iNTAlIiBzdG9wLWNvbG9yPSIjRTc0QzNDIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMUEwQTBBIi8+PC9yYWRpYWxHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNyZWQpIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZpbGw9IiNGRkQ3MDAiIGZvbnQtc2l6ZT0iMjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7wn5GRIPCfkqkg4pyoPC90ZXh0Pjwvc3ZnPg==",
            "test": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImdyZWVuIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMEYxNDE5Ii8+PHN0b3Agb2Zmc2V0PSI1MCUiIHN0b3AtY29sb3I9IiMyRUNDNzEiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMxQTJFMUEiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyZWVuKSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmaWxsPSIjRkZENzAwIiBmb250LXNpemU9IjIwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+8J+ngqog4pyoIOKcqDwvdGV4dD48L3N2Zz4="
        }
        
        # 方案3: 更簡單的外部圖片
        self.simple_backgrounds = {
            "basic": "https://via.placeholder.com/400x200/1A1A2E/FFD700?text=✨+星空+✨",
            "advanced": "https://via.placeholder.com/400x200/9B59B6/FFD700?text=💎+進階+💎", 
            "admin": "https://via.placeholder.com/400x200/E74C3C/FFD700?text=👑+管理+👑",
            "test": "https://via.placeholder.com/400x200/2ECC71/FFD700?text=🧪+測試+🧪"
        }
        
        # 方案4: 保留原始方案作為備用
        cache_buster = f"?v={int(time.time())}"
        self.background_images = {
            "basic": f"https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400&q=80{cache_buster}",
            "advanced": f"https://images.unsplash.com/photo-1502134249126-9f3755a50d78?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400&q=80{cache_buster}",
            "admin": f"https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400&q=80{cache_buster}",
            "test": f"https://images.unsplash.com/photo-1464802686167-b939a6910659?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400&q=80{cache_buster}"
        }
        
        # 備用背景圖片
        self.fallback_images = {
            "basic": "https://via.placeholder.com/800x400/4A90E2/FFD700?text=✨+基本功能+✨",
            "advanced": "https://via.placeholder.com/800x400/9B59B6/FFD700?text=💎+進階功能+💎",
            "admin": "https://via.placeholder.com/800x400/E74C3C/FFD700?text=👑+管理功能+👑",
            "test": "https://via.placeholder.com/800x400/2ECC71/FFD700?text=🧪+測試功能+🧪"
        }

    def generate_function_menu(self, user_stats: Dict[str, Any]) -> Optional[TextMessage]:
        """
        生成功能選單 Quick Reply (第一層：分類選擇)
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            TextMessage 物件或 None
        """
        try:
            # 獲取用戶權限
            user_info = user_stats.get("user_info", {})
            membership_info = user_stats.get("membership_info", {})
            
            is_admin = user_info.get("is_admin", False)
            is_premium = membership_info.get("is_premium", False)
            
            # 創建快速回覆按鈕
            quick_reply_buttons = []
            
            # 1. 基本功能 - 所有用戶都能看到
            quick_reply_buttons.append(
                QuickReplyItem(
                    action=PostbackAction(
                        label="🔮 基本功能",
                        data="category=basic_functions",
                        displayText="🔮 基本功能"
                    )
                )
            )
            
            # 2. 進階功能 - 付費會員和管理員可見
            if is_premium or is_admin:
                quick_reply_buttons.append(
                    QuickReplyItem(
                        action=PostbackAction(
                            label="💎 進階功能",
                            data="category=advanced_functions", 
                            displayText="💎 進階功能"
                        )
                    )
                )
            
            # 3. 管理員功能 - 僅管理員可見
            if is_admin:
                quick_reply_buttons.append(
                    QuickReplyItem(
                        action=PostbackAction(
                            label="👑 管理功能",
                            data="category=admin_functions",
                            displayText="👑 管理功能"
                        )
                    )
                )
                
                # 4. 測試功能 - 僅管理員可見
                quick_reply_buttons.append(
                    QuickReplyItem(
                        action=PostbackAction(
                            label="🧪 測試功能",
                            data="category=test_functions",
                            displayText="🧪 測試功能"
                        )
                    )
                )
            
            if not quick_reply_buttons:
                logger.warning("沒有可用的功能分類")
                return None
            
            # 創建快速回覆
            quick_reply = QuickReply(items=quick_reply_buttons)
            
            return TextMessage(
                text="✨ 請選擇功能分類 ✨\n\n選擇後將顯示該分類的詳細功能選單",
                quickReply=quick_reply
            )
            
        except Exception as e:
            logger.error(f"生成功能選單失敗: {e}", exc_info=True)
            return None

    def generate_category_menu(self, category: str, user_stats: Dict[str, Any]) -> Optional[TemplateMessage]:
        """
        生成特定分類的功能選單 Image Carousel (第二層：詳細功能)
        
        Args:
            category: 功能分類 (basic_functions, advanced_functions, admin_functions, test_functions)
            user_stats: 用戶統計資訊
            
        Returns:
            TemplateMessage 物件或 None
        """
        try:
            user_info = user_stats.get("user_info", {})
            membership_info = user_stats.get("membership_info", {})
            
            is_admin = user_info.get("is_admin", False)
            is_premium = membership_info.get("is_premium", False)
            
            if category == "basic_functions":
                return self._create_basic_functions_carousel()
            elif category == "advanced_functions" and (is_premium or is_admin):
                return self._create_advanced_functions_carousel()
            elif category == "admin_functions" and is_admin:
                return self._create_admin_functions_carousel()
            elif category == "test_functions" and is_admin:
                return self._create_test_functions_carousel()
            else:
                logger.warning(f"無權限訪問分類: {category}")
                return None
                
        except Exception as e:
            logger.error(f"生成分類選單失敗: {e}", exc_info=True)
            return None

    def _create_basic_function_page(self, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """創建基本功能分頁 - Hero底圖+Body透明疊加方案"""
        try:
            # 創建標題文字層 (發光效果)
            title_text = FlexText(
                text="✨ 基本功能 ✨",
                size="md",
                weight="bold",
                color="#FFD700",  # 星光金
                align="center"
            )
            
            # 創建功能按鈕 (疊加在圖片上)
            function_buttons = FlexBox(
                layout="horizontal",
                spacing="sm",
                contents=[
                    FlexBox(
                        layout="vertical",
                        flex=1,
                        contents=[
                            FlexText(text="🔮", size="lg", align="center", color="#FFD700"),
                            FlexText(text="本週占卜", size="xs", align="center", color="#FFFFFF", weight="bold")
                        ],
                        action=PostbackAction(data="function=weekly_divination", displayText="本週占卜"),
                        paddingAll="8px",
                        cornerRadius="8px",
                        borderWidth="1px",
                        borderColor="#FFD700"
                    ),
                    FlexBox(
                        layout="vertical", 
                        flex=1,
                        contents=[
                            FlexText(text="👤", size="lg", align="center", color="#FFD700"),
                            FlexText(text="會員資訊", size="xs", align="center", color="#FFFFFF", weight="bold")
                        ],
                        action=PostbackAction(data="function=member_info", displayText="會員資訊"),
                        paddingAll="8px", 
                        cornerRadius="8px",
                        borderWidth="1px",
                        borderColor="#FFD700"
                    ),
                    FlexBox(
                        layout="vertical",
                        flex=1, 
                        contents=[
                            FlexText(text="📖", size="lg", align="center", color="#FFD700"),
                            FlexText(text="使用說明", size="xs", align="center", color="#FFFFFF", weight="bold")
                        ],
                        action=PostbackAction(data="function=instructions", displayText="使用說明"),
                        paddingAll="8px",
                        cornerRadius="8px",
                        borderWidth="1px",
                        borderColor="#FFD700"
                    )
                ]
            )
            
            # 組合標題和按鈕
            content_overlay = FlexBox(
                layout="vertical",
                spacing="md",
                paddingAll="15px",
                contents=[title_text, function_buttons]
            )
            
            return FlexBubble(
                size="nano",
                # Hero 作為底層星空背景
                hero=FlexImage(
                    url="https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=200&fit=crop&auto=format",
                    size="full",
                    aspectRatio="20:10",
                    aspectMode="cover"
                ),
                # Body 作為透明暗色疊加層
                body=content_overlay,
                styles={
                    "body": {
                        "backgroundColor": "#00000080"  # 半透明黑色疊加
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建基本功能分頁失敗: {e}")
            return None

    def _create_advanced_function_page(self, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """創建進階功能分頁 - 圖片背景方案"""
        try:
            # 創建標題文字層
            title_text = FlexText(
                text="💎 進階功能 💎",
                size="md",
                weight="bold",
                color=self.colors["star_gold"],
                align="center"
            )
            
            # 創建功能按鈕 (疊加在圖片上)
            function_buttons = FlexBox(
                layout="vertical",
                spacing="xs",
                contents=[
                    FlexBox(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="🌟", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="大限運勢", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="function=daxian_fortune", displayText="大限運勢") if (is_premium or is_admin) else None,
                                paddingAll="6px",
                                cornerRadius="6px"
                            ),
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="🎯", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="小限運勢", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="function=xiaoxian_fortune", displayText="小限運勢") if (is_premium or is_admin) else None,
                                paddingAll="6px",
                                cornerRadius="6px"
                            )
                        ]
                    ),
                    FlexBox(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="📅", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="流年運勢", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="function=yearly_fortune", displayText="流年運勢") if (is_premium or is_admin) else None,
                                paddingAll="6px",
                                cornerRadius="6px"
                            ),
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="🌙", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="流月運勢", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="function=monthly_fortune", displayText="流月運勢") if (is_premium or is_admin) else None,
                                paddingAll="6px",
                                cornerRadius="6px"
                            )
                        ]
                    )
                ]
            )
            
            # 組合標題和按鈕
            content_overlay = FlexBox(
                layout="vertical",
                spacing="sm",
                paddingAll="12px",
                backgroundColor="#2C1810",  # 深棕色背景
                cornerRadius="12px",  # 圓角浮層效果
                contents=[title_text, function_buttons]
            )
            
            return FlexBubble(
                size="nano",
                # 使用 hero 作為星空背景圖片
                hero=FlexImage(
                    url="https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=400&h=200&fit=crop&auto=format",
                    size="full",
                    aspectRatio="20:10",
                    aspectMode="cover"
                ),
                # body 作為內容疊加層
                body=content_overlay
                # 移除 styles，因為 LINE API 不支援 rgba backgroundColor
            )
            
        except Exception as e:
            logger.error(f"創建進階功能分頁失敗: {e}")
            return None

    def _create_admin_function_page(self) -> Optional[FlexBubble]:
        """創建管理員功能分頁 - 圖片背景方案"""
        try:
            # 創建標題文字層
            title_text = FlexText(
                text="👑 管理功能 👑",
                size="md",
                weight="bold",
                color=self.colors["star_gold"],
                align="center"
            )
            
            # 創建功能按鈕 (疊加在圖片上)
            function_buttons = FlexBox(
                layout="vertical",
                spacing="xs",
                contents=[
                    FlexBox(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="⏰", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="指定時間占卜", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="admin_function=time_divination", displayText="指定時間占卜"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            ),
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="📊", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="系統監控", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="admin_function=system_monitor", displayText="系統監控"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            )
                        ]
                    ),
                    FlexBox(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="👥", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="用戶管理", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="admin_function=user_management", displayText="用戶管理"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            ),
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="⚙️", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="選單管理", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="admin_function=menu_management", displayText="選單管理"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            )
                        ]
                    )
                ]
            )
            
            # 組合標題和按鈕
            content_overlay = FlexBox(
                layout="vertical",
                spacing="sm",
                paddingAll="12px",
                backgroundColor="#2E1A1A",  # 深紅色背景
                cornerRadius="12px",  # 圓角浮層效果
                contents=[title_text, function_buttons]
            )
            
            return FlexBubble(
                size="nano",
                # 使用 hero 作為星空背景圖片
                hero=FlexImage(
                    url="https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=400&h=200&fit=crop&auto=format",
                    size="full",
                    aspectRatio="20:10",
                    aspectMode="cover"
                ),
                # body 作為內容疊加層
                body=content_overlay
            )
            
        except Exception as e:
            logger.error(f"創建管理員功能分頁失敗: {e}")
            return None

    def _create_test_function_page(self) -> Optional[FlexBubble]:
        """創建測試功能分頁 - 圖片背景方案"""
        try:
            # 創建標題文字層
            title_text = FlexText(
                text="🧪 測試功能 🧪",
                size="md",
                weight="bold",
                color=self.colors["star_gold"],
                align="center"
            )
            
            # 創建功能按鈕 (疊加在圖片上)
            function_buttons = FlexBox(
                layout="vertical",
                spacing="xs",
                contents=[
                    FlexBox(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="🧪", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="測試免費", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="test_function=test_free", displayText="測試免費"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            ),
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="💎", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="測試付費", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="test_function=test_premium", displayText="測試付費"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            )
                        ]
                    ),
                    FlexBox(
                        layout="horizontal",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="👑", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="回復管理員", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="test_function=restore_admin", displayText="回復管理員"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            ),
                            FlexBox(
                                layout="vertical",
                                flex=1,
                                contents=[
                                    FlexText(text="📋", size="md", align="center", color=self.colors["star_gold"]),
                                    FlexText(text="檢查狀態", size="xxs", align="center", color=self.colors["text_primary"], weight="bold")
                                ],
                                action=PostbackAction(data="test_function=check_status", displayText="檢查狀態"),
                                paddingAll="6px",
                                cornerRadius="6px"
                            )
                        ]
                    )
                ]
            )
            
            # 組合標題和按鈕
            content_overlay = FlexBox(
                layout="vertical",
                spacing="sm",
                paddingAll="12px",
                backgroundColor="#0F1419",  # 非常深的夜空色
                cornerRadius="12px",  # 圓角浮層效果
                contents=[title_text, function_buttons]
            )
            
            return FlexBubble(
                size="nano",
                # 使用 hero 作為星空背景圖片
                hero=FlexImage(
                    url="https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&h=200&fit=crop&auto=format",
                    size="full",
                    aspectRatio="20:10",
                    aspectMode="cover"
                ),
                # body 作為內容疊加層
                body=content_overlay
            )
            
        except Exception as e:
            logger.error(f"創建測試功能分頁失敗: {e}")
            return None

    def _create_basic_functions_carousel(self) -> TemplateMessage:
        """創建基本功能的 Image Carousel"""
        columns = [
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="function=weekly_divination",
                    displayText="🔮 本週占卜"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="function=member_info", 
                    displayText="👤 會員資訊"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="function=instructions",
                    displayText="📖 使用說明"
                )
            )
        ]
        
        template = ImageCarouselTemplate(columns=columns)
        return TemplateMessage(
            altText="🔮 基本功能選單",
            template=template
        )

    def _create_advanced_functions_carousel(self) -> TemplateMessage:
        """創建進階功能的 Image Carousel"""
        columns = [
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="function=daxian_fortune",
                    displayText="🌟 大限運勢"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="function=xiaoxian_fortune",
                    displayText="🎯 小限運勢"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="function=yearly_fortune",
                    displayText="📅 流年運勢"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1500375592092-40eb2168fd21?w=400&h=240&fit=crop&auto=format",
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

    def _create_admin_functions_carousel(self) -> TemplateMessage:
        """創建管理員功能的 Image Carousel"""
        columns = [
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="admin_function=time_divination",
                    displayText="⏰ 指定時間占卜"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="admin_function=system_monitor",
                    displayText="📊 系統監控"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="admin_function=user_management",
                    displayText="👥 用戶管理"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="admin_function=menu_management",
                    displayText="⚙️ 選單管理"
                )
            )
        ]
        
        template = ImageCarouselTemplate(columns=columns)
        return TemplateMessage(
            altText="👑 管理功能選單",
            template=template
        )

    def _create_test_functions_carousel(self) -> TemplateMessage:
        """創建測試功能的 Image Carousel"""
        columns = [
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="test_function=test_free",
                    displayText="🧪 測試免費"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="test_function=test_premium",
                    displayText="💎 測試付費"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="test_function=restore_admin",
                    displayText="👑 回復管理員"
                )
            ),
            ImageCarouselColumn(
                imageUrl="https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=400&h=240&fit=crop&auto=format",
                action=PostbackAction(
                    data="test_function=check_status",
                    displayText="📋 檢查狀態"
                )
            )
        ]
        
        template = ImageCarouselTemplate(columns=columns)
        return TemplateMessage(
            altText="🧪 測試功能選單",
            template=template
        )

    def _create_function_button(self, emoji: str, title: str, subtitle: str, data: str, enabled: bool, color: str) -> Optional[FlexBox]:
        """創建功能按鈕"""
        try:
            # 根據啟用狀態設定顏色
            if enabled:
                text_color = self.colors["text_primary"]
                icon_color = color
                border_color = color
                desc_color = self.colors["text_secondary"]
            else:
                text_color = self.colors["disabled"]
                icon_color = self.colors["disabled"]
                border_color = self.colors["disabled"]
                desc_color = self.colors["disabled"]
            
            return FlexBox(
                layout="horizontal",
                contents=[
                    # 圖標區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text=emoji,
                                size="md",  # 再減小圖標尺寸
                                color=icon_color,
                                align="center",
                                weight="bold"
                            )
                        ],
                        flex=1,
                        justifyContent="center",
                        alignItems="center"
                    ),
                    # 文字說明區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text=title,
                                weight="bold",
                                size="xs",  # 再減小標題尺寸
                                color=text_color,
                                wrap=True
                            ),
                            FlexText(
                                text=subtitle,
                                size="xxs",  # 再減小副標題尺寸
                                color=desc_color,
                                wrap=True,
                                margin="none"  # 移除 margin
                            )
                        ],
                        flex=3,
                        justifyContent="center"
                    )
                ],
                borderWidth="1px",
                borderColor=border_color,
                cornerRadius="4px",  # 再減小圓角
                paddingAll="6px",  # 再減小內邊距
                action=PostbackAction(
                    data=data,
                    displayText=title
                ) if enabled else None
            )
            
        except Exception as e:
            logger.error(f"創建功能按鈕失敗: {e}")
            return None


# 全局實例
new_function_menu_generator = NewFunctionMenuGenerator()


def generate_new_function_menu(user_stats: Dict[str, Any]) -> Optional[FlexMessage]:
    """
    生成新的功能選單
    
    Args:
        user_stats: 用戶統計資訊
        
    Returns:
        FlexMessage 物件或 None
    """
    return new_function_menu_generator.generate_function_menu(user_stats) 