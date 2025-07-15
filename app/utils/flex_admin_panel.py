"""
Flex Message 管理員面板生成器
用於生成管理員專用的功能面板
"""

import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class FlexAdminPanelGenerator:
    """Flex Message 管理員面板生成器"""
    
    def __init__(self):
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
    
    def generate_admin_panel(self) -> Optional[Dict]:
        """
        生成管理員面板
        
        Returns:
            Flex Message 字典格式
        """
        try:
            # 構建管理員面板
            flex_message = {
                "type": "flex",
                "altText": "👑 管理員功能面板",
                "contents": {
                    "type": "bubble",
                    "size": "kilo",
                    "header": self._create_header(),
                    "body": self._create_body(),
                    "footer": self._create_footer()
                }
            }
            
            return flex_message
            
        except Exception as e:
            logger.error(f"生成管理員面板失敗: {e}")
            return None
    
    def _create_header(self) -> Dict:
        """創建管理員面板標題區域"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "👑 管理員功能面板",
                    "weight": "bold",
                    "size": "xl",
                    "color": self.colors["admin"],
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "⚙️ 系統管理與數據分析",
                    "size": "sm",
                    "color": self.colors["text_secondary"],
                    "align": "center",
                    "margin": "xs"
                }
            ],
            "paddingBottom": "md"
        }
    
    def _create_body(self) -> Dict:
        """創建管理員面板主體內容"""
        contents = []
        
        # 系統管理區塊
        system_section = self._create_system_management_section()
        contents.append(system_section)
        
        # 分隔線
        contents.append(self._create_separator())
        
        # 數據管理區塊
        data_section = self._create_data_management_section()
        contents.append(data_section)
        
        # 分隔線
        contents.append(self._create_separator())
        
        # 選單管理區塊
        menu_section = self._create_menu_management_section()
        contents.append(menu_section)
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "spacing": "md"
        }
    
    def _create_system_management_section(self) -> Dict:
        """創建系統管理區塊"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🔧 系統管理",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["admin"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        self._create_admin_button(
                            "指定時間占卜",
                            "回溯特定時間點運勢分析",
                            "⏰",
                            "admin_action=time_divination"
                        ),
                        self._create_admin_button(
                            "用戶數據統計",
                            "查看系統用戶使用情況",
                            "📊", 
                            "admin_action=user_stats"
                        ),
                        self._create_admin_button(
                            "系統狀態監控",
                            "監控系統運行狀態",
                            "🖥️",
                            "admin_action=system_status"
                        )
                    ],
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
        }
    
    def _create_data_management_section(self) -> Dict:
        """創建數據管理區塊"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📊 數據管理",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["secondary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        self._create_admin_button(
                            "占卜記錄查詢",
                            "查看用戶占卜歷史記錄",
                            "🔍",
                            "admin_action=divination_records"
                        ),
                        self._create_admin_button(
                            "用戶權限管理",
                            "管理用戶權限和會員狀態",
                            "👥",
                            "admin_action=user_permissions"
                        ),
                        self._create_admin_button(
                            "數據導出",
                            "導出系統數據報表",
                            "📤",
                            "admin_action=data_export"
                        )
                    ],
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
        }
    
    def _create_menu_management_section(self) -> Dict:
        """創建選單管理區塊"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "⚙️ 選單管理",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["accent"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        self._create_admin_button(
                            "更新選單",
                            "更新用戶Rich Menu",
                            "🔄",
                            "admin_action=update_menu"
                        ),
                        self._create_admin_button(
                            "創建選單",
                            "創建新的Rich Menu",
                            "➕",
                            "admin_action=create_menu"
                        ),
                        self._create_admin_button(
                            "選單統計",
                            "查看選單使用統計",
                            "📈",
                            "admin_action=menu_stats"
                        )
                    ],
                    "spacing": "sm",
                    "margin": "sm"
                }
            ]
        }
    
    def _create_admin_button(self, title: str, description: str, icon: str, action_data: str) -> Dict:
        """創建管理員功能按鈕"""
        return {
            "type": "button",
            "style": "primary",
            "height": "sm",
            "action": {
                "type": "postback",
                "label": f"{icon} {title}",
                "data": action_data,
                "displayText": f"{icon} {title}"
            },
            "color": self.colors["admin"]
        }
    
    def _create_separator(self) -> Dict:
        """創建分隔線"""
        return {
            "type": "separator",
            "margin": "md",
            "color": "#E5E5E5"
        }
    
    def _create_footer(self) -> Dict:
        """創建管理員面板底部"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "⚠️ 管理員功能請謹慎使用",
                    "size": "xs",
                    "color": self.colors["text_light"],
                    "align": "center",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "如需文字指令，請參考使用說明",
                    "size": "xs",
                    "color": self.colors["text_light"],
                    "align": "center",
                    "wrap": True,
                    "margin": "xs"
                }
            ],
            "margin": "sm"
        } 