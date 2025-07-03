"""
占卜結果 Flex Message 生成器
實現三個區塊的 Carousel 設計：
1. 基本命盤資訊 Carousel (12宮位)
2. 太極點命宮資訊 Carousel (12宮位重新分佈)  
3. 四化解析 Carousel (4個四化)
"""

from typing import Dict, List, Any, Optional
from linebot.v3.messaging import (
    FlexMessage, FlexContainer, FlexCarousel, FlexBubble,
    FlexBox, FlexText, FlexSeparator, FlexFiller
)
import logging

logger = logging.getLogger(__name__)

class DivinationFlexMessageGenerator:
    """占卜結果 Flex Message 生成器"""
    
    # 宮位顏色配置 (12色環)
    PALACE_COLORS = {
        "命宮": "#FF6B6B",    # 紅色
        "兄弟宮": "#4ECDC4",  # 青色  
        "夫妻宮": "#45B7D1",  # 藍色
        "子女宮": "#96CEB4",  # 綠色
        "財帛宮": "#FFEAA7",  # 黃色
        "疾厄宮": "#DDA0DD",  # 紫色
        "遷移宮": "#98D8C8",  # 薄荷綠
        "奴僕宮": "#F7DC6F",  # 金黃
        "官祿宮": "#BB8FCE",  # 淡紫
        "田宅宮": "#85C1E9",  # 天藍
        "福德宮": "#F8C471",  # 橙色
        "父母宮": "#82E0AA"   # 淺綠
    }
    
    # 四化顏色配置
    SIHUA_COLORS = {
        "祿": "#FFD700",  # 金色
        "權": "#FF6B6B",  # 紅色
        "科": "#4ECDC4",  # 青色
        "忌": "#8B4513"   # 棕色
    }
    
    # 四化 emoji
    SIHUA_EMOJIS = {
        "祿": "💰",
        "權": "👑", 
        "科": "🌟",
        "忌": "⚡"
    }
    
    def __init__(self):
        self.palace_order = [
            "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
            "遷移宮", "奴僕宮", "官祿宮", "田宅宮", "福德宮", "父母宮"
        ]
    
    def generate_divination_messages(
        self, 
        result: Dict[str, Any], 
        is_admin: bool = False
    ) -> List[FlexMessage]:
        """
        生成占卜結果消息列表
        
        Args:
            result: 占卜結果數據
            is_admin: 是否為管理員
            
        Returns:
            List[FlexMessage]: 消息列表
        """
        messages = []
        
        try:
            logger.info(f"開始生成占卜Flex消息 - 管理員: {is_admin}")
            
            # 1. 基本資訊摘要 (所有用戶可見)
            logger.info("生成基本資訊摘要...")
            summary_message = self._create_summary_message(result, is_admin)
            if summary_message:
                messages.append(summary_message)
                logger.info("✅ 基本資訊摘要生成成功")
            
            # 2. 基本命盤資訊 (僅管理員可見)
            if is_admin:
                logger.info("生成基本命盤資訊Carousel...")
                basic_chart_message = self._create_basic_chart_carousel(result)
                if basic_chart_message:
                    messages.append(basic_chart_message)
                    logger.info("✅ 基本命盤資訊Carousel生成成功")
                else:
                    logger.warning("⚠️ 基本命盤資訊Carousel生成失敗")
            
            # 3. 太極點命宮資訊 (僅管理員可見)
            if is_admin:
                logger.info("生成太極點命宮資訊Carousel...")
                taichi_message = self._create_taichi_palace_carousel(result)
                if taichi_message:
                    messages.append(taichi_message)
                    logger.info("✅ 太極點命宮資訊Carousel生成成功")
                else:
                    logger.warning("⚠️ 太極點命宮資訊Carousel生成失敗")
            
            # 4. 四化解析 (所有用戶可見)
            logger.info("生成四化解析Carousel...")
            sihua_message = self._create_sihua_carousel(result)
            if sihua_message:
                messages.append(sihua_message)
                logger.info("✅ 四化解析Carousel生成成功")
            else:
                logger.warning("⚠️ 四化解析Carousel生成失敗")
                
            logger.info(f"占卜Flex消息生成完成 - 總計 {len(messages)} 個消息")
                
        except Exception as e:
            logger.error(f"生成占卜Flex消息失敗: {e}")
            logger.error(f"錯誤詳情: {str(e)}")
            
        return messages
    
    def _create_summary_message(self, result: Dict[str, Any], is_admin: bool) -> Optional[FlexMessage]:
        """創建基本資訊摘要"""
        try:
            # 基本資訊
            gender_text = "男性" if result.get("gender") == "M" else "女性"
            divination_time = result.get("divination_time", "")
            taichi_palace = result.get("taichi_palace", "")
            minute_dizhi = result.get("minute_dizhi", "")
            palace_tiangan = result.get("palace_tiangan", "")
            
            # 解析時間
            from datetime import datetime
            if divination_time:
                try:
                    if '+' in divination_time:
                        dt = datetime.fromisoformat(divination_time)
                    else:
                        dt = datetime.fromisoformat(divination_time.replace('Z', '+00:00'))
                    time_str = dt.strftime("%m/%d %H:%M")
                except:
                    time_str = "現在"
            else:
                time_str = "現在"
            
            # 管理員標識
            admin_badge = "👑 管理員" if is_admin else ""
            
            bubble = FlexBubble(
                size="kilo",  # 使用更大的尺寸
                body=FlexBox(
                    layout="vertical",
                    contents=[
                        # 標題
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text="🔮 紫微斗數占卜",
                                    weight="bold",
                                    size="xl",
                                    color="#FF6B6B",
                                    flex=1
                                ),
                                FlexText(
                                    text=admin_badge,
                                    size="sm",
                                    color="#FFD700",
                                    align="end",
                                    flex=0
                                ) if is_admin else FlexFiller()
                            ]
                        ),
                        
                        FlexSeparator(margin="md"),
                        
                        # 占卜基本資訊
                        FlexBox(
                            layout="vertical",
                            contents=[
                                FlexBox(
                                    layout="horizontal",
                                    contents=[
                                        FlexText(text="📅 時間", size="sm", color="#666666", flex=1),
                                        FlexText(text=time_str, size="sm", weight="bold", flex=2, align="end")
                                    ],
                                    margin="md"
                                ),
                                FlexBox(
                                    layout="horizontal",
                                    contents=[
                                        FlexText(text="👤 性別", size="sm", color="#666666", flex=1),
                                        FlexText(text=gender_text, size="sm", weight="bold", flex=2, align="end")
                                    ],
                                    margin="sm"
                                ),
                                FlexBox(
                                    layout="horizontal",
                                    contents=[
                                        FlexText(text="🏰 太極宮", size="sm", color="#666666", flex=1),
                                        FlexText(text=taichi_palace, size="sm", weight="bold", flex=2, align="end")
                                    ],
                                    margin="sm"
                                ),
                                FlexBox(
                                    layout="horizontal",
                                    contents=[
                                        FlexText(text="🕰️ 分鐘支", size="sm", color="#666666", flex=1),
                                        FlexText(text=minute_dizhi, size="sm", weight="bold", flex=2, align="end")
                                    ],
                                    margin="sm"
                                ),
                                FlexBox(
                                    layout="horizontal",
                                    contents=[
                                        FlexText(text="⭐ 宮干", size="sm", color="#666666", flex=1),
                                        FlexText(text=palace_tiangan, size="sm", weight="bold", flex=2, align="end")
                                    ],
                                    margin="sm"
                                )
                            ]
                        ),
                        
                        FlexSeparator(margin="md"),
                        
                        # 四化說明
                        FlexBox(
                            layout="vertical",
                            contents=[
                                FlexText(
                                    text="🔮 四化解析",
                                    weight="bold",
                                    size="lg",
                                    color="#4ECDC4",
                                    margin="md"
                                ),
                                FlexText(
                                    text="💰祿：好運機會 👑權：主導掌控 🌟科：名聲地位 ⚡忌：需要留意",
                                    size="xs",
                                    color="#888888",
                                    wrap=True,
                                    margin="sm"
                                )
                            ]
                        )
                    ],
                    spacing="none",
                    paddingAll="lg"
                )
            )
            
            return FlexMessage(
                alt_text="🔮 紫微斗數占卜結果",
                contents=bubble
            )
            
        except Exception as e:
            logger.error(f"創建摘要消息失敗: {e}")
            return None
    
    def _create_basic_chart_carousel(self, result: Dict[str, Any]) -> Optional[FlexMessage]:
        """創建基本命盤資訊 Carousel"""
        try:
            basic_chart = result.get("basic_chart", {})
            if not basic_chart:
                return None
            
            bubbles = []
            
            # 為每個宮位創建一個 bubble
            for palace_name in self.palace_order:
                palace_data = basic_chart.get(palace_name, {})
                if not palace_data:
                    continue
                    
                bubble = self._create_palace_bubble(palace_name, palace_data)
                if bubble:
                    bubbles.append(bubble)
            
            if not bubbles:
                return None
            
            # 限制最多12個bubble
            bubbles = bubbles[:12]
            
            carousel = FlexCarousel(contents=bubbles)
            
            return FlexMessage(
                alt_text="🏛️ 基本命盤資訊",
                contents=carousel
            )
            
        except Exception as e:
            logger.error(f"創建基本命盤Carousel失敗: {e}")
            return None
    
    def _create_taichi_palace_carousel(self, result: Dict[str, Any]) -> Optional[FlexMessage]:
        """創建太極點命宮資訊 Carousel"""
        try:
            taichi_mapping = result.get("taichi_palace_mapping", {})
            basic_chart = result.get("basic_chart", {})
            
            if not taichi_mapping or not basic_chart:
                return None
            
            bubbles = []
            
            # 根據太極點重新分佈創建bubble
            for original_branch, new_palace_name in taichi_mapping.items():
                # 找到原始地支對應的宮位數據
                palace_data = None
                for palace_name, data in basic_chart.items():
                    if data.get("dizhi") == original_branch:
                        palace_data = data
                        break
                
                if palace_data:
                    bubble = self._create_palace_bubble(
                        new_palace_name, 
                        palace_data, 
                        is_taichi=True
                    )
                    if bubble:
                        bubbles.append(bubble)
            
            if not bubbles:
                return None
            
            # 限制最多12個bubble  
            bubbles = bubbles[:12]
            
            carousel = FlexCarousel(contents=bubbles)
            
            return FlexMessage(
                alt_text="🎯 太極點命宮資訊",
                contents=carousel
            )
            
        except Exception as e:
            logger.error(f"創建太極點Carousel失敗: {e}")
            return None
    
    def _create_sihua_carousel(self, result: Dict[str, Any]) -> Optional[FlexMessage]:
        """創建四化解析 Carousel"""
        try:
            sihua_results = result.get("sihua_results", [])
            if not sihua_results:
                return None
            
            # 按四化類型分組
            sihua_groups = {"祿": [], "權": [], "科": [], "忌": []}
            
            for sihua_info in sihua_results:
                sihua_type = sihua_info.get("type", "")
                if sihua_type in sihua_groups:
                    sihua_groups[sihua_type].append(sihua_info)
            
            bubbles = []
            
            # 為每個四化類型創建bubble
            for sihua_type in ["祿", "權", "科", "忌"]:
                sihua_list = sihua_groups[sihua_type]
                if sihua_list:
                    bubble = self._create_sihua_bubble(sihua_type, sihua_list)
                    if bubble:
                        bubbles.append(bubble)
            
            if not bubbles:
                return None
            
            carousel = FlexCarousel(contents=bubbles)
            
            return FlexMessage(
                alt_text="🔮 四化解析",
                contents=carousel
            )
            
        except Exception as e:
            logger.error(f"創建四化Carousel失敗: {e}")
            return None
    
    def _create_palace_bubble(
        self, 
        palace_name: str, 
        palace_data: Dict[str, Any], 
        is_taichi: bool = False
    ) -> Optional[FlexBubble]:
        """創建宮位 bubble (模擬命盤格子)"""
        try:
            color = self.PALACE_COLORS.get(palace_name, "#95A5A6")
            
            # 獲取宮位資訊
            tiangan = str(palace_data.get("tiangan", ""))
            dizhi = str(palace_data.get("dizhi", ""))
            stars = palace_data.get("stars", [])
            
            # 主星和輔星分離
            main_stars = []
            minor_stars = []
            
            for star in stars[:8]:  # 增加到8顆星
                star_str = str(star)
                if any(main in star_str for main in ["紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"]):
                    main_stars.append(star_str)
                else:
                    minor_stars.append(star_str)
            
            # 構建bubble內容
            body_contents = []
            
            # 宮位名稱 (頂部)
            body_contents.append(
                FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text=str(palace_name),
                            weight="bold",
                            size="lg",  # 增大字體
                            color=color,
                            align="center"
                        )
                    ],
                    backgroundColor="#F8F9FA",
                    cornerRadius="md",
                    paddingAll="sm"
                )
            )
            
            # 天干地支 (左右排列)
            body_contents.append(
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(
                            text=f"{tiangan}",
                            size="sm",
                            color="#333333",
                            weight="bold",
                            flex=1
                        ),
                        FlexText(
                            text=f"{dizhi}",
                            size="sm", 
                            color="#333333",
                            weight="bold",
                            flex=1,
                            align="end"
                        )
                    ],
                    margin="sm"
                )
            )
            
            # 主星
            if main_stars:
                body_contents.append(
                    FlexText(
                        text="【主星】",
                        size="xs",
                        color="#FF6B6B",
                        weight="bold",
                        margin="sm"
                    )
                )
                # 將主星分行顯示，每行最多2顆
                for i in range(0, len(main_stars), 2):
                    star_line = main_stars[i:i+2]
                    if len(star_line) == 2:
                        body_contents.append(
                            FlexBox(
                                layout="horizontal",
                                contents=[
                                    FlexText(
                                        text=star_line[0],
                                        size="xs",
                                        color="#444444",
                                        flex=1
                                    ),
                                    FlexText(
                                        text=star_line[1],
                                        size="xs",
                                        color="#444444",
                                        flex=1,
                                        align="end"
                                    )
                                ],
                                margin="xs"
                            )
                        )
                    else:
                        body_contents.append(
                            FlexText(
                                text=star_line[0],
                                size="xs",
                                color="#444444",
                                margin="xs"
                            )
                        )
            
            # 輔星
            if minor_stars:
                body_contents.append(
                    FlexText(
                        text="【輔星】",
                        size="xs",
                        color="#4ECDC4",
                        weight="bold",
                        margin="sm"
                    )
                )
                # 將輔星分行顯示，每行最多2顆
                for i in range(0, min(len(minor_stars), 4), 2):  # 最多顯示4顆輔星
                    star_line = minor_stars[i:i+2]
                    if len(star_line) == 2:
                        body_contents.append(
                            FlexBox(
                                layout="horizontal",
                                contents=[
                                    FlexText(
                                        text=star_line[0],
                                        size="xs",
                                        color="#666666",
                                        flex=1
                                    ),
                                    FlexText(
                                        text=star_line[1],
                                        size="xs",
                                        color="#666666",
                                        flex=1,
                                        align="end"
                                    )
                                ],
                                margin="xs"
                            )
                        )
                    else:
                        body_contents.append(
                            FlexText(
                                text=star_line[0],
                                size="xs",
                                color="#666666",
                                margin="xs"
                            )
                        )
            
            # 太極點標記
            if is_taichi:
                body_contents.append(
                    FlexText(
                        text="🎯 太極重分",
                        size="xs",
                        color="#FF6B6B",
                        weight="bold",
                        align="center",
                        margin="sm"
                    )
                )
            
            bubble = FlexBubble(
                size="nano",  # 使用更小的尺寸讓更多內容可見
                body=FlexBox(
                    layout="vertical",
                    contents=body_contents,
                    spacing="none",
                    paddingAll="sm"  # 減少內邊距
                ),
                styles={
                    "body": {
                        "backgroundColor": "#FFFFFF"
                    }
                }
            )
            
            return bubble
            
        except Exception as e:
            logger.error(f"創建宮位bubble失敗: {e}")
            return None
    
    def _create_sihua_bubble(self, sihua_type: str, sihua_list: List[Dict[str, Any]]) -> Optional[FlexBubble]:
        """創建四化 bubble"""
        try:
            color = self.SIHUA_COLORS.get(sihua_type, "#95A5A6")
            emoji = self.SIHUA_EMOJIS.get(sihua_type, "⭐")
            
            body_contents = []
            
            # 四化標題
            body_contents.append(
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(
                            text=str(emoji),
                            size="xl",  # 增大 emoji 尺寸
                            flex=0
                        ),
                        FlexText(
                            text=f"{str(sihua_type)}星",
                            weight="bold",
                            size="xl",  # 增大標題字體
                            color=color,
                            flex=1,
                            margin="sm"
                        )
                    ],
                    backgroundColor="#F8F9FA",
                    cornerRadius="md",
                    paddingAll="md"  # 增加內邊距
                )
            )
            
            # 四化星曜列表
            for sihua_info in sihua_list:
                star = str(sihua_info.get("star", ""))
                palace = str(sihua_info.get("palace", ""))
                explanation = str(sihua_info.get("explanation", ""))
                
                # 添加分隔線
                body_contents.append(FlexSeparator(margin="md"))
                
                # 星曜和宮位
                body_contents.append(
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text=f"⭐ {star}",
                                weight="bold",
                                size="md",  # 增大字體
                                color="#333333",
                                flex=2
                            ),
                            FlexText(
                                text=f"📍 {palace}",
                                size="md",  # 增大字體
                                color="#666666",
                                weight="bold",
                                flex=2,
                                align="end"
                            )
                        ],
                        margin="md"
                    )
                )
                
                # 解釋內容 (完整版)
                if explanation:
                    # 分段顯示解釋內容
                    explanation_parts = explanation.split('。')
                    for i, part in enumerate(explanation_parts[:3]):  # 最多顯示3段
                        if part.strip():
                            body_contents.append(
                                FlexText(
                                    text=f"• {part.strip()}。",
                                    size="sm",  # 增大字體
                                    color="#444444",
                                    wrap=True,
                                    margin="sm"
                                )
                            )
                    
                    # 如果內容太長，添加省略號
                    if len(explanation_parts) > 3:
                        body_contents.append(
                            FlexText(
                                text="...",
                                size="sm",
                                color="#888888",
                                align="center",
                                margin="xs"
                            )
                        )
            
            bubble = FlexBubble(
                size="mega",  # 使用最大尺寸以容納更多內容
                body=FlexBox(
                    layout="vertical",
                    contents=body_contents,
                    spacing="none",
                    paddingAll="lg"  # 增加內邊距
                ),
                styles={
                    "body": {
                        "backgroundColor": "#FFFFFF"
                    }
                }
            )
            
            return bubble
            
        except Exception as e:
            logger.error(f"創建四化bubble失敗: {e}")
            return None 