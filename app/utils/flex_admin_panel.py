"""
管理員 Flex Message 面板生成器
提供管理員專用的控制面板和功能選單
"""

import logging
from typing import Dict, List, Optional
from linebot.v3.messaging import (
    FlexMessage, FlexBubble, FlexBox, FlexText, FlexSeparator, PostbackAction
)

logger = logging.getLogger(__name__)

class FlexAdminPanelGenerator:
    """Flex Message 管理員面板生成器"""
    
    def __init__(self):
        # 色彩主題
        self.colors = {
            "admin": "#8B0000",      # 深紅色 - 管理員主色
            "primary": "#2E86AB",    # 深藍色 - 主要功能
            "secondary": "#A23B72",  # 紫紅色 - 次要功能  
            "accent": "#F18F01",     # 橙色 - 強調色
            "success": "#C73E1D",    # 深紅色 - 成功狀態
            "background": "#F8F9FA"  # 淺灰色 - 背景
        }
    
    def generate_admin_panel(self) -> Optional[FlexMessage]:
        """生成管理員功能面板"""
        try:
            # 創建主要功能按鈕 - 將指定時間占卜放在最前面
            main_buttons = [
                self._create_main_admin_button(
                    "⏰ 指定時間占卜",
                    "回溯特定時間點進行占卜",
                    "admin_action=time_divination_start",
                    self.colors["primary"]
                ),
                self._create_main_admin_button(
                    "📊 用戶數據統計", 
                    "查看系統使用情況",
                    "admin_action=user_stats",
                    self.colors["secondary"]
                ),
                self._create_main_admin_button(
                    "🖥️ 系統狀態監控",
                    "監控系統運行狀態", 
                    "admin_action=system_status",
                    self.colors["accent"]
                ),
                self._create_main_admin_button(
                    "⚙️ 選單管理",
                    "管理Rich Menu設定",
                    "admin_action=menu_management", 
                    self.colors["success"]
                )
            ]

            bubble = FlexBubble(
                size="giga",
                body=FlexBox(
                    layout="vertical",
                    contents=[
                        # 標題區域
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text="👑",
                                    size="xxl",
                                    flex=0
                                ),
                                FlexText(
                                    text="管理員控制面板",
                                    weight="bold",
                                    size="xxl",
                                    color=self.colors["admin"],
                                    flex=1,
                                    margin="md"
                                )
                            ],
                            backgroundColor=self.colors["background"],
                            cornerRadius="md",
                            paddingAll="lg"
                        ),
                        FlexSeparator(margin="xl"),
                        
                        # 主要功能區域
                        FlexBox(
                            layout="vertical",
                            contents=main_buttons,
                            spacing="md",
                            margin="lg"
                        ),
                        
                        # 底部說明
                        FlexSeparator(margin="xl"),
                        FlexText(
                            text="💫 管理員專屬功能面板",
                            size="sm",
                            color="#999999",
                            align="center",
                            margin="md"
                        )
                    ],
                    spacing="none",
                    paddingAll="xl"
                ),
                styles={
                    "body": {
                        "backgroundColor": "#FFFFFF"
                    }
                }
            )
            
            return FlexMessage(
                alt_text="👑 管理員控制面板",
                contents=bubble
            )
            
        except Exception as e:
            logger.error(f"生成管理員面板失敗: {e}")
            return None
    
    def _create_main_admin_button(self, title: str, description: str, action: str, color: str) -> FlexBox:
        """創建主要管理員功能按鈕"""
        return FlexBox(
            layout="vertical",
            contents=[
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(
                            text=title,
                            weight="bold",
                            size="lg",
                            color="#FFFFFF",
                            flex=1
                        )
                    ],
                    backgroundColor=color,
                    cornerRadius="md",
                    paddingAll="lg",
                    action=PostbackAction(
                        data=action
                    )
                ),
                FlexText(
                    text=description,
                    size="sm",
                    color="#666666",
                    margin="sm"
                )
            ],
            spacing="none",
            margin="md"
        )
    
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