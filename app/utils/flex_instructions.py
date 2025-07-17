"""
Flex Message 使用說明生成器
用於生成智能的使用說明，根據用戶權限顯示不同內容
"""

import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class FlexInstructionsGenerator:
    """Flex Message 使用說明生成器"""
    
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
    
    def generate_instructions(self, user_stats: Dict[str, Any]) -> Optional[Dict]:
        """
        生成使用說明
        
        Args:
            user_stats: 用戶統計資訊，包含權限和會員資訊
            
        Returns:
            Flex Message 字典格式
        """
        try:
            is_admin = user_stats.get("user_info", {}).get("is_admin", False)
            is_premium = user_stats.get("membership_info", {}).get("is_premium", False)
            
            # 構建使用說明
            flex_message = {
                "type": "flex",
                "altText": "📖 使用說明",
                "contents": {
                    "type": "bubble",
                    "size": "micro",  # 改為微型尺寸，與其他面板一致
                    "header": self._create_header(is_admin, is_premium),
                    "body": self._create_body(is_admin, is_premium),
                    "footer": self._create_footer()
                }
            }
            
            return flex_message
            
        except Exception as e:
            logger.error(f"生成使用說明失敗: {e}")
            return None
    
    def _create_header(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建使用說明標題區域"""
        user_type = "管理員" if is_admin else ("付費會員" if is_premium else "免費會員")
        user_color = self.colors["admin"] if is_admin else (self.colors["premium"] if is_premium else self.colors["primary"])
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📖 使用說明",
                    "weight": "bold",
                    "size": "xl",
                    "color": self.colors["text_primary"],
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": f"✨ 專為{user_type}設計",
                    "size": "sm",
                    "color": user_color,
                    "align": "center",
                    "margin": "xs"
                }
            ],
            "paddingBottom": "md"
        }
    
    def _create_body(self, is_admin: bool, is_premium: bool) -> Dict:
        """創建使用說明主體內容"""
        contents = []
        
        # 基本功能說明
        basic_section = self._create_basic_functions_guide()
        contents.append(basic_section)
        
        # 分隔線
        contents.append(self._create_separator())
        
        # 操作指南
        operation_section = self._create_operation_guide()
        contents.append(operation_section)
        
        # 如果是付費會員或管理員，添加進階功能說明
        if is_premium or is_admin:
            contents.append(self._create_separator())
            advanced_section = self._create_advanced_guide(is_admin)
            contents.append(advanced_section)
        
        # 如果是管理員，添加管理功能說明
        if is_admin:
            contents.append(self._create_separator())
            admin_section = self._create_admin_guide()
            contents.append(admin_section)
        
        # 貼心提醒
        contents.append(self._create_separator())
        tips_section = self._create_tips_section()
        contents.append(tips_section)
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "spacing": "md"
        }
    
    def _create_basic_functions_guide(self) -> Dict:
        """創建基本功能說明"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🔮 主要功能",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["text_primary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "• 本週占卜 - 根據當下時間進行觸機占卜",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": "• 會員資訊 - 查看個人使用記錄和權限",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": "• 功能選單 - 智能控制面板，權限感知",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        }
                    ],
                    "margin": "sm"
                }
            ]
        }
    
    def _create_operation_guide(self) -> Dict:
        """創建操作指南"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "💫 操作方式",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["text_primary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "1️⃣ 點擊下方選單按鈕快速進入功能",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": "2️⃣ 或直接輸入文字指令（如「占卜」）",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": "3️⃣ 依照系統提示完成操作",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        }
                    ],
                    "margin": "sm"
                }
            ]
        }
    
    def _create_advanced_guide(self, is_admin: bool) -> Dict:
        """創建進階功能說明"""
        features = [
            "• 流年運勢 - 年度整體運勢分析",
            "• 流月運勢 - 月度運勢變化分析", 
            "• 流日運勢 - 每日運勢詳細分析",
            "• 四化詳細解釋 - 完整的紫微斗數解析"
        ]
        
        if is_admin:
            features.append("• 指定時間占卜 - 回溯特定時間點運勢")
        
        feature_texts = []
        for feature in features:
            feature_texts.append({
                "type": "text",
                "text": feature,
                "size": "sm",
                "color": self.colors["text_secondary"],
                "wrap": True,
                "margin": "xs" if feature != features[0] else "none"
            })
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "⭐ 專屬功能",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["premium"] if not is_admin else self.colors["admin"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": feature_texts,
                    "margin": "sm"
                }
            ]
        }
    
    def _create_admin_guide(self) -> Dict:
        """創建管理員功能說明"""
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
                    "contents": [
                        {
                            "type": "text",
                            "text": "• 系統監控 - 用戶數據和系統狀態",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": "• 權限管理 - 用戶權限和會員管理",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": "• 選單管理 - Rich Menu 創建和更新",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        }
                    ],
                    "margin": "sm"
                }
            ]
        }
    
    def _create_tips_section(self) -> Dict:
        """創建貼心提醒區塊"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🌟 貼心提醒",
                    "weight": "bold",
                    "size": "md",
                    "color": self.colors["text_primary"],
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "• 每週只能占卜一次，請珍惜機會",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": "• 升級會員可享受更多專業功能",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": "• 有問題可隨時聯繫客服",
                            "size": "sm",
                            "color": self.colors["text_secondary"],
                            "wrap": True,
                            "margin": "xs"
                        }
                    ],
                    "margin": "sm"
                }
            ]
        }
    
    def _create_separator(self) -> Dict:
        """創建分隔線"""
        return {
            "type": "separator",
            "margin": "md",
            "color": "#E5E5E5"
        }
    
    def _create_footer(self) -> Dict:
        """創建使用說明底部"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "⭐ 願紫微斗數為您指引人生方向！",
                    "size": "sm",
                    "color": self.colors["primary"],
                    "align": "center",
                    "weight": "bold",
                    "wrap": True
                }
            ],
            "margin": "sm"
        } 