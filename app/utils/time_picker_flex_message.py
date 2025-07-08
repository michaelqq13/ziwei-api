"""
時間選擇器 Flex Message 生成器
使用 Datetime Picker Action 提供更好的時間選擇體驗
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from linebot.v3.messaging import (
    FlexMessage, FlexContainer, FlexBubble, FlexBox, FlexText, 
    FlexSeparator, FlexFiller, FlexButton, FlexSpacer
)
from linebot.v3.messaging.models import (
    Action, MessageAction, DatetimePickerAction, PostbackAction
)
import logging

logger = logging.getLogger(__name__)

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

class TimePickerFlexMessageGenerator:
    """時間選擇器 Flex Message 生成器"""
    
    def __init__(self):
        self.current_time = datetime.now(TAIPEI_TZ)
    
    def create_time_selection_message(self, gender: str) -> FlexMessage:
        """
        創建時間選擇 Flex Message
        
        Args:
            gender: 性別 ('M' 或 'F')
            
        Returns:
            FlexMessage: 時間選擇器消息
        """
        try:
            # 設定時間範圍
            min_time = (self.current_time - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M")
            max_time = (self.current_time + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
            initial_time = (self.current_time - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
            
            # 創建主要的時間選擇區域
            main_contents = [
                # 標題
                FlexText(
                    text="⏰ 選擇占卜時間",
                    weight="bold",
                    size="xl",
                    color="#FF6B6B",
                    align="center"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 說明文字
                FlexText(
                    text="請選擇您想要占卜的時間點",
                    size="md",
                    color="#666666",
                    align="center",
                    wrap=True,
                    margin="md"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 當前時間顯示
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(
                            text="📅 當前時間",
                            size="sm",
                            color="#888888",
                            flex=1
                        ),
                        FlexText(
                            text=self.current_time.strftime("%Y-%m-%d %H:%M"),
                            size="sm",
                            weight="bold",
                            color="#333333",
                            flex=2,
                            align="end"
                        )
                    ],
                    margin="md"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 快速選擇按鈕區域
                FlexText(
                    text="🚀 快速選擇",
                    size="md",
                    weight="bold",
                    color="#4ECDC4",
                    margin="md"
                ),
                
                # 第一行快速按鈕
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexButton(
                            action=PostbackAction(
                                label="1小時前",
                                data=f"time_select|{(self.current_time - timedelta(hours=1)).isoformat()}|{gender}"
                            ),
                            style="secondary",
                            size="sm",
                            color="#4ECDC4",
                            flex=1
                        ),
                        FlexSpacer(size="sm"),
                        FlexButton(
                            action=PostbackAction(
                                label="2小時前",
                                data=f"time_select|{(self.current_time - timedelta(hours=2)).isoformat()}|{gender}"
                            ),
                            style="secondary",
                            size="sm",
                            color="#4ECDC4",
                            flex=1
                        ),
                        FlexSpacer(size="sm"),
                        FlexButton(
                            action=PostbackAction(
                                label="3小時前",
                                data=f"time_select|{(self.current_time - timedelta(hours=3)).isoformat()}|{gender}"
                            ),
                            style="secondary",
                            size="sm",
                            color="#4ECDC4",
                            flex=1
                        )
                    ],
                    spacing="sm",
                    margin="md"
                ),
                
                # 第二行快速按鈕
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexButton(
                            action=PostbackAction(
                                label="6小時前",
                                data=f"time_select|{(self.current_time - timedelta(hours=6)).isoformat()}|{gender}"
                            ),
                            style="secondary",
                            size="sm",
                            color="#4ECDC4",
                            flex=1
                        ),
                        FlexSpacer(size="sm"),
                        FlexButton(
                            action=PostbackAction(
                                label="昨天同時",
                                data=f"time_select|{(self.current_time - timedelta(days=1)).isoformat()}|{gender}"
                            ),
                            style="secondary",
                            size="sm",
                            color="#4ECDC4",
                            flex=1
                        ),
                        FlexSpacer(size="sm"),
                        FlexButton(
                            action=PostbackAction(
                                label="一週前",
                                data=f"time_select|{(self.current_time - timedelta(days=7)).isoformat()}|{gender}"
                            ),
                            style="secondary",
                            size="sm",
                            color="#4ECDC4",
                            flex=1
                        )
                    ],
                    spacing="sm",
                    margin="sm"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 精確時間選擇標題
                FlexText(
                    text="🎯 精確時間選擇",
                    size="md",
                    weight="bold",
                    color="#FF6B6B",
                    margin="md"
                ),
                
                # 說明文字
                FlexText(
                    text="滑動滾輪選擇精確的日期和時間",
                    size="sm",
                    color="#888888",
                    align="center",
                    wrap=True,
                    margin="xs"
                ),
                
                # 日期時間選擇器按鈕
                FlexButton(
                    action=DatetimePickerAction(
                        label="📅 選擇日期時間",
                        data=f"datetime_select|{gender}",
                        mode="datetime",
                        initial=initial_time,
                        max=max_time,
                        min=min_time
                    ),
                    style="primary",
                    color="#FF6B6B",
                    height="md",
                    margin="md"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 底部說明
                FlexText(
                    text="💡 可選擇過去30天內或未來7天內的時間",
                    size="xs",
                    color="#999999",
                    align="center",
                    wrap=True,
                    margin="md"
                )
            ]
            
            bubble = FlexBubble(
                size="giga",
                body=FlexBox(
                    layout="vertical",
                    contents=main_contents,
                    paddingAll="xl",
                    spacing="none"
                ),
                styles={
                    "body": {
                        "backgroundColor": "#FFFFFF"
                    }
                }
            )
            
            return FlexMessage(
                alt_text="⏰ 選擇占卜時間",
                contents=bubble
            )
            
        except Exception as e:
            logger.error(f"創建時間選擇器失敗: {e}")
            return None
    
    def create_time_confirmation_message(self, selected_time: datetime, gender: str) -> FlexMessage:
        """
        創建時間確認 Flex Message
        
        Args:
            selected_time: 選擇的時間
            gender: 性別
            
        Returns:
            FlexMessage: 時間確認消息
        """
        try:
            # 計算時間差
            time_diff = self.current_time - selected_time
            
            # 生成時間差描述
            if time_diff.total_seconds() > 0:
                if time_diff.days > 0:
                    time_desc = f"{time_diff.days}天前"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_desc = f"{hours}小時前"
                else:
                    minutes = time_diff.seconds // 60
                    time_desc = f"{minutes}分鐘前"
            else:
                time_desc = "未來時間"
            
            gender_text = "👨 男性" if gender == "M" else "👩 女性"
            
            contents = [
                # 標題
                FlexText(
                    text="✅ 確認占卜時間",
                    weight="bold",
                    size="xl",
                    color="#4ECDC4",
                    align="center"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 選擇的時間資訊
                FlexBox(
                    layout="vertical",
                    contents=[
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text="🕰️ 選擇時間",
                                    size="md",
                                    color="#666666",
                                    flex=1
                                ),
                                FlexText(
                                    text=selected_time.strftime("%Y-%m-%d %H:%M"),
                                    size="md",
                                    weight="bold",
                                    color="#333333",
                                    flex=2,
                                    align="end"
                                )
                            ]
                        ),
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text="📊 時間差",
                                    size="md",
                                    color="#666666",
                                    flex=1
                                ),
                                FlexText(
                                    text=time_desc,
                                    size="md",
                                    weight="bold",
                                    color="#FF6B6B",
                                    flex=2,
                                    align="end"
                                )
                            ],
                            margin="sm"
                        ),
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text="👤 性別",
                                    size="md",
                                    color="#666666",
                                    flex=1
                                ),
                                FlexText(
                                    text=gender_text,
                                    size="md",
                                    weight="bold",
                                    color="#333333",
                                    flex=2,
                                    align="end"
                                )
                            ],
                            margin="sm"
                        )
                    ],
                    margin="md"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 確認按鈕
                FlexButton(
                    action=PostbackAction(
                        label="🔮 開始占卜",
                        data=f"confirm_divination|{selected_time.isoformat()}|{gender}"
                    ),
                    style="primary",
                    color="#FF6B6B",
                    height="md",
                    margin="md"
                ),
                
                # 重新選擇按鈕
                FlexButton(
                    action=PostbackAction(
                        label="🔄 重新選擇時間",
                        data=f"reselect_time|{gender}"
                    ),
                    style="secondary",
                    height="sm",
                    margin="sm"
                ),
                
                FlexSeparator(margin="lg"),
                
                # 底部說明
                FlexText(
                    text="確認無誤後點擊「開始占卜」",
                    size="sm",
                    color="#999999",
                    align="center",
                    margin="md"
                )
            ]
            
            bubble = FlexBubble(
                size="kilo",
                body=FlexBox(
                    layout="vertical",
                    contents=contents,
                    paddingAll="xl",
                    spacing="none"
                ),
                styles={
                    "body": {
                        "backgroundColor": "#FFFFFF"
                    }
                }
            )
            
            return FlexMessage(
                alt_text="✅ 確認占卜時間",
                contents=bubble
            )
            
        except Exception as e:
            logger.error(f"創建時間確認消息失敗: {e}")
            return None 