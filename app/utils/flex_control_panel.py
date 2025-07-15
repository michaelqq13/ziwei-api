"""
Flex Message 控制面板生成器
用於生成智能的功能控制面板，根據用戶權限顯示不同功能
"""

import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class FlexControlPanelGenerator:
    """Flex Message 控制面板生成器"""
    
    def __init__(self):
        self.panel_title = "🌟 功能控制面板"
        self.colors = {
            "primary": "#1DB446",      # LINE 綠色
            "secondary": "#FFD700",    # 金色
            "accent": "#FF6B6B",       # 珊瑚紅
            "premium": "#9B59B6",      # 紫色
            "admin": "#E74C3C",        # 紅色
            "text_primary": "#333333",
            "text_secondary": "#666666",
            "text_light": "#999999"
        }
    
    def generate_control_panel(self, user_stats: Dict[str, Any]) -> Optional[Dict]:
        """
        生成控制面板
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            Flex Message 字典格式
        """
        try:
            is_admin = user_stats.get("user_info", {}).get("is_admin", False)
            is_premium = user_stats.get("membership_info", {}).get("is_premium", False)
            
            # 構建控制面板
            flex_message = {
                "type": "flex",
                "altText": "🌟 功能控制面板",
                "contents": {
                    "type": "bubble",
                    "size": "kilo",
                    "header": self._create_header(is_admin, is_premium),
                    "body": self._create_body(is_admin, is_premium),
                    "footer": self._create_footer()
                }
            }
            
            return flex_message
            
        except Exception as e:
            logger.error(f"生成控制面板失敗: {e}")
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
                    "text": "🌟 功能控制面板",
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
    
    def _create_body(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建控制面板主體內容"""
        contents = []
        
        # 基本功能區塊
        basic_section = self._create_basic_functions_section()
        contents.append(basic_section)
        
        # 分隔線
        contents.append(self._create_separator())
        
        # 運勢功能區塊
        fortune_section = self._create_fortune_functions_section(is_admin, is_premium)
        contents.append(fortune_section)
        
        # 如果是付費會員或管理員，添加進階功能
        if is_premium or is_admin:
            contents.append(self._create_separator())
            advanced_section = self._create_advanced_functions_section(is_admin)
            contents.append(advanced_section)
        
        # 如果是管理員，添加管理功能
        if is_admin:
            contents.append(self._create_separator())
            admin_section = self._create_admin_functions_section()
            contents.append(admin_section)
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "spacing": "md"
        }
    
    def _create_basic_functions_section(self) -> Dict:
        """創建基本功能區塊"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🔮 基本功能",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["text_primary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        self._create_function_button(
                            "本週占卜",
                            "根據當下時間進行觸機占卜",
                            "🔮",
                            "control_panel=basic_divination",
                            self.colors["primary"]
                        )
                    ],
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
        }
    
    def _create_fortune_functions_section(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建運勢功能區塊"""
        buttons = []
        
        # 流年運勢
        buttons.append(
            self._create_function_button(
                "流年運勢",
                "年度整體運勢分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🌍",
                "control_panel=yearly_fortune",
                self.colors["secondary"] if (is_admin or is_premium) else self.colors["text_light"],
                disabled=not (is_admin or is_premium)
            )
        )
        
        # 流月運勢
        buttons.append(
            self._create_function_button(
                "流月運勢",
                "月度運勢變化分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🌙",
                "control_panel=monthly_fortune",
                self.colors["secondary"] if (is_admin or is_premium) else self.colors["text_light"],
                disabled=not (is_admin or is_premium)
            )
        )
        
        # 流日運勢
        buttons.append(
            self._create_function_button(
                "流日運勢",
                "每日運勢詳細分析" if (is_admin or is_premium) else "🔒 需要付費會員",
                "🪐",
                "control_panel=daily_fortune",
                self.colors["secondary"] if (is_admin or is_premium) else self.colors["text_light"],
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
                    "size": "md",
                    "color": self.colors["text_primary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons,
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
        }
    
    def _create_advanced_functions_section(self, is_admin: bool) -> Dict:
        """創建進階功能區塊"""
        buttons = []
        
        # 命盤分析
        buttons.append(
            self._create_function_button(
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
                self._create_function_button(
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
                    "size": "md",
                    "color": self.colors["text_primary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons,
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
        }
    
    def _create_admin_functions_section(self) -> Dict:
        """創建管理員功能區塊"""
        buttons = [
            self._create_function_button(
                "⏰ 指定時間占卜",
                "回溯特定時間點進行占卜",
                "⏰",
                "admin_action=time_divination_start",
                self.colors["primary"]
            ),
            self._create_function_button(
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
                    "size": "md",
                    "color": self.colors["admin"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons,
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
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
    
    def _create_separator(self) -> Dict:
        """創建分隔線"""
        return {
            "type": "separator",
            "margin": "md",
            "color": "#E5E5E5"
        }
    
    def _create_footer(self) -> Dict:
        """創建控制面板底部"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "💫 智能控制面板會根據您的權限動態調整功能",
                    "size": "xs",
                    "color": self.colors["text_light"],
                    "align": "center",
                    "wrap": True
                }
            ],
            "margin": "sm"
        } 