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
        """創建宮位 bubble (模擬命盤格子) - 優化尺寸和顯示"""
        try:
            color = self.PALACE_COLORS.get(palace_name, "#95A5A6")
            
            # 獲取宮位資訊
            tiangan = str(palace_data.get("tiangan", ""))
            dizhi = str(palace_data.get("dizhi", ""))
            stars = palace_data.get("stars", [])
            
            # 主星和輔星分離
            main_stars = []
            minor_stars = []
            
            for star in stars:  # 顯示所有星曜
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
                            size="xxl",  # 加大宮位名稱字體
                            color=color,
                            align="center"
                        )
                    ],
                    backgroundColor="#F8F9FA",
                    cornerRadius="md",
                    paddingAll="md"  # 增加內邊距
                )
            )
            
            # 天干地支 (左右排列)
            body_contents.append(
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(
                            text=f"{tiangan}",
                            size="md",  # 加大天干地支字體
                            color="#333333",
                            weight="bold",
                            flex=1
                        ),
                        FlexText(
                            text=f"{dizhi}",
                            size="md", 
                            color="#333333",
                            weight="bold",
                            flex=1,
                            align="end"
                        )
                    ],
                    margin="md"
                )
            )
            
            # 主星 - 優化顯示，確保不被遮擋
            if main_stars:
                body_contents.append(
                    FlexText(
                        text="【主星】",
                        size="sm",  # 稍微加大標籤字體
                        color="#FF6B6B",
                        weight="bold",
                        margin="md"
                    )
                )
                # 主星單行顯示，每行最多2顆，確保完整顯示
                for i in range(0, len(main_stars), 2):
                    star_line = main_stars[i:i+2]
                    if len(star_line) == 2:
                        body_contents.append(
                            FlexBox(
                                layout="horizontal",
                                contents=[
                                    FlexText(
                                        text=star_line[0][:10],  # 適當字數限制
                                        size="sm",  # 加大主星字體
                                        color="#444444",
                                        weight="bold",
                                        flex=1
                                    ),
                                    FlexText(
                                        text=star_line[1][:10],
                                        size="sm",
                                        color="#444444",
                                        weight="bold",
                                        flex=1,
                                        align="end"
                                    )
                                ],
                                margin="sm"
                            )
                        )
                    else:
                        body_contents.append(
                            FlexText(
                                text=star_line[0][:15],
                                size="sm",
                                color="#444444",
                                weight="bold",
                                margin="sm"
                            )
                        )
            
            # 輔星 - 增加顯示空間
            if minor_stars:
                body_contents.append(
                    FlexText(
                        text="【輔星】",
                        size="sm",
                        color="#4ECDC4",
                        weight="bold",
                        margin="md"
                    )
                )
                # 輔星分行顯示，每行最多2顆（確保可讀性）
                for i in range(0, min(len(minor_stars), 8), 2):  # 最多顯示8顆輔星
                    star_line = minor_stars[i:i+2]
                    if len(star_line) == 2:
                        body_contents.append(
                            FlexBox(
                                layout="horizontal",
                                contents=[
                                    FlexText(
                                        text=star_line[0][:8],
                                        size="xs",
                                        color="#666666",
                                        flex=1
                                    ),
                                    FlexText(
                                        text=star_line[1][:8],
                                        size="xs",
                                        color="#666666",
                                        flex=1,
                                        align="end"
                                    )
                                ],
                                margin="sm"
                            )
                        )
                    else:
                        body_contents.append(
                            FlexText(
                                text=star_line[0][:12],
                                size="xs",
                                color="#666666",
                                margin="sm"
                            )
                        )
                
                # 如果輔星太多，顯示省略提示
                if len(minor_stars) > 8:
                    body_contents.append(
                        FlexText(
                            text=f"...及其他{len(minor_stars)-8}顆星",
                            size="xxs",
                            color="#999999",
                            align="center",
                            margin="sm"
                        )
                    )
            
            # 太極點標記
            if is_taichi:
                body_contents.append(
                    FlexText(
                        text="🎯 太極重分",
                        size="sm",
                        color="#FF6B6B",
                        weight="bold",
                        align="center",
                        margin="md"
                    )
                )
            
            bubble = FlexBubble(
                size="giga",  # 使用超大尺寸，確保內容不被遮擋
                body=FlexBox(
                    layout="vertical",
                    contents=body_contents,
                    spacing="none",
                    paddingAll="lg"  # 增加內邊距，給內容更多空間
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
        """創建四化 bubble - 分層顯示設計"""
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
                            size="xxl",  # 加大 emoji
                            flex=0
                        ),
                        FlexText(
                            text=f"{str(sihua_type)}星解析",
                            weight="bold",
                            size="xxl",  # 加大標題
                            color=color,
                            flex=1,
                            margin="md"
                        )
                    ],
                    backgroundColor="#F8F9FA",
                    cornerRadius="md",
                    paddingAll="lg"  # 增加內邊距
                )
            )
            
            # 第一層：核心信息顯示
            body_contents.append(
                FlexText(
                    text="✨ 核心信息",
                    size="lg",
                    weight="bold",
                    color="#333333",
                    margin="lg"
                )
            )
            
            # 星曜概要列表
            for i, sihua_info in enumerate(sihua_list):
                if i >= 2:  # 第一層最多顯示2個，保持簡潔
                    break
                    
                star = str(sihua_info.get("star", ""))
                palace = str(sihua_info.get("palace", ""))
                explanation = str(sihua_info.get("explanation", ""))
                
                # 添加分隔線
                if i > 0:
                    body_contents.append(FlexSeparator(margin="md"))
                
                # 星曜和宮位 - 核心信息
                body_contents.append(
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text=f"⭐ {star}",
                                weight="bold",
                                size="lg",  # 加大字體
                                color="#333333",
                                flex=2
                            ),
                            FlexText(
                                text=f"📍 {palace}",
                                size="lg",  # 加大字體
                                color="#666666",
                                weight="bold",
                                flex=2,
                                align="end"
                            )
                        ],
                        margin="md"
                    )
                )
                
                # 核心現象 - 只顯示最重要的信息
                if explanation:
                    # 提取關鍵信息（通常在開頭）
                    key_info = self._extract_key_info(explanation, sihua_type)
                    if key_info:
                        body_contents.append(
                            FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text="🎯 核心現象",
                                        size="sm",
                                        color="#888888",
                                        weight="bold",
                                        margin="sm"
                                    ),
                                    FlexText(
                                        text=key_info,
                                        size="md",
                                        color="#444444",
                                        wrap=True,
                                        margin="xs"
                                    )
                                ]
                            )
                        )
            
            # 如果有更多星曜，顯示數量提示
            if len(sihua_list) > 2:
                body_contents.append(
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexSeparator(margin="lg"),
                            FlexText(
                                text=f"+ 另有 {len(sihua_list) - 2} 顆{sihua_type}星",
                                size="md",
                                color="#888888",
                                align="center",
                                margin="md"
                            )
                        ]
                    )
                )
            
            # 第二層：展開按鈕
            body_contents.append(
                FlexBox(
                    layout="vertical",
                    contents=[
                        FlexSeparator(margin="lg"),
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text="📖 查看完整解釋",
                                    size="md",
                                    color="#FFFFFF",
                                    weight="bold",
                                    align="center",
                                    flex=1
                                )
                            ],
                            backgroundColor=color,
                            cornerRadius="md",
                            paddingAll="md",
                            margin="md",
                            action={
                                "type": "message", 
                                "text": f"查看{sihua_type}星完整解釋"
                            }
                        )
                    ]
                )
            )
            
            # 底部說明
            body_contents.append(
                FlexText(
                    text=self._get_sihua_description(sihua_type),
                    size="sm",
                    color="#999999",
                    wrap=True,
                    align="center",
                    margin="lg"
                )
            )
            
            bubble = FlexBubble(
                size="giga",  # 使用超大尺寸
                body=FlexBox(
                    layout="vertical",
                    contents=body_contents,
                    spacing="none",
                    paddingAll="xl"  # 增加內邊距
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
    
    def _extract_key_info(self, explanation: str, sihua_type: str) -> str:
        """提取四化的關鍵信息"""
        try:
            if not explanation:
                return ""
                
            # 分割句子
            sentences = explanation.split('。')
            
            # 根據四化類型提取關鍵詞句
            key_words = {
                "祿": ["財運", "收入", "機會", "好運", "順利", "賺錢", "利益"],
                "權": ["權力", "主導", "領導", "掌控", "管理", "決策", "影響力"],
                "科": ["名聲", "地位", "聲望", "學習", "考試", "文化", "名氣"],
                "忌": ["阻礙", "困難", "小心", "注意", "不利", "問題", "挑戰"]
            }
            
            target_words = key_words.get(sihua_type, [])
            
            # 找出包含關鍵詞的重要句子
            key_sentences = []
            for sentence in sentences[:3]:  # 只查看前3句
                if sentence.strip():
                    for word in target_words:
                        if word in sentence:
                            key_sentences.append(sentence.strip())
                            break
            
            # 如果沒有找到關鍵句，就用前兩句
            if not key_sentences:
                key_sentences = [s.strip() for s in sentences[:2] if s.strip()]
            
            # 組合關鍵信息，限制長度
            result = "。".join(key_sentences[:2])
            if len(result) > 80:
                result = result[:80] + "..."
            
            return result + "。" if result and not result.endswith("。") else result
            
        except Exception as e:
            logger.error(f"提取關鍵信息失敗: {e}")
            return explanation[:50] + "..." if len(explanation) > 50 else explanation
    
    def _get_sihua_description(self, sihua_type: str) -> str:
        """獲取四化類型的簡要說明"""
        descriptions = {
            "祿": "💰 祿星代表好運與財富，是吉利的象徵",
            "權": "👑 權星代表權力與主導，具有領導特質", 
            "科": "🌟 科星代表名聲與地位，利於學習考試",
            "忌": "⚡ 忌星代表阻礙與挑戰，需要特別留意"
        }
        return descriptions.get(sihua_type, "✨ 四化影響運勢走向")
    
    def generate_sihua_detail_message(
        self, 
        sihua_type: str, 
        sihua_list: List[Dict[str, Any]]
    ) -> Optional[FlexMessage]:
        """
        生成四化詳細解釋消息
        
        Args:
            sihua_type: 四化類型 (祿/權/科/忌)
            sihua_list: 該四化的星曜列表
            
        Returns:
            包含完整解釋的 FlexMessage
        """
        try:
            color = self.SIHUA_COLORS.get(sihua_type, "#95A5A6")
            emoji = self.SIHUA_EMOJIS.get(sihua_type, "⭐")
            
            body_contents = []
            
            # 詳細解釋標題
            body_contents.append(
                FlexBox(
                    layout="horizontal",
                    contents=[
                        FlexText(
                            text=str(emoji),
                            size="xxl",
                            flex=0
                        ),
                        FlexText(
                            text=f"{str(sihua_type)}星完整解釋",
                            weight="bold",
                            size="xl",
                            color=color,
                            flex=1,
                            margin="md"
                        )
                    ],
                    backgroundColor="#F8F9FA",
                    cornerRadius="md",
                    paddingAll="lg"
                )
            )
            
            # 四化總體說明
            body_contents.append(
                FlexBox(
                    layout="vertical",
                    contents=[
                        FlexText(
                            text="📋 總體說明",
                            size="lg",
                            weight="bold",
                            color="#333333",
                            margin="lg"
                        ),
                        FlexText(
                            text=self._get_detailed_sihua_description(sihua_type),
                            size="md",
                            color="#444444",
                            wrap=True,
                            margin="sm"
                        )
                    ]
                )
            )
            
            # 詳細星曜解釋
            for i, sihua_info in enumerate(sihua_list):
                star = str(sihua_info.get("star", ""))
                palace = str(sihua_info.get("palace", ""))
                explanation = str(sihua_info.get("explanation", ""))
                
                # 添加分隔線
                body_contents.append(FlexSeparator(margin="lg"))
                
                # 星曜標題
                body_contents.append(
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text=f"⭐ {star}",
                                weight="bold",
                                size="lg",
                                color="#333333",
                                flex=2
                            ),
                            FlexText(
                                text=f"📍 {palace}",
                                size="md",
                                color="#666666",
                                weight="bold",
                                flex=2,
                                align="end"
                            )
                        ],
                        margin="md"
                    )
                )
                
                # 完整解釋內容
                if explanation:
                    # 將解釋分段顯示
                    explanation_parts = explanation.split('。')
                    
                    for j, part in enumerate(explanation_parts):
                        if part.strip():
                            # 區分不同類型的內容
                            if any(keyword in part for keyword in ["心理", "個性", "性格"]):
                                label = "🧠 心理特質"
                                label_color = "#9B59B6"
                            elif any(keyword in part for keyword in ["現象", "表現", "行為"]):
                                label = "🎭 外在表現"
                                label_color = "#3498DB"
                            elif any(keyword in part for keyword in ["事件", "發生", "情況"]):
                                label = "📅 可能事件"
                                label_color = "#E67E22"
                            elif any(keyword in part for keyword in ["提示", "建議", "注意"]):
                                label = "💡 建議提示"
                                label_color = "#27AE60"
                            else:
                                label = "📝 詳細說明"
                                label_color = "#7F8C8D"
                            
                            # 只在第一段或內容類型改變時顯示標籤
                            if j == 0 or (j > 0 and len(part.strip()) > 20):
                                body_contents.append(
                                    FlexText(
                                        text=label,
                                        size="sm",
                                        color=label_color,
                                        weight="bold",
                                        margin="md" if j == 0 else "lg"
                                    )
                                )
                            
                            body_contents.append(
                                FlexText(
                                    text=part.strip() + "。",
                                    size="sm",
                                    color="#444444",
                                    wrap=True,
                                    margin="sm"
                                )
                            )
            
            # 底部總結
            body_contents.append(
                FlexBox(
                    layout="vertical",
                    contents=[
                        FlexSeparator(margin="lg"),
                        FlexText(
                            text="📖 以上為完整的四化解釋內容",
                            size="sm",
                            color="#999999",
                            align="center",
                            margin="lg"
                        )
                    ]
                )
            )
            
            bubble = FlexBubble(
                size="giga",
                body=FlexBox(
                    layout="vertical",
                    contents=body_contents,
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
                alt_text=f"🔮 {sihua_type}星完整解釋",
                contents=bubble
            )
            
        except Exception as e:
            logger.error(f"生成四化詳細解釋失敗: {e}")
            return None
    
    def _get_detailed_sihua_description(self, sihua_type: str) -> str:
        """獲取四化類型的詳細說明"""
        descriptions = {
            "祿": "祿星為四化之首，代表財富、福祿、好運與機會。當星曜化祿時，通常表示在該領域能得到好的發展，有賺錢的機會，做事順利，容易得到貴人幫助。祿星也代表緣分與人際關係的和諧。",
            "權": "權星代表權力、領導力、主導權與掌控能力。化權的星曜會增強其主導性，使人在該領域具有領導才能，但也可能變得強勢或固執。權星有助於事業發展和地位提升，但需注意不要過於專斷。",
            "科": "科星代表名聲、聲望、文化、學習與考試運。化科的星曜能提升個人的名氣和社會地位，有利於學習進修、考試升學，也代表文化修養和專業能力的提升。科星也象徵貴人相助和良好的社會形象。",
            "忌": "忌星代表阻礙、困難、執著與不順利。化忌並非完全凶惡，而是提醒需要特別留意的地方。忌星會帶來挑戰和考驗，但也能促使人成長和學習。關鍵在於如何化解和轉化這些困難。"
        }
        return descriptions.get(sihua_type, "四化星對運勢產生重要影響，需要仔細分析其作用力。") 