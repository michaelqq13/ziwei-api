"""
Flex Message Carousel 控制面板生成器
實現分頁式功能選單，支援權限控制和星空主題設計
每個分頁代表一個功能區，用戶可以左右滑動查看不同功能
"""

import json
import os
from typing import Dict, Any, List, Optional
import logging
from linebot.v3.messaging import FlexMessage, FlexContainer, FlexCarousel, FlexBubble, FlexBox, FlexText, FlexSeparator, FlexImage, PostbackAction
import time

logger = logging.getLogger(__name__)

class FlexCarouselControlPanelGenerator:
    """Flex Message Carousel 控制面板生成器 - 分頁式星空主題"""
    
    def __init__(self):
        self.panel_title = "🌌 星空功能選單"
        
        # 動態獲取伺服器地址
        self.server_url = self._get_server_url()
        
        # 星空主題色彩配置
        self.colors = {
            "primary": "#4A90E2",        # 星空藍
            "secondary": "#FFD700",      # 星光金
            "accent": "#9B59B6",         # 深紫色
            "premium": "#E67E22",        # 橙色
            "admin": "#E74C3C",          # 管理員紅
            "background": "#1A1A2E",     # 深夜藍
            "card_bg": "#16213E",        # 卡片背景
            "gradient_start": "#2C3E50", # 漸變起始
            "gradient_end": "#34495E",   # 漸變結束
            "text_primary": "#FFFFFF",   # 主文字白色
            "text_secondary": "#B0C4DE", # 次要文字淺藍
            "text_light": "#87CEEB",     # 淺藍色
            "border": "#2C3E50",         # 邊框顏色
            "disabled": "#6C7B7F",       # 禁用顏色
            "star_gold": "#FFD700",      # 星星金色
            "star_silver": "#C0C0C0"     # 星星銀色
        }
        
        # 快取破壞者，確保LINE每次都重新載入圖片
        cache_buster = f"?v={int(time.time())}"
        
        # 星空背景圖片 URL - 使用動態伺服器地址
        self.background_images = {
            "basic": f"{self.server_url}/assets/backgrounds/basic.jpg{cache_buster}",
            "premium": f"{self.server_url}/assets/backgrounds/premium.jpg{cache_buster}",
            "admin": f"{self.server_url}/assets/backgrounds/admin.jpg{cache_buster}"
        }
        
        # 如果無法存取 Unsplash，備用星空圖片 URL
        self.fallback_images = {
            "basic": "https://via.placeholder.com/800x400/1A1A2E/FFD700?text=✨+基本功能+✨",
            "premium": "https://via.placeholder.com/800x400/2C3E50/E67E22?text=🌟+進階功能+🌟", 
            "admin": "https://via.placeholder.com/800x400/8B0000/FFD700?text=👑+管理功能+👑"
        }
    
    def generate_carousel_control_panel(self, user_stats: Dict[str, Any]) -> Optional[FlexMessage]:
        """
        生成 Carousel 星空主題控制面板
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            FlexMessage 物件或 None
        """
        try:
            # 安全地獲取用戶權限資訊，處理 None 或無效輸入
            if not user_stats or not isinstance(user_stats, dict):
                user_stats = {}
            
            user_info = user_stats.get("user_info") or {}
            membership_info = user_stats.get("membership_info") or {}
            
            is_admin = user_info.get("is_admin", False) if isinstance(user_info, dict) else False
            is_premium = membership_info.get("is_premium", False) if isinstance(membership_info, dict) else False
            
            # 根據權限確定可訪問的分頁
            available_pages = self._get_available_pages(is_admin, is_premium)
            
            if not available_pages:
                logger.warning("用戶沒有可訪問的功能分頁")
                return None
            
            # 創建 carousel bubbles
            bubbles = []
            for page_type in available_pages:
                bubble = self._create_page_bubble(page_type, is_admin, is_premium)
                if bubble:
                    bubbles.append(bubble)
            
            if not bubbles:
                return None
            
            # 創建 FlexCarousel
            carousel = FlexCarousel(contents=bubbles)
            
            # 創建 FlexMessage
            flex_message = FlexMessage(
                alt_text="🌌 星空功能選單",
                contents=carousel
            )
            
            return flex_message
            
        except Exception as e:
            logger.error(f"生成 Carousel 控制面板失敗: {e}", exc_info=True)
            return None
    
    def _get_available_pages(self, is_admin: bool, is_premium: bool) -> List[str]:
        """
        根據用戶權限獲取可訪問的分頁
        
        Args:
            is_admin: 是否為管理員
            is_premium: 是否為付費會員
            
        Returns:
            可訪問的分頁列表
        """
        pages = ["basic"]  # 基本功能所有人都可以訪問
        
        if is_premium or is_admin:
            pages.append("premium")  # 付費會員和管理員可以訪問進階功能
            
        if is_admin:
            pages.append("admin")  # 管理員可以訪問管理功能
            pages.append("test")   # 管理員可以訪問測試功能
            
        return pages
    
    def _create_page_bubble(self, page_type: str, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """
        創建單個分頁的 bubble
        
        Args:
            page_type: 分頁類型 ('basic', 'premium', 'admin')
            is_admin: 是否為管理員
            is_premium: 是否為付費會員
            
        Returns:
            FlexBubble 物件
        """
        try:
            # 根據分頁類型設定內容
            if page_type == "basic":
                return self._create_basic_page(is_admin, is_premium)
            elif page_type == "premium":
                return self._create_premium_page(is_admin, is_premium)
            elif page_type == "admin":
                return self._create_admin_page(is_admin, is_premium)
            elif page_type == "test":
                return self._create_test_page(is_admin, is_premium)
            else:
                return None
        except Exception as e:
            logger.error(f"創建 {page_type} 分頁失敗: {e}")
            return None
    
    def _create_basic_page(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建基本功能分頁 - 調整為微型尺寸"""
        
        # 設定背景圖片和主題色彩
        background_image = self.background_images.get("basic", self.fallback_images["basic"])
        
        bubble = FlexBubble(
            size="micro",  # 改為微型尺寸，與太極十二宮一致
            hero=FlexBox(
                layout="vertical",
                contents=[
                    # 標題區域 - 縮小高度
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text="✨ 基本功能",
                                weight="bold",
                                size="lg",  # 縮小字體
                                color=self.colors["star_gold"],
                                align="center"
                            ),
                            FlexText(
                                text="Essential",
                                size="xs",  # 縮小副標題
                                color=self.colors["text_secondary"],
                                align="center",
                                margin="xs"
                            )
                        ],
                        spacing="none",
                        margin="sm"  # 縮小邊距
                    )
                ],
                paddingAll="12px",  # 縮小內邊距
                height="80px"  # 大幅縮小高度
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕 - 緊湊排列
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_compact_button("🔮", "占卜", "control_panel=basic_divination", True),
                            self._create_compact_button("👤", "會員", "action=show_member_info", True),
                            self._create_compact_button("📖", "說明", "action=show_instructions", True)
                        ],
                        spacing="xs"  # 緊湊間距
                    ),
                    # 頁面指示器
                    FlexText(
                        text="← 滑動 →" if (is_premium or is_admin) else "✨ 功能 ✨",
                        size="xxs",
                        color=self.colors["text_light"],
                        align="center",
                        margin="sm"
                    )
                ],
                spacing="sm",
                paddingAll="12px"  # 縮小內邊距
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                }
            }
        )
        
        return bubble

    def _create_premium_page(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建付費功能分頁 - 調整為微型尺寸"""
        
        # 設定背景圖片
        background_image = self.background_images.get("premium", self.fallback_images["premium"])
        
        bubble = FlexBubble(
            size="micro",  # 微型尺寸
            hero=FlexBox(
                layout="vertical",
                contents=[
                    # 標題區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text="🌟 進階功能",
                                weight="bold",
                                size="lg",
                                color=self.colors["premium"],
                                align="center"
                            ),
                            FlexText(
                                text="Premium",
                                size="xs",
                                color=self.colors["text_secondary"],
                                align="center",
                                margin="xs"
                            )
                        ],
                        spacing="none",
                        margin="sm"
                    )
                ],
                paddingAll="12px",
                height="80px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_compact_button("🌍", "流年", "control_panel=yearly_fortune", is_premium or is_admin),
                            self._create_compact_button("🌙", "流月", "control_panel=monthly_fortune", is_premium or is_admin),
                            self._create_compact_button("🪐", "流日", "control_panel=daily_fortune", is_premium or is_admin),
                            self._create_compact_button("💎", "升級", "control_panel=member_upgrade", True)
                        ],
                        spacing="xs"
                    ),
                    # 頁面指示器
                    FlexText(
                        text="← 滑動 →" if is_admin else "💎 升級",
                        size="xxs",
                        color=self.colors["premium"] if not (is_premium or is_admin) else self.colors["text_light"],
                        align="center",
                        margin="sm"
                    )
                ],
                spacing="sm",
                paddingAll="12px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                }
            }
        )
        
        return bubble

    def _create_admin_page(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建管理員功能分頁 - 調整為微型尺寸"""
        
        # 設定背景圖片
        background_image = self.background_images.get("admin", self.fallback_images["admin"])
        
        bubble = FlexBubble(
            size="micro",  # 微型尺寸
            hero=FlexBox(
                layout="vertical",
                contents=[
                    # 標題區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text="👑 管理功能",
                                weight="bold",
                                size="lg",
                                color=self.colors["admin"],
                                align="center"
                            ),
                            FlexText(
                                text="Admin",
                                size="xs",
                                color=self.colors["text_secondary"],
                                align="center",
                                margin="xs"
                            )
                        ],
                        spacing="none",
                        margin="sm"
                    )
                ],
                paddingAll="12px",
                height="80px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_compact_button("⏰", "時間占卜", "admin_action=time_divination_start", is_admin),
                            self._create_compact_button("📊", "用戶統計", "admin_action=user_stats", is_admin),
                            self._create_compact_button("🖥️", "系統監控", "admin_action=system_status", is_admin),
                            self._create_compact_button("⚙️", "選單管理", "admin_action=menu_management", is_admin)
                        ],
                        spacing="xs"
                    ),
                    # 頁面指示器
                    FlexText(
                        text="← 滑動返回 →",
                        size="xxs",
                        color=self.colors["text_light"],
                        align="center",
                        margin="sm"
                    )
                ],
                spacing="sm",
                paddingAll="12px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                }
            }
        )
        
        return bubble

    def _create_test_page(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建測試功能分頁 - 調整為微型尺寸"""
        
        # 設定背景圖片
        background_image = self.background_images.get("admin", self.fallback_images["admin"]) # 使用管理員背景圖片
        
        bubble = FlexBubble(
            size="micro",  # 微型尺寸
            hero=FlexBox(
                layout="vertical",
                contents=[
                    # 標題區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text="🧪 測試功能",
                                weight="bold",
                                size="lg",
                                color=self.colors["admin"], # 使用管理員顏色
                                align="center"
                            ),
                            FlexText(
                                text="Test",
                                size="xs",
                                color=self.colors["text_secondary"],
                                align="center",
                                margin="xs"
                            )
                        ],
                        spacing="none",
                        margin="sm"
                    )
                ],
                paddingAll="12px",
                height="80px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_compact_button("👤", "測試免費", "test_mode=free", is_admin),
                            self._create_compact_button("💎", "測試付費", "test_mode=premium", is_admin),
                            self._create_compact_button("👑", "恢復管理員", "test_mode=admin", is_admin),
                            self._create_compact_button("📊", "查看狀態", "test_mode=status", is_admin)
                        ],
                        spacing="xs"
                    ),
                    # 頁面指示器
                    FlexText(
                        text="← 滑動返回 →",
                        size="xxs",
                        color=self.colors["text_light"],
                        align="center",
                        margin="sm"
                    )
                ],
                spacing="sm",
                paddingAll="12px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                }
            }
        )
        
        return bubble

    def _create_compact_button(self, icon: str, title: str, action_data: str, is_enabled: bool) -> FlexBox:
        """創建緊湊型功能按鈕 - 適合微型bubble"""
        
        # 根據啟用狀態設定顏色
        if is_enabled:
            text_color = self.colors["text_primary"]
            icon_color = self.colors["star_gold"]
            border_color = self.colors["star_gold"]
        else:
            text_color = self.colors["disabled"]
            icon_color = self.colors["disabled"]
            border_color = self.colors["disabled"]
        
        return FlexBox(
            layout="horizontal",
            contents=[
                # 圖標
                FlexText(
                    text=icon,
                    size="md",
                    color=icon_color,
                    flex=0,
                    weight="bold"
                ),
                # 標題
                FlexText(
                    text=title,
                    weight="bold",
                    size="sm",
                    color=text_color,
                    flex=1,
                    margin="sm"
                )
            ],
            paddingAll="8px",  # 緊湊內邊距
            borderWidth="1px",
            borderColor=border_color,
            action=PostbackAction(
                data=action_data,
                displayText=title
            ) if is_enabled else None,
            margin="xs"
        )

    def _create_function_button(self, icon: str, title: str, description: str, action_data: str, is_enabled: bool) -> FlexBox:
        """創建單一功能按鈕 - 保留原版功能"""
        
        # 根據啟用狀態設定顏色
        if is_enabled:
            text_color = self.colors["text_primary"]
            icon_color = self.colors["star_gold"]
            border_color = self.colors["star_gold"]
            stars = "⭐⭐⭐"
        else:
            text_color = self.colors["disabled"]
            icon_color = self.colors["disabled"]
            border_color = self.colors["disabled"]
            stars = "🔒🔒🔒"
        
        return FlexBox(
            layout="vertical",
            contents=[
                # 主按鈕區域
                FlexBox(
                    layout="horizontal",
                    contents=[
                        # 圖標區域
                        FlexBox(
                            layout="vertical",
                            contents=[
                                FlexText(
                                    text=icon,
                                    size="lg",
                                    color=icon_color,
                                    align="center",
                                    weight="bold"
                                ),
                                FlexText(
                                    text=stars,
                                    size="xs",
                                    color=icon_color,
                                    align="center",
                                    margin="xs"
                                )
                            ],
                            flex=1,
                            justify="center",
                            align_items="center"
                        ),
                        # 文字說明區域
                        FlexBox(
                            layout="vertical",
                            contents=[
                                FlexText(
                                    text=title,
                                    weight="bold",
                                    size="md",
                                    color=text_color,
                                    flex_shrink=0
                                ),
                                FlexText(
                                    text=description,
                                    size="xs",
                                    color=self.colors["text_secondary"] if is_enabled else self.colors["disabled"],
                                    wrap=True,
                                    margin="xs"
                                )
                            ],
                            flex=3,
                            justify="center"
                        )
                    ],
                    paddingAll="16px",
                    borderWidth="1px",
                    borderColor=border_color,
                    action=PostbackAction(
                        data=action_data,
                        displayText=title
                    ) if is_enabled else None
                ),
                
                # 底部裝飾線（模擬陰影效果）
                FlexBox(
                    layout="vertical",
                    contents=[],
                    height="2px",
                    margin="none"
                )
            ],
            spacing="none",
            margin="sm"
        )
    
    def _create_page_footer(self, page_indicator: str, instruction: str) -> FlexBox:
        """創建分頁底部區域"""
        return FlexBox(
            layout="vertical",
            contents=[
                FlexSeparator(color=self.colors["border"], margin="lg"),
                FlexBox(
                    layout="horizontal", 
                    contents=[
                        FlexText(
                            text=page_indicator,
                            size="xs",
                            color=self.colors["star_gold"],
                            flex=0,
                            weight="bold"
                        ),
                        FlexText(
                            text=instruction,
                            size="xs",
                            color=self.colors["text_light"],
                            flex=1,
                            align="end"
                        )
                    ],
                    margin="md"
                )
            ]
        )

    def _get_server_url(self) -> str:
        """
        動態獲取伺服器 URL
        優先使用 BASE_URL 環境變數
        """
        # 優先從 BASE_URL 環境變數獲取
        base_url = os.getenv("BASE_URL")
        if base_url:
            return base_url.rstrip('/')

        # 備用：檢查是否設定了自定義 SERVER_URL
        server_url = os.getenv("SERVER_URL")
        if server_url:
            return server_url.rstrip('/')
            
        # 預設為本地開發環境
        return "http://localhost:8000"

# 創建全局實例
flex_carousel_panel_generator = FlexCarouselControlPanelGenerator()

def generate_carousel_control_panel(user_stats: Dict[str, Any]) -> Optional[FlexMessage]:
    """
    生成 Carousel 控制面板的便捷函數
    
    Args:
        user_stats: 用戶統計資訊
        
    Returns:
        FlexMessage 或 None
    """
    return flex_carousel_panel_generator.generate_carousel_control_panel(user_stats) 