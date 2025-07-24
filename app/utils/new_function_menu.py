"""
全新功能選單生成器
四個 Flex Message 分類：基本功能、進階功能、管理員功能、測試功能
星空背景搭配懸浮半透明按鈕設計
"""

import logging
from typing import Dict, List, Optional, Any
from linebot.v3.messaging import (
    FlexMessage, FlexCarousel, FlexBubble, FlexBox, FlexText,
    FlexSeparator, PostbackAction
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
        
        # 星空背景圖片配置 - 快取破壞者
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

    def generate_function_menu(self, user_stats: Dict[str, Any]) -> Optional[FlexMessage]:
        """
        生成功能選單 Carousel
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            FlexMessage 物件或 None
        """
        try:
            # 獲取用戶權限
            user_info = user_stats.get("user_info", {})
            membership_info = user_stats.get("membership_info", {})
            
            is_admin = user_info.get("is_admin", False)
            is_premium = membership_info.get("is_premium", False)
            
            # 創建所有分頁
            bubbles = []
            
            # 1. 基本功能 - 所有用戶都能看到
            basic_bubble = self._create_basic_function_page(is_admin, is_premium)
            if basic_bubble:
                bubbles.append(basic_bubble)
            
            # 2. 進階功能 - 付費會員和管理員可見
            if is_premium or is_admin:
                advanced_bubble = self._create_advanced_function_page(is_admin, is_premium)
                if advanced_bubble:
                    bubbles.append(advanced_bubble)
            
            # 3. 管理員功能 - 僅管理員可見
            if is_admin:
                admin_bubble = self._create_admin_function_page()
                if admin_bubble:
                    bubbles.append(admin_bubble)
                
                # 4. 測試功能 - 僅管理員可見
                test_bubble = self._create_test_function_page()
                if test_bubble:
                    bubbles.append(test_bubble)
            
            if not bubbles:
                logger.warning("沒有可用的功能分頁")
                return None
            
            # 創建 Carousel
            carousel = FlexCarousel(contents=bubbles)
            
            return FlexMessage(
                alt_text="🌌 功能選單",
                contents=carousel
            )
            
        except Exception as e:
            logger.error(f"生成功能選單失敗: {e}", exc_info=True)
            return None

    def _create_basic_function_page(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建基本功能分頁"""
        
        background_image = self.background_images.get("basic", self.fallback_images["basic"])
        
        return FlexBubble(
            size="mega",
            hero=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="✨ 基本功能",
                        weight="bold",
                        size="xl",
                        color=self.colors["star_gold"],
                        align="center"
                    ),
                    FlexText(
                        text="Essential Functions",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        margin="xs"
                    )
                ],
                backgroundColor="rgba(26, 26, 46, 0.8)",  # 半透明遮罩
                paddingAll="20px",
                height="120px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_function_button(
                                "🔮", "本週占卜", "觸機占卜，當下時間運勢",
                                "function=weekly_divination", True
                            ),
                            self._create_function_button(
                                "👤", "會員資訊", "查看個人使用記錄和權限",
                                "function=member_info", True
                            ),
                            self._create_function_button(
                                "📖", "使用說明", "功能介紹和操作指南",
                                "function=instructions", True
                            )
                        ],
                        spacing="md"
                    ),
                    
                    # 頁面指示器
                    FlexText(
                        text="← 滑動查看更多功能 →" if (is_premium or is_admin) else "✨ 基本功能完整版 ✨",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center",
                        margin="lg"
                    )
                ],
                spacing="lg",
                paddingAll="20px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                },
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        )

    def _create_advanced_function_page(self, is_admin: bool, is_premium: bool) -> FlexBubble:
        """創建進階功能分頁"""
        
        background_image = self.background_images.get("advanced", self.fallback_images["advanced"])
        
        return FlexBubble(
            size="mega",
            hero=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="💎 進階功能",
                        weight="bold",
                        size="xl",
                        color=self.colors["star_gold"],
                        align="center"
                    ),
                    FlexText(
                        text="Premium Functions",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        margin="xs"
                    )
                ],
                backgroundColor="rgba(155, 89, 182, 0.8)",  # 紫色半透明遮罩
                paddingAll="20px",
                height="120px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_function_button(
                                "🌟", "大限運勢", "十年大運流轉分析",
                                "function=daxian_fortune", is_premium or is_admin
                            ),
                            self._create_function_button(
                                "🌙", "小限運勢", "年度小限運勢查詢",
                                "function=xiaoxian_fortune", is_premium or is_admin
                            ),
                            self._create_function_button(
                                "🌍", "流年運勢", "當年整體運勢分析",
                                "function=yearly_fortune", is_premium or is_admin
                            ),
                            self._create_function_button(
                                "🗓️", "流月運勢", "當月詳細運勢解析",
                                "function=monthly_fortune", is_premium or is_admin
                            )
                        ],
                        spacing="md"
                    ),
                    
                    # 頁面指示器
                    FlexText(
                        text="← 滑動查看管理功能 →" if is_admin else "💎 付費會員專享",
                        size="xs",
                        color=self.colors["premium"] if not (is_premium or is_admin) else self.colors["text_light"],
                        align="center",
                        margin="lg"
                    )
                ],
                spacing="lg",
                paddingAll="20px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                },
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        )

    def _create_admin_function_page(self) -> FlexBubble:
        """創建管理員功能分頁"""
        
        background_image = self.background_images.get("admin", self.fallback_images["admin"])
        
        return FlexBubble(
            size="mega",
            hero=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="👑 管理功能",
                        weight="bold",
                        size="xl",
                        color=self.colors["star_gold"],
                        align="center"
                    ),
                    FlexText(
                        text="Administrator Functions",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        margin="xs"
                    )
                ],
                backgroundColor="rgba(231, 76, 60, 0.8)",  # 紅色半透明遮罩
                paddingAll="20px",
                height="120px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_function_button(
                                "⏰", "指定時間占卜", "指定特定時間進行占卜",
                                "admin_function=time_divination", True
                            ),
                            self._create_function_button(
                                "📊", "系統監控", "查看系統運行狀態",
                                "admin_function=system_monitor", True
                            ),
                            self._create_function_button(
                                "👥", "用戶管理", "管理用戶權限和資料",
                                "admin_function=user_management", True
                            ),
                            self._create_function_button(
                                "⚙️", "選單管理", "管理 Rich Menu 和功能",
                                "admin_function=menu_management", True
                            )
                        ],
                        spacing="md"
                    ),
                    
                    # 頁面指示器
                    FlexText(
                        text="← 滑動查看測試功能 →",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center",
                        margin="lg"
                    )
                ],
                spacing="lg",
                paddingAll="20px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                },
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        )

    def _create_test_function_page(self) -> FlexBubble:
        """創建測試功能分頁"""
        
        background_image = self.background_images.get("test", self.fallback_images["test"])
        
        return FlexBubble(
            size="mega",
            hero=FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="🧪 測試功能",
                        weight="bold",
                        size="xl",
                        color=self.colors["star_gold"],
                        align="center"
                    ),
                    FlexText(
                        text="Testing Functions",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        margin="xs"
                    )
                ],
                backgroundColor="rgba(46, 204, 113, 0.8)",  # 綠色半透明遮罩
                paddingAll="20px",
                height="120px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 功能按鈕區域
                    FlexBox(
                        layout="vertical",
                        contents=[
                            self._create_function_button(
                                "🆓", "測試免費", "測試免費用戶功能",
                                "test_function=test_free", True
                            ),
                            self._create_function_button(
                                "💎", "測試付費", "測試付費會員功能",
                                "test_function=test_premium", True
                            ),
                            self._create_function_button(
                                "🔧", "回復管理員", "恢復管理員權限狀態",
                                "test_function=restore_admin", True
                            ),
                            self._create_function_button(
                                "🩺", "檢查狀態", "檢查系統和用戶狀態",
                                "test_function=check_status", True
                            )
                        ],
                        spacing="md"
                    ),
                    
                    # 頁面指示器
                    FlexText(
                        text="← 滑動返回基本功能 →",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center",
                        margin="lg"
                    )
                ],
                spacing="lg",
                paddingAll="20px"
            ),
            styles={
                "hero": {
                    "backgroundImage": background_image,
                    "backgroundSize": "cover",
                    "backgroundPosition": "center"
                },
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        )

    def _create_function_button(self, icon: str, title: str, description: str, action_data: str, is_enabled: bool) -> FlexBox:
        """創建懸浮半透明功能按鈕"""
        
        # 根據啟用狀態設定顏色
        if is_enabled:
            text_color = self.colors["text_primary"]
            icon_color = self.colors["star_gold"]
            border_color = self.colors["star_gold"]
            bg_color = "rgba(74, 144, 226, 0.15)"  # 半透明藍色背景
            desc_color = "#666666"
        else:
            text_color = self.colors["disabled"]
            icon_color = self.colors["disabled"]
            border_color = self.colors["disabled"]
            bg_color = "rgba(108, 123, 127, 0.1)"  # 半透明灰色背景
            desc_color = self.colors["disabled"]
        
        return FlexBox(
            layout="vertical",
            contents=[
                # 主按鈕區域 - 懸浮效果
                FlexBox(
                    layout="horizontal",
                    contents=[
                        # 圖標區域
                        FlexBox(
                            layout="vertical",
                            contents=[
                                FlexText(
                                    text=icon,
                                    size="xl",
                                    color=icon_color,
                                    align="center",
                                    weight="bold"
                                ),
                                FlexText(
                                    text="⭐⭐⭐" if is_enabled else "🔒🔒🔒",
                                    size="xs",
                                    color=icon_color,
                                    align="center",
                                    margin="xs"
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
                                    size="lg",
                                    color=text_color,
                                    wrap=True
                                ),
                                FlexText(
                                    text=description,
                                    size="sm",
                                    color=desc_color,
                                    wrap=True,
                                    margin="xs"
                                )
                            ],
                            flex=3,
                            justifyContent="center"
                        )
                    ],
                    backgroundColor=bg_color,  # 半透明背景
                    borderWidth="2px",
                    borderColor=border_color,
                    cornerRadius="12px",
                    paddingAll="16px",
                    action=PostbackAction(
                        data=action_data,
                        displayText=title
                    ) if is_enabled else None
                ),
                # 底部陰影效果
                FlexBox(
                    layout="vertical",
                    contents=[],
                    height="3px",
                    backgroundColor="rgba(0, 0, 0, 0.1)",  # 陰影效果
                    cornerRadius="0px 0px 8px 8px",
                    margin="none"
                )
            ],
            spacing="none"
        )


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