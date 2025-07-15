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
        """創建星空主題控制面板標題區域"""
        user_type = "👑 管理員" if is_admin else ("💎 付費會員" if is_premium else "✨ 免費會員")
        user_color = self.colors["admin"] if is_admin else (self.colors["premium"] if is_premium else self.colors["primary"])
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🌌",
                            "size": "xxl",
                            "flex": 0,
                            "color": self.colors["secondary"]
                        },
                        {
                            "type": "text",
                            "text": "星空功能面板",
                            "weight": "bold",
                            "size": "xl",
                            "color": self.colors["text_primary"],
                            "flex": 1,
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "⭐",
                            "size": "lg",
                            "flex": 0,
                            "color": self.colors["secondary"]
                        }
                    ],
                    "paddingAll": "lg",
                    "backgroundColor": self.colors["card_bg"],
                    "cornerRadius": "md"
                },
                {
                    "type": "text",
                    "text": user_type,
                    "size": "md",
                    "color": user_color,
                    "align": "center",
                    "margin": "md",
                    "weight": "bold"
                }
            ],
            "paddingBottom": "md"
        }
    
    def _create_starry_body(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建星空主題控制面板主體內容"""
        contents = []
        
        # 基本功能區塊
        basic_section = self._create_starry_basic_section()
        contents.append(basic_section)
        
        # 星空分隔線
        contents.append(self._create_starry_separator())
        
        # 運勢功能區塊
        fortune_section = self._create_starry_fortune_section(is_admin, is_premium)
        contents.append(fortune_section)
        
        # 如果是付費會員或管理員，添加進階功能
        if is_premium or is_admin:
            contents.append(self._create_starry_separator())
            advanced_section = self._create_starry_advanced_section(is_admin)
            contents.append(advanced_section)
        
        # 如果是管理員，添加管理功能
        if is_admin:
            contents.append(self._create_starry_separator())
            admin_section = self._create_starry_admin_section()
            contents.append(admin_section)
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "spacing": "md",
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
                            "control_panel=basic_divination",
                            self.colors["primary"]
                        )
                    ],
                    "spacing": "sm",
                    "margin": "md"
                }
            ],
            "backgroundColor": self.colors["card_bg"],
            "cornerRadius": "md",
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
                "control_panel=yearly_fortune",
                self.colors["primary"] if (is_admin or is_premium) else self.colors["text_light"],
                disabled=not (is_admin or is_premium)
            )
        )
        
        # 流月運勢
        buttons.append(
            self._create_starry_button(
                "流月運勢",
                "月度運勢變化分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🌙",
                "control_panel=monthly_fortune",
                self.colors["primary"] if (is_admin or is_premium) else self.colors["text_light"],
                disabled=not (is_admin or is_premium)
            )
        )
        
        # 流日運勢
        buttons.append(
            self._create_starry_button(
                "流日運勢",
                "每日運勢詳細分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🪐",
                "control_panel=daily_fortune",
                self.colors["primary"] if (is_admin or is_premium) else self.colors["text_light"],
                disabled=not (is_admin or is_premium)
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
            "cornerRadius": "md",
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
                "control_panel=chart_analysis",
                self.colors["accent"]
            )
        )
        
        # 會員升級（只有非管理員看到）
        if not is_admin:
            buttons.append(
                self._create_starry_button(
                    "會員升級",
                    "升級享受更多專業功能",
                    "💎",
                    "control_panel=member_upgrade",
                    self.colors["premium"]
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
            "cornerRadius": "md",
            "paddingAll": "lg"
        }
    
    def _create_starry_admin_section(self) -> Dict:
        """創建星空主題管理員功能區塊"""
        buttons = [
            self._create_starry_button(
                "⏰ 指定時間占卜",
                "回溯特定時間點進行占卜",
                "⏰",
                "admin_action=time_divination_start",
                self.colors["admin"]
            ),
            self._create_starry_button(
                "管理員工具",
                "系統管理與數據分析",
                "⚙️",
                "control_panel=admin_functions",
                self.colors["admin"]
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
            "cornerRadius": "md",
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
    
    def _create_starry_button(self, title: str, description: str, icon: str, 
                              action_data: str, color: str, disabled: bool = False) -> Dict:
        """創建星空主題功能按鈕"""
        button_bg = color if not disabled else self.colors["border"]
        text_color = "#FFFFFF" if not disabled else self.colors["text_light"]
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": icon,
                            "size": "lg",
                            "flex": 0,
                            "color": text_color
                        },
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "md",
                            "color": text_color,
                            "flex": 1,
                            "margin": "sm"
                        }
                    ],
                    "paddingAll": "md",
                    "backgroundColor": button_bg,
                    "cornerRadius": "md",
                    "action": {
                        "type": "postback",
                        "data": action_data,
                        "displayText": f"{icon} {title}"
                    } if not disabled else None
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "xs",
                    "color": self.colors["text_secondary"],
                    "wrap": True,
                    "margin": "xs"
                }
            ],
            "spacing": "none"
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