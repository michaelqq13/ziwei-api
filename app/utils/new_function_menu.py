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
        """創建基本功能分頁 - 測試方案2: 內建生成SVG背景"""
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
                paddingAll="10px",
                spacing="xs",
                contents=[
                    FlexText(
                        text="✨ 基本功能 ✨",
                        size="md",
                        weight="bold",
                        color=self.colors["star_gold"],
                        align="center"
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
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="xs", color=self.colors["star_gold"]))
            
            # 組合所有內容
            all_contents = [header_box]
            all_contents.extend(function_boxes)
            
            return FlexBubble(
                size="nano",
                hero=FlexBox(
                    layout="vertical",
                    height="40px",
                    paddingAll="0px",
                    spacing="none",
                    contents=[]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="10px",
                    spacing="xs",
                    contents=all_contents
                ),
                styles={
                    "hero": {
                        "backgroundImage": self.generated_backgrounds.get("basic"),  # 方案2: SVG背景
                        "backgroundSize": "cover",
                        "backgroundPosition": "center"
                    },
                    "body": {
                        "backgroundColor": "#1A1A2E"  # 深夜藍背景
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建基本功能分頁失敗: {e}")
            return None

    def _create_advanced_function_page(self, is_admin: bool, is_premium: bool) -> Optional[FlexBubble]:
        """創建進階功能分頁 - 測試方案3: 簡單外部圖片"""
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
                paddingAll="10px",
                spacing="xs",
                contents=[
                    FlexText(
                        text="💎 進階功能 💎",
                        size="md",
                        weight="bold",
                        color=self.colors["star_gold"],
                        align="center"
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
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="xs", color=self.colors["star_gold"]))
            
            # 組合所有內容
            all_contents = [header_box]
            all_contents.extend(function_boxes)
            
            return FlexBubble(
                size="nano",
                hero=FlexBox(
                    layout="vertical",
                    height="40px",
                    paddingAll="0px",
                    spacing="none",
                    contents=[]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="10px",
                    spacing="xs",
                    contents=all_contents
                ),
                styles={
                    "hero": {
                        "backgroundImage": self.simple_backgrounds.get("advanced"),  # 方案3: 簡單圖片
                        "backgroundSize": "cover",
                        "backgroundPosition": "center"
                    },
                    "body": {
                        "backgroundColor": "#2C1810"  # 深棕色背景
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建進階功能分頁失敗: {e}")
            return None

    def _create_admin_function_page(self) -> Optional[FlexBubble]:
        """創建管理員功能分頁 - 測試方案1: 優化的外部星空圖片"""
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
                paddingAll="10px",
                spacing="xs",
                contents=[
                    FlexText(
                        text="👑 管理功能 👑",
                        size="md",
                        weight="bold",
                        color=self.colors["star_gold"],
                        align="center"
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
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="xs", color=self.colors["star_gold"]))
            
            # 組合所有內容
            all_contents = [header_box]
            all_contents.extend(function_boxes)
            
            return FlexBubble(
                size="nano",
                hero=FlexBox(
                    layout="vertical",
                    height="40px",
                    paddingAll="0px",
                    spacing="none",
                    contents=[]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="10px",
                    spacing="xs",
                    contents=all_contents
                ),
                styles={
                    "hero": {
                        "backgroundImage": self.background_images_v1.get("admin"),  # 方案1: 優化星空圖片
                        "backgroundSize": "cover",
                        "backgroundPosition": "center"
                    },
                    "body": {
                        "backgroundColor": "#2E1A1A"  # 深紅色背景
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"創建管理員功能分頁失敗: {e}")
            return None

    def _create_test_function_page(self) -> Optional[FlexBubble]:
        """創建測試功能分頁 - 測試方案4: 原始方案作為備用"""
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
            
            # 創建星空裝飾標題
            header_box = FlexBox(
                layout="vertical",
                paddingAll="10px",
                spacing="xs",
                contents=[
                    FlexText(
                        text="✨🌟⭐ 測試功能 ⭐🌟✨",
                        size="md",
                        weight="bold",
                        color=self.colors["star_gold"],
                        align="center"
                    ),
                    FlexText(
                        text="🌌 🌟 ✨ 🌟 🌌",
                        size="xs",
                        color=self.colors["text_light"],
                        align="center"
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
                function_boxes.insert((i + 1) * 2 - 1, FlexSeparator(margin="xs", color=self.colors["star_gold"]))
            
            # 組合所有內容
            all_contents = [header_box]
            all_contents.extend(function_boxes)
            
            return FlexBubble(
                size="nano",
                hero=FlexBox(
                    layout="vertical",
                    height="40px",
                    paddingAll="0px",
                    spacing="none",
                    contents=[]
                ),
                body=FlexBox(
                    layout="vertical",
                    paddingAll="10px",
                    spacing="xs",
                    contents=all_contents
                ),
                styles={
                    "hero": {
                        "backgroundImage": self.fallback_images.get("test"),  # 方案4: 備用方案
                        "backgroundSize": "cover",
                        "backgroundPosition": "center"
                    },
                    "body": {
                        "backgroundColor": "#0F1419"  # 非常深的夜空色
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