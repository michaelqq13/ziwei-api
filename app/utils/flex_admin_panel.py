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
        
        # 星空背景圖片 - 管理員專用
        self.background_images = {
            "admin": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400&q=80"  # 調整尺寸
        }
        
        # 備用背景圖片
        self.fallback_images = {
            "admin": "https://via.placeholder.com/800x400/8B0000/FFD700?text=👑+管理員面板+👑"  # 調整尺寸
        }
    
    def generate_admin_panel(self) -> Optional[FlexMessage]:
        """生成管理員功能面板"""
        try:
            bubble = FlexBubble(
                size="micro",  # 改為微型尺寸，與其他面板一致
                hero=FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text="👑 管理功能",  # 簡化標題
                            weight="bold",
                            size="lg",  # 縮小字體
                            color="#FFD700",
                            align="center"
                        ),
                        FlexText(
                            text="Admin Panel",  # 簡化副標題
                            size="xs",
                            color="#B0C4DE",
                            align="center",
                            margin="xs"
                        )
                    ],
                    backgroundColor="#8B0000CC",  # 半透明深紅遮罩
                    backgroundImage=self.background_images.get("admin", self.fallback_images["admin"]),
                    backgroundSize="cover",
                    backgroundPosition="center",
                    paddingAll="12px",  # 縮小內邊距
                    height="80px"  # 設定固定高度
                ),
                body=FlexBox(
                    layout="vertical",
                    contents=[
                        # 簡化的功能按鈕 - 改用緊湊型
                        FlexBox(
                            layout="vertical",
                            contents=[
                                self._create_compact_admin_button("⏰", "時間占卜", "admin_action=time_divination_start"),
                                self._create_compact_admin_button("📊", "用戶統計", "admin_action=user_stats"),
                                self._create_compact_admin_button("🖥️", "系統監控", "admin_action=system_status"),
                                self._create_compact_admin_button("⚙️", "選單管理", "admin_action=menu_management")
                            ],
                            spacing="xs"  # 緊湊間距
                        ),
                        
                        # 簡化底部說明
                        FlexText(
                            text="💫 管理員專屬",
                            size="xxs",
                            color="#999999",
                            align="center",
                            margin="sm"
                        )
                    ],
                    spacing="sm",
                    paddingAll="12px"  # 縮小內邊距
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
    
    def _create_admin_button(self, title: str, description: str, icon: str, action_data: str, color: str) -> FlexBox:
        """創建管理員功能按鈕 - 半透明立體效果"""
        
        # 半透明管理員按鈕配色
        button_bg = "rgba(139, 0, 0, 0.15)"    # 深紅色 15% 透明度
        border_color = "rgba(255, 215, 0, 0.8)"  # 金邊 80% 透明度
        
        return FlexBox(
            layout="vertical",
            contents=[
                # 主按鈕區域
                FlexBox(
                    layout="vertical",
                    contents=[
                        # 上半部：圖標和標題
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text=icon,
                                    size="xl",
                                    color="#FFD700",
                                    flex=0,
                                    weight="bold"
                                ),
                                FlexText(
                                    text=title,
                                    weight="bold",
                                    size="lg",
                                    color="#FFFFFF",
                                    flex=1,
                                    margin="sm"
                                ),
                                FlexText(
                                    text="👑👑👑",
                                    size="sm",
                                    color="#FFD700",
                                    flex=0,
                                    align="end"
                                )
                            ],
                            spacing="sm"
                        ),
                        # 下半部：描述文字
                        FlexText(
                            text=description,
                            size="xs",
                            color="#B0C4DE",
                            wrap=True,
                            margin="xs"
                        )
                    ],
                    # 半透明背景 + 邊框效果
                    backgroundColor=button_bg,
                    paddingAll="16px",
                    borderWidth="1px",
                    borderColor=border_color,
                    action=PostbackAction(data=action_data, displayText=title)
                ),
                
                # 底部陰影效果（模擬立體感）
                FlexBox(
                    layout="vertical",
                    contents=[],
                    height="3px",
                    backgroundColor="rgba(0, 0, 0, 0.1)",  # 淺色陰影
                    margin="none"
                )
            ],
            spacing="none",
            margin="sm"
        )
    
    def _create_compact_admin_button(self, icon: str, title: str, action_data: str) -> FlexBox:
        """創建緊湊型管理員功能按鈕"""
        return FlexBox(
            layout="horizontal",
            contents=[
                FlexText(
                    text=icon,
                    size="md",
                    color="#FFD700",
                    flex=0,
                    weight="bold"
                ),
                FlexText(
                    text=title,
                    weight="bold",
                    size="sm",
                    color="#FFFFFF",
                    flex=1,
                    margin="sm"
                )
            ],
            paddingAll="8px",
            borderWidth="1px",
            borderColor="#FFD700",
            backgroundColor="rgba(139, 0, 0, 0.15)",  # 半透明深紅背景
            action=PostbackAction(
                data=action_data,
                displayText=title
            ),
            margin="xs"
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