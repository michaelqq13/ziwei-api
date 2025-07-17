"""
Flex Message 控制面板生成器
用於生成智能的功能控制面板，根據用戶權限顯示不同功能
使用星空背景主題設計
"""

import json
from typing import Dict, Any, List, Optional
import logging
from linebot.v3.messaging import FlexMessage, FlexContainer

logger = logging.getLogger(__name__)

class FlexControlPanelGenerator:
    """Flex Message 控制面板生成器 - 星空主題"""
    
    def __init__(self):
        self.panel_title = "🌌 星空功能面板"
        # 使用星空主題色彩
        self.colors = {
            "primary": "#4A90E2",      # 星空藍
            "secondary": "#FFD700",    # 星光金
            "accent": "#9B59B6",       # 深紫色
            "premium": "#E67E22",      # 橙色
            "admin": "#E74C3C",        # 管理員紅
            "background": "#1A1A2E",   # 深夜藍
            "card_bg": "#16213E",      # 卡片背景
            "text_primary": "#FFFFFF", # 主文字白色
            "text_secondary": "#B0C4DE", # 次要文字淺藍
            "text_light": "#87CEEB",   # 淺藍色
            "border": "#2C3E50"        # 邊框顏色
        }
        
        # 星空背景圖片 - 與 carousel 保持一致
        self.background_images = {
            "panel": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1040&h=600&q=80"  # 深藍星空
        }
        
        # 備用背景圖片
        self.fallback_images = {
            "panel": "https://via.placeholder.com/1040x600/1A1A2E/FFD700?text=🌌+功能面板+🌌"
        }
    
    def generate_control_panel(self, user_stats: Dict[str, Any]) -> Optional[FlexMessage]:
        """
        生成星空主題控制面板
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            FlexMessage 物件或 None
        """
        try:
            is_admin = user_stats.get("user_info", {}).get("is_admin", False)
            is_premium = user_stats.get("membership_info", {}).get("is_premium", False)
            
            # 構建星空主題控制面板
            bubble_dict = {
                "type": "bubble",
                "size": "giga",
                "header": self._create_starry_header(is_admin, is_premium),
                "body": self._create_starry_body(is_admin, is_premium),
                "footer": self._create_starry_footer(),
                "styles": {
                    "header": {
                        "backgroundColor": self.colors["background"]
                    },
                    "body": {
                        "backgroundColor": self.colors["background"]
                    },
                    "footer": {
                        "backgroundColor": self.colors["background"]
                    }
                }
            }
            
            # 將字典轉換為 FlexContainer
            flex_container = FlexContainer.from_dict(bubble_dict)
            
            # 創建 FlexMessage
            flex_message = FlexMessage(
                alt_text="🌌 星空功能面板",
                contents=flex_container
            )
            
            return flex_message
            
        except Exception as e:
            logger.error(f"生成星空控制面板失敗: {e}", exc_info=True)
            return None
    
    def _create_header(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建控制面板標題區域"""
        user_type = "管理員" if is_admin else ("付費會員" if is_premium else "免費會員")
        user_color = self.colors["admin"] if is_admin else (self.colors["premium"] if is_premium else self.colors["primary"])
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🌌 星空功能面板",
                    "weight": "bold",
                    "size": "xl",
                    "color": self.colors["text_primary"],
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": f"✨ {user_type}",
                    "size": "sm",
                    "color": user_color,
                    "align": "center",
                    "margin": "xs"
                }
            ],
            "paddingBottom": "md"
        }
    
    def _create_starry_header(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建星空主題頭部 - 添加背景圖片支援"""
        
        # 根據用戶等級設定標題和顏色
        if is_admin:
            title = "👑 管理員面板"
            title_color = "#FFD700"
        elif is_premium:
            title = "💎 付費會員面板"
            title_color = "#9B59B6"
        else:
            title = "✨ 功能面板"
            title_color = "#4A90E2"
        
        # 選擇背景圖片
        background_image = self.background_images.get("panel", self.fallback_images["panel"])
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "xxl",
                    "color": title_color,
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "🌌 Star Control Panel",
                    "size": "sm",
                    "color": self.colors["text_secondary"],
                    "align": "center",
                    "margin": "xs"
                }
            ],
            "backgroundColor": "#1A1A2ECC",  # 半透明深藍遮罩
            "paddingAll": "20px",
            "backgroundImage": background_image,
            "backgroundSize": "cover",
            "backgroundPosition": "center"
        }
    
    def _create_starry_body(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建星空主題控制面板主體內容"""
        # 基本功能按鈕
        basic_buttons = []
        basic_buttons.append(
            self._create_starry_button(
                "🔮",
                "本週占卜",
                "control_panel=basic_divination",
                True,
                False,
                False
            )
        )
        
        # 進階功能按鈕
        advanced_buttons = []
        advanced_buttons.append(
            self._create_starry_button(
                "🌍",
                "流年運勢" if (is_admin or is_premium) else "🔒 需要付費會員",
                "control_panel=yearly_fortune",
                (is_admin or is_premium),
                is_premium,
                is_admin
            )
        )
        advanced_buttons.append(
            self._create_starry_button(
                "🌙",
                "流月運勢" if (is_admin or is_premium) else "🔒 需要付費會員",
                "control_panel=monthly_fortune",
                (is_admin or is_premium),
                is_premium,
                is_admin
            )
        )
        advanced_buttons.append(
            self._create_starry_button(
                "🪐",
                "流日運勢" if (is_admin or is_premium) else "🔒 需要付費會員",
                "control_panel=daily_fortune",
                (is_admin or is_premium),
                is_premium,
                is_admin
            )
        )
        
        # 其他功能按鈕
        other_buttons = []
        other_buttons.append(
            self._create_starry_button(
                "📊",
                "命盤解析",
                "control_panel=chart_analysis",
                True,
                False,
                False
            )
        )
        other_buttons.append(
            self._create_starry_button(
                "💎",
                "會員升級",
                "control_panel=member_upgrade",
                True,
                False,
                False
            )
        )
        
        # 管理員功能按鈕
        admin_buttons = []
        if is_admin:
            admin_buttons.append(
                self._create_starry_button(
                    "⏰",
                    "指定時間占卜",
                    "admin_action=time_divination_start",
                    True,
                    False,
                    True
                )
            )
            admin_buttons.append(
                self._create_starry_button(
                    "⚙️",
                    "管理員工具",
                    "control_panel=admin_functions",
                    True,
                    False,
                    True
                )
            )
        
        # 組合所有按鈕到分區
        all_sections = []
        
        # 基本功能區
        if basic_buttons:
            all_sections.append({
                "type": "text",
                "text": "✨ 基本功能",
                "weight": "bold",
                "size": "lg",
                "color": "#FFD700",
                "margin": "md"
            })
            all_sections.extend(basic_buttons)
        
        # 進階功能區
        if advanced_buttons:
            all_sections.append({
                "type": "separator",
                "margin": "xl",
                "color": "rgba(255, 215, 0, 0.3)"
            })
            all_sections.append({
                "type": "text",
                "text": "🌟 進階功能",
                "weight": "bold",
                "size": "lg",
                "color": "#E67E22",
                "margin": "md"
            })
            all_sections.extend(advanced_buttons)
        
        # 其他功能區
        if other_buttons:
            all_sections.append({
                "type": "separator",
                "margin": "xl",
                "color": "rgba(255, 215, 0, 0.3)"
            })
            all_sections.append({
                "type": "text",
                "text": "🎯 其他功能",
                "weight": "bold",
                "size": "lg",
                "color": "#9B59B6",
                "margin": "md"
            })
            all_sections.extend(other_buttons)
        
        # 管理員功能區
        if admin_buttons:
            all_sections.append({
                "type": "separator",
                "margin": "xl",
                "color": "rgba(255, 215, 0, 0.3)"
            })
            all_sections.append({
                "type": "text",
                "text": "👑 管理功能",
                "weight": "bold",
                "size": "lg",
                "color": "#E74C3C",
                "margin": "md"
            })
            all_sections.extend(admin_buttons)
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": all_sections,
            "spacing": "sm",
            "paddingAll": "lg"
        }
    
    def _create_starry_basic_section(self) -> Dict:
        """創建星空主題基本功能區塊"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🔮 基本功能",
                    "weight": "bold",
                    "size": "lg",
                    "color": self.colors["secondary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        self._create_starry_button(
                            "本週占卜",
                            "根據當下時間進行觸機占卜",
                            "🔮",
                            True,
                            False,
                            False
                        )
                    ],
                    "spacing": "sm",
                    "margin": "md"
                }
            ],
            "backgroundColor": self.colors["card_bg"],
            "paddingAll": "lg"
        }
    
    def _create_starry_fortune_section(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建星空主題運勢功能區塊"""
        buttons = []
        
        # 流年運勢
        buttons.append(
            self._create_starry_button(
                "流年運勢",
                "年度整體運勢分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🌍",
                True,
                False,
                False
            )
        )
        
        # 流月運勢
        buttons.append(
            self._create_starry_button(
                "流月運勢",
                "月度運勢變化分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🌙",
                True,
                False,
                False
            )
        )
        
        # 流日運勢
        buttons.append(
            self._create_starry_button(
                "流日運勢",
                "每日運勢詳細分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🪐",
                True,
                False,
                False
            )
        )
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "⭐ 運勢查詢",
                    "weight": "bold",
                    "size": "lg",
                    "color": self.colors["secondary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons,
                    "spacing": "sm",
                    "margin": "md"
                }
            ],
            "backgroundColor": self.colors["card_bg"],
            "paddingAll": "lg"
        }
    
    def _create_starry_advanced_section(self, is_admin: bool) -> Dict:
        """創建星空主題進階功能區塊"""
        buttons = []
        
        # 命盤分析
        buttons.append(
            self._create_starry_button(
                "命盤分析",
                "完整紫微斗數命盤解析",
                "📊",
                True,
                False,
                False
            )
        )
        
        # 會員升級（只有非管理員看到）
        if not is_admin:
            buttons.append(
                self._create_starry_button(
                    "會員升級",
                    "升級享受更多專業功能",
                    "💎",
                    True,
                    False,
                    False
                )
            )
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "💫 進階功能",
                    "weight": "bold",
                    "size": "lg",
                    "color": self.colors["secondary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons,
                    "spacing": "sm",
                    "margin": "md"
                }
            ],
            "backgroundColor": self.colors["card_bg"],
            "paddingAll": "lg"
        }
    
    def _create_starry_admin_section(self) -> Dict:
        """創建星空主題管理員功能區塊"""
        buttons = [
            self._create_starry_button(
                "⏰ 指定時間占卜",
                "回溯特定時間點進行占卜",
                "⏰",
                True,
                False,
                True
            ),
            self._create_starry_button(
                "管理員工具",
                "系統管理與數據分析",
                "⚙️",
                True,
                False,
                True
            )
        ]
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "👑 管理功能",
                    "weight": "bold",
                    "size": "lg",
                    "color": self.colors["admin"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons,
                    "spacing": "sm",
                    "margin": "md"
                }
            ],
            "backgroundColor": self.colors["card_bg"],
            "paddingAll": "lg"
        }
    
    def _create_function_button(self, title: str, description: str, icon: str, 
                              action_data: str, color: str, disabled: bool = False) -> Dict:
        """創建功能按鈕"""
        button_style = "primary" if not disabled else "secondary"
        button_color = color if not disabled else self.colors["text_light"]
        
        return {
            "type": "button",
            "style": button_style,
            "height": "sm",
            "action": {
                "type": "postback",
                "label": f"{icon} {title}",
                "data": action_data,
                "displayText": f"{icon} {title}"
            },
            "color": button_color
        }
    
    def _create_starry_button(self, icon: str, text: str, action_data: str, is_enabled: bool = True, 
                             is_premium: bool = False, is_admin: bool = False) -> Dict:
        """創建星空主題按鈕 - 半透明立體效果"""
        
        if not is_enabled:
            # 禁用狀態 - 半透明灰色
            button_bg = "rgba(108, 123, 127, 0.1)"
            border_color = "rgba(128, 128, 128, 0.3)"
            text_color = "#999999"
            icon_color = "#999999"
        elif is_admin:
            # 管理員按鈕 - 半透明紅金色
            button_bg = "rgba(231, 76, 60, 0.15)"
            border_color = "rgba(255, 215, 0, 0.8)"
            text_color = "#FFFFFF"
            icon_color = "#FFD700"
        elif is_premium:
            # 付費會員按鈕 - 半透明紫色
            button_bg = "rgba(155, 89, 182, 0.15)"
            border_color = "rgba(230, 126, 34, 0.8)"
            text_color = "#FFFFFF"
            icon_color = "#E67E22"
        else:
            # 一般按鈕 - 半透明藍色
            button_bg = "rgba(74, 144, 226, 0.15)"
            border_color = "rgba(255, 215, 0, 0.6)"
            text_color = "#FFFFFF"
            icon_color = "#FFD700"
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                # 主按鈕區域
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": icon,
                            "size": "xl",
                            "color": icon_color,
                            "flex": 0,
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": text,
                            "weight": "bold",
                            "size": "lg",
                            "color": text_color,
                            "flex": 1,
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "⭐⭐⭐" if is_enabled else "🔒🔒",
                            "size": "sm",
                            "color": "#FFD700" if is_enabled else "#999999",
                            "flex": 0
                        }
                    ],
                    "backgroundColor": button_bg,
                    "paddingAll": "16px",
                    "borderWidth": "1px",
                    "borderColor": border_color,
                    "action": {
                        "type": "postback",
                        "data": action_data
                    } if is_enabled else None
                },
                # 底部陰影效果
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "height": "3px",
                    "backgroundColor": "rgba(0, 0, 0, 0.1)"
                }
            ],
            "spacing": "none",
            "margin": "sm"
        }
    
    def _create_starry_separator(self) -> Dict:
        """創建星空主題分隔線"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "✨",
                    "size": "xs",
                    "color": self.colors["secondary"],
                    "align": "center",
                    "flex": 1
                },
                {
                    "type": "separator",
                    "color": self.colors["border"],
                    "flex": 8
                },
                {
                    "type": "text",
                    "text": "✨",
                    "size": "xs",
                    "color": self.colors["secondary"],
                    "align": "center",
                    "flex": 1
                }
            ],
            "margin": "md"
        }
    
    def _create_starry_footer(self) -> Dict:
        """創建星空主題控制面板底部"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🌟 星空智能面板會根據您的權限動態調整功能 🌟",
                    "size": "xs",
                    "color": self.colors["text_secondary"],
                    "align": "center",
                    "wrap": True
                }
            ],
            "margin": "sm",
            "paddingAll": "sm"
        } 