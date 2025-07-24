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

    def _create_basic_function_page(self, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """創建基本功能分頁"""
        try:
            # 基本功能按鈕配置
            functions = [
                {
                    "emoji": "🔮",
                    "title": "本週占卜",
                    "subtitle": "即時觸機占卜",
                    "data": "function=weekly_divination",
                    "enabled": True
                },
                {
                    "emoji": "👤",
                    "title": "會員資訊",
                    "subtitle": "查看個人資訊",
                    "data": "function=member_info",
                    "enabled": True
                },
                {
                    "emoji": "📖",
                    "title": "使用說明",
                    "subtitle": "功能操作指南",
                    "data": "function=instructions",
                    "enabled": True
                }
            ]
            
            # 創建標題 Box
            header_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                # backgroundColor="rgba(26, 26, 46, 0.8)",  # 移除半透明遮罩
                contents=[
                    FlexText(
                        text="✨ 基本功能",
                        size="xl",
                        weight="bold",
                        color=self.colors["text_primary"],
                        align="center"
                    ),
                    FlexText(
                        text="所有用戶都可使用的基礎功能",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        wrap=True
                    )
                ]
            )
            
            # 創建功能按鈕
            function_boxes = []
            for func in functions:
                button_box = self._create_function_button(
                    emoji=func["emoji"],
                    title=func["title"],
                    subtitle=func["subtitle"],
                    data=func["data"],
                    enabled=func["enabled"],
                    color=self.colors["primary"]
                )
                if button_box:
                    function_boxes.append(button_box)
            
            # 分隔符號
            for i in range(len(function_boxes) - 1):
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="md", color=self.colors["text_secondary"]))
            
            # 主內容 Box
            body_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                contents=function_boxes
            )
            
            # 底部資訊
            footer_box = FlexBox(
                layout="vertical",
                paddingAll="15px",
                spacing="sm",
                contents=[
                    FlexText(
                        text="💫 星空紫微斗數",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center"
                    ),
                    FlexText(
                        text="基礎功能 - 免費使用",
                        size="xxs",
                        color=self.colors["text_secondary"],
                        align="center"
                    )
                ]
            )
            
            return FlexBubble(
                size="kilo",
                hero=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    # backgroundColor="rgba(26, 26, 46, 0.8)",  # 移除
                    contents=[
                        FlexText(
                            text=" ",
                            size="xs"
                        )
                    ]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[header_box, body_box, footer_box]
                ),
                styles={
                    "hero": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    },
                    "body": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建基本功能分頁失敗: {e}")
            return None

    def _create_advanced_function_page(self, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """創建進階功能分頁"""
        try:
            # 進階功能按鈕配置
            functions = [
                {
                    "emoji": "🌟",
                    "title": "大限運勢",
                    "subtitle": "十年大運分析",
                    "data": "function=daxian_fortune",
                    "enabled": is_premium or is_admin
                },
                {
                    "emoji": "🎯",
                    "title": "小限運勢", 
                    "subtitle": "年度運勢詳解",
                    "data": "function=xiaoxian_fortune",
                    "enabled": is_premium or is_admin
                },
                {
                    "emoji": "📅",
                    "title": "流年運勢",
                    "subtitle": "當年運勢走向",
                    "data": "function=yearly_fortune",
                    "enabled": is_premium or is_admin
                },
                {
                    "emoji": "🌙",
                    "title": "流月運勢",
                    "subtitle": "月度運勢指引",
                    "data": "function=monthly_fortune",
                    "enabled": is_premium or is_admin
                }
            ]
            
            # 創建標題 Box
            header_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                # backgroundColor="rgba(155, 89, 182, 0.8)",  # 移除紫色半透明遮罩
                contents=[
                    FlexText(
                        text="💎 進階功能",
                        size="xl",
                        weight="bold",
                        color=self.colors["text_primary"],
                        align="center"
                    ),
                    FlexText(
                        text="付費會員專屬進階功能",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        wrap=True
                    )
                ]
            )
            
            # 創建功能按鈕
            function_boxes = []
            for func in functions:
                button_box = self._create_function_button(
                    emoji=func["emoji"],
                    title=func["title"],
                    subtitle=func["subtitle"],
                    data=func["data"],
                    enabled=func["enabled"],
                    color=self.colors["accent"]
                )
                if button_box:
                    function_boxes.append(button_box)
            
            # 分隔符號
            for i in range(len(function_boxes) - 1):
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="md", color=self.colors["text_secondary"]))
            
            # 主內容 Box
            body_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                contents=function_boxes
            )
            
            # 底部資訊
            footer_box = FlexBox(
                layout="vertical",
                paddingAll="15px",
                spacing="sm",
                contents=[
                    FlexText(
                        text="💎 進階運勢分析",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center"
                    ),
                    FlexText(
                        text="付費會員專屬",
                        size="xxs",
                        color=self.colors["accent"],
                        align="center"
                    )
                ]
            )
            
            return FlexBubble(
                size="kilo",
                hero=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[
                        FlexText(
                            text=" ",
                            size="xs"
                        )
                    ]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[header_box, body_box, footer_box]
                ),
                styles={
                    "hero": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    },
                    "body": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建進階功能分頁失敗: {e}")
            return None

    def _create_admin_function_page(self) -> Optional[FlexBubble]:
        """創建管理員功能分頁"""
        try:
            # 管理員功能按鈕配置
            functions = [
                {
                    "emoji": "⏰",
                    "title": "指定時間占卜",
                    "subtitle": "自定義時間占卜",
                    "data": "admin_function=time_divination",
                    "enabled": True
                },
                {
                    "emoji": "📊",
                    "title": "系統監控",
                    "subtitle": "系統狀態監控",
                    "data": "admin_function=system_monitor",
                    "enabled": True
                },
                {
                    "emoji": "👥",
                    "title": "用戶管理",
                    "subtitle": "管理用戶資料",
                    "data": "admin_function=user_management",
                    "enabled": True
                },
                {
                    "emoji": "⚙️",
                    "title": "選單管理",
                    "subtitle": "功能選單設定",
                    "data": "admin_function=menu_management",
                    "enabled": True
                }
            ]
            
            # 創建標題 Box
            header_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                # backgroundColor="rgba(231, 76, 60, 0.8)",  # 移除紅色半透明遮罩
                contents=[
                    FlexText(
                        text="👑 管理功能",
                        size="xl",
                        weight="bold",
                        color=self.colors["text_primary"],
                        align="center"
                    ),
                    FlexText(
                        text="系統管理員專用功能",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        wrap=True
                    )
                ]
            )
            
            # 創建功能按鈕
            function_boxes = []
            for func in functions:
                button_box = self._create_function_button(
                    emoji=func["emoji"],
                    title=func["title"],
                    subtitle=func["subtitle"],
                    data=func["data"],
                    enabled=func["enabled"],
                    color=self.colors["admin"]
                )
                if button_box:
                    function_boxes.append(button_box)
            
            # 分隔符號
            for i in range(len(function_boxes) - 1):
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="md", color=self.colors["text_secondary"]))
            
            # 主內容 Box
            body_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                contents=function_boxes
            )
            
            # 底部資訊
            footer_box = FlexBox(
                layout="vertical",
                paddingAll="15px",
                spacing="sm",
                contents=[
                    FlexText(
                        text="👑 系統管理功能",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center"
                    ),
                    FlexText(
                        text="管理員專屬",
                        size="xxs",
                        color=self.colors["admin"],
                        align="center"
                    )
                ]
            )
            
            return FlexBubble(
                size="kilo",
                hero=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[
                        FlexText(
                            text=" ",
                            size="xs"
                        )
                    ]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[header_box, body_box, footer_box]
                ),
                styles={
                    "hero": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    },
                    "body": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建管理員功能分頁失敗: {e}")
            return None

    def _create_test_function_page(self) -> Optional[FlexBubble]:
        """創建測試功能分頁"""
        try:
            # 測試功能按鈕配置
            functions = [
                {
                    "emoji": "🧪",
                    "title": "測試免費",
                    "subtitle": "切換免費會員身份",
                    "data": "test_function=test_free",
                    "enabled": True
                },
                {
                    "emoji": "💎",
                    "title": "測試付費",
                    "subtitle": "切換付費會員身份",
                    "data": "test_function=test_premium",
                    "enabled": True
                },
                {
                    "emoji": "👑",
                    "title": "回復管理員",
                    "subtitle": "恢復管理員身份",
                    "data": "test_function=restore_admin",
                    "enabled": True
                },
                {
                    "emoji": "📋",
                    "title": "檢查狀態",
                    "subtitle": "查看當前測試狀態",
                    "data": "test_function=check_status",
                    "enabled": True
                }
            ]
            
            # 創建標題 Box
            header_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                # backgroundColor="rgba(46, 204, 113, 0.8)",  # 移除綠色半透明遮罩
                contents=[
                    FlexText(
                        text="🧪 測試功能",
                        size="xl",
                        weight="bold",
                        color=self.colors["text_primary"],
                        align="center"
                    ),
                    FlexText(
                        text="權限測試與身份切換",
                        size="sm",
                        color=self.colors["text_secondary"],
                        align="center",
                        wrap=True
                    )
                ]
            )
            
            # 創建功能按鈕
            function_boxes = []
            for func in functions:
                button_box = self._create_function_button(
                    emoji=func["emoji"],
                    title=func["title"],
                    subtitle=func["subtitle"],
                    data=func["data"],
                    enabled=func["enabled"],
                    color=self.colors["test"]
                )
                if button_box:
                    function_boxes.append(button_box)
            
            # 分隔符號
            for i in range(len(function_boxes) - 1):
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="md", color=self.colors["text_secondary"]))
            
            # 主內容 Box
            body_box = FlexBox(
                layout="vertical",
                paddingAll="20px",
                spacing="md",
                contents=function_boxes
            )
            
            # 底部資訊
            footer_box = FlexBox(
                layout="vertical",
                paddingAll="15px",
                spacing="sm",
                contents=[
                    FlexText(
                        text="🧪 權限測試功能",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center"
                    ),
                    FlexText(
                        text="身份切換測試",
                        size="xxs",
                        color=self.colors["test"],
                        align="center"
                    )
                ]
            )
            
            return FlexBubble(
                size="kilo",
                hero=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[
                        FlexText(
                            text=" ",
                            size="xs"
                        )
                    ]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="0px",
                    spacing="none",
                    contents=[header_box, body_box, footer_box]
                ),
                styles={
                    "hero": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    },
                    "body": {
                        # "backgroundColor": "#FFFFFF"  # 移除
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建測試功能分頁失敗: {e}")
            return None

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
                                size="xl",
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
                                size="md",
                                color=text_color,
                                wrap=True
                            ),
                            FlexText(
                                text=subtitle,
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
                # backgroundColor=bg_color,  # 移除半透明背景
                borderWidth="1px",
                borderColor=border_color,
                cornerRadius="8px",
                paddingAll="12px",
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