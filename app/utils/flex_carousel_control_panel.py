"""
Flex Message Carousel 控制面板生成器
實現分頁式功能選單，支援權限控制和星空主題設計
每個分頁代表一個功能區，用戶可以左右滑動查看不同功能
"""

import json
from typing import Dict, Any, List, Optional
import logging
from linebot.v3.messaging import FlexMessage, FlexContainer, FlexCarousel, FlexBubble, FlexBox, FlexText, FlexSeparator, FlexImage, PostbackAction

logger = logging.getLogger(__name__)

class FlexCarouselControlPanelGenerator:
    """Flex Message Carousel 控制面板生成器 - 分頁式星空主題"""
    
    def __init__(self):
        self.panel_title = "🌌 星空功能選單"
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
        
        # 星空背景圖片 URL (可以放在靜態資源中)
        self.background_images = {
            "basic": "https://via.placeholder.com/800x400/1A1A2E/FFD700?text=✨+基本功能",
            "premium": "https://via.placeholder.com/800x400/2C3E50/E67E22?text=🌟+進階功能", 
            "admin": "https://via.placeholder.com/800x400/8B0000/FFD700?text=👑+管理功能"
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
            
        return pages
    
    def _create_page_bubble(self, page_type: str, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """
        創建分頁 bubble
        
        Args:
            page_type: 分頁類型 ("basic", "premium", "admin")
            is_admin: 是否為管理員
            is_premium: 是否為付費會員
            
        Returns:
            FlexBubble 物件或 None
        """
        try:
            if page_type == "basic":
                return self._create_basic_page_bubble()
            elif page_type == "premium":
                return self._create_premium_page_bubble(is_admin, is_premium)
            elif page_type == "admin":
                return self._create_admin_page_bubble()
            else:
                return None
                
        except Exception as e:
            logger.error(f"創建 {page_type} 分頁失敗: {e}")
            return None
    
    def _create_basic_page_bubble(self) -> FlexBubble:
        """創建基本功能分頁"""
        return FlexBubble(
            size="giga",
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 標題區域
                    self._create_page_header("🔮 基本功能", "免費使用・觸機占卜", self.colors["primary"]),
                    
                    FlexSeparator(margin="lg", color=self.colors["border"]),
                    
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_star_button(
                                "🔮 本週占卜",
                                "根據當下時間進行觸機占卜",
                                "control_panel=basic_divination",
                                self.colors["primary"],
                                "⭐⭐⭐"
                            ),
                            
                            self._create_star_button(
                                "👤 會員資訊",
                                "查看個人資料和占卜記錄",
                                "action=show_member_info", 
                                self.colors["accent"],
                                "⭐⭐"
                            ),
                            
                            self._create_star_button(
                                "📖 使用說明",
                                "了解如何使用紫微斗數占卜",
                                "action=show_instructions",
                                self.colors["secondary"],
                                "⭐"
                            )
                        ],
                        spacing="md",
                        margin="lg"
                    ),
                    
                    # 分頁指示器和說明
                    self._create_page_footer("1/3", "左右滑動查看更多功能"),
                ],
                spacing="sm",
                paddingAll="lg"
            ),
            styles={
                "body": {"backgroundColor": self.colors["background"]}
            }
        )
    
    def _create_premium_page_bubble(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建進階功能分頁"""
        # 根據權限決定按鈕是否可用
        can_access = is_premium or is_admin
        
        # 創建按鈕列表
        buttons = [
            self._create_star_button(
                "🌍 流年運勢",
                "年度整體運勢分析" if can_access else "🔒 需要付費會員解鎖",
                "control_panel=yearly_fortune" if can_access else "control_panel=upgrade_required",
                self.colors["premium"] if can_access else self.colors["disabled"],
                "⭐⭐⭐⭐" if can_access else "🔒🔒🔒🔒",
                disabled=not can_access
            ),
            
            self._create_star_button(
                "🌙 流月運勢", 
                "月度運勢變化分析" if can_access else "🔒 需要付費會員解鎖",
                "control_panel=monthly_fortune" if can_access else "control_panel=upgrade_required",
                self.colors["accent"] if can_access else self.colors["disabled"],
                "⭐⭐⭐⭐" if can_access else "🔒🔒🔒🔒",
                disabled=not can_access
            ),
            
            self._create_star_button(
                "🪐 流日運勢",
                "每日運勢詳細分析" if can_access else "🔒 需要付費會員解鎖", 
                "control_panel=daily_fortune" if can_access else "control_panel=upgrade_required",
                self.colors["primary"] if can_access else self.colors["disabled"],
                "⭐⭐⭐⭐" if can_access else "🔒🔒🔒🔒",
                disabled=not can_access
            )
        ]
        
        # 會員升級按鈕（非管理員才顯示）
        if not is_admin:
            upgrade_button = self._create_star_button(
                "💎 會員升級",
                "升級享受更多專業功能" if not can_access else "管理會員狀態",
                "control_panel=member_upgrade",
                self.colors["star_gold"],
                "💫💫💫💫💫"
            )
            if upgrade_button:
                buttons.append(upgrade_button)
        
        return FlexBubble(
            size="giga", 
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 標題區域
                    self._create_page_header(
                        "🌟 進階功能", 
                        "付費會員專享・深度分析" if can_access else "🔒 需要付費會員",
                        self.colors["premium"] if can_access else self.colors["disabled"]
                    ),
                    
                    FlexSeparator(margin="lg", color=self.colors["border"]),
                    
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=buttons,
                        spacing="md",
                        margin="lg"
                    ),
                    
                    # 分頁指示器和說明
                    self._create_page_footer("2/3", "左右滑動查看其他功能"),
                ],
                spacing="sm",
                paddingAll="lg"
            ),
            styles={
                "body": {"backgroundColor": self.colors["background"]}
            }
        )
    
    def _create_admin_page_bubble(self) -> FlexBubble:
        """創建管理員功能分頁"""
        return FlexBubble(
            size="giga",
            body=FlexBox(
                layout="vertical", 
                contents=[
                    # 標題區域
                    self._create_page_header("👑 管理功能", "管理員專用・系統控制", self.colors["admin"]),
                    
                    FlexSeparator(margin="lg", color=self.colors["border"]),
                    
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_star_button(
                                "⏰ 指定時間占卜",
                                "回溯特定時間點進行占卜",
                                "admin_action=time_divination_start",
                                self.colors["admin"],
                                "👑👑👑👑👑"
                            ),
                            
                            self._create_star_button(
                                "📊 用戶數據統計",
                                "查看系統使用情況和統計",
                                "admin_action=user_stats",
                                self.colors["accent"],
                                "👑👑👑👑"
                            ),
                            
                            self._create_star_button(
                                "🖥️ 系統狀態監控",
                                "監控系統運行狀態",
                                "admin_action=system_status", 
                                self.colors["primary"],
                                "👑👑👑"
                            ),
                            
                            self._create_star_button(
                                "⚙️ 選單管理",
                                "管理 Rich Menu 和功能設定",
                                "admin_action=menu_management",
                                self.colors["secondary"],
                                "👑👑"
                            )
                        ],
                        spacing="md",
                        margin="lg"
                    ),
                    
                    # 分頁指示器和說明
                    self._create_page_footer("3/3", "管理員專屬功能面板"),
                ],
                spacing="sm",
                paddingAll="lg"
            ),
            styles={
                "body": {"backgroundColor": self.colors["background"]}
            }
        )
    
    def _create_page_header(self, title: str, subtitle: str, color: str) -> FlexBox:
        """創建分頁標題區域"""
        return FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text=title,
                    weight="bold",
                    size="xl",
                    color=color,
                    align="center"
                ),
                FlexText(
                    text=subtitle,
                    size="sm",
                    color=self.colors["text_secondary"],
                    align="center",
                    margin="xs"
                )
            ],
            backgroundColor=self.colors["card_bg"],
            cornerRadius="md",
            paddingAll="md"
        )
    
    def _create_star_button(self, title: str, description: str, action_data: str, 
                           color: str, stars: str, disabled: bool = False) -> Optional[FlexBox]:
        """創建星空主題功能按鈕"""
        if disabled:
            return FlexBox(
                layout="vertical",
                contents=[
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text=title,
                                weight="bold",
                                size="md",
                                color=self.colors["text_light"],
                                flex=1
                            ),
                            FlexText(
                                text=stars,
                                size="sm",
                                color=self.colors["disabled"],
                                flex=0,
                                align="end"
                            )
                        ],
                        backgroundColor=self.colors["disabled"],
                        cornerRadius="md",
                        paddingAll="md"
                    ),
                    FlexText(
                        text=description,
                        size="xs",
                        color=self.colors["text_light"],
                        wrap=True,
                        margin="xs"
                    )
                ],
                spacing="none",
                margin="sm"
            )
        else:
            return FlexBox(
                layout="vertical",
                contents=[
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text=title,
                                weight="bold",
                                size="md",
                                color=self.colors["text_primary"],
                                flex=1
                            ),
                            FlexText(
                                text=stars,
                                size="sm",
                                color=self.colors["star_gold"],
                                flex=0,
                                align="end"
                            )
                        ],
                        backgroundColor=color,
                        cornerRadius="md",
                        paddingAll="md",
                        action=PostbackAction(
                            data=action_data,
                            displayText=title
                        )
                    ),
                    FlexText(
                        text=description,
                        size="xs",
                        color=self.colors["text_secondary"],
                        wrap=True,
                        margin="xs"
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