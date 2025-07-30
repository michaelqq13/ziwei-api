"""
占卜結果 Flex Message 生成器
實現三個區塊的 Carousel 設計：
1. 基本命盤資訊 Carousel (12宮位)
2. 太極點命宮資訊 Carousel (12宮位重新分佈)  
3. 四化解析 Carousel (4個四化)
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from linebot.v3.messaging import (
    FlexMessage, FlexContainer, FlexCarousel, FlexBubble,
    FlexBox, FlexText, FlexSeparator, FlexFiller, MessageAction, TextMessage
)
import logging
import os
import time

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
        "交友宮": "#F7DC6F",  # 金黃
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
        # 星空主題色彩配置
        self.colors = {
            "primary": "#4A90E2",
            "secondary": "#FFD700", 
            "accent": "#9B59B6",
            "background": "#1A1A2E",
            "card_bg": "#16213E",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B0C4DE",
            "star_gold": "#FFD700"
        }
        
        # 基礎URL，用於構建靜態資源的完整路徑
        base_url = os.getenv("BASE_URL", "").rstrip('/')
        # 快取破壞者，確保LINE每次都重新載入圖片
        cache_buster = f"?v={int(time.time())}"
        
        # 從環境變數讀取背景圖片 URL，如果未設定則使用預設值
        self.background_images = {
            "basic": "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1040&h=600&q=80",
            "premium": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1040&h=600&q=80",
            "admin": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?ixlib=rb-4.0.3&auto=format&fit=crop&w=1040&h=600&q=80"
        }
        
        # 備用背景圖片
        self.fallback_images = {
            "basic": "https://via.placeholder.com/1040x600/1A1A2E/FFD700?text=🔮+占卜結果+🔮",
            "premium": "https://via.placeholder.com/1040x600/2C3E50/E67E22?text=💎+會員結果+💎",
            "admin": "https://via.placeholder.com/1040x600/8B0000/FFD700?text=��+管理員+👑"
        }
        
        self.palace_order = [
            "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
            "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"
        ]
    
    @staticmethod
    def clean_sihua_explanation(text: str) -> str:
        """清理四化解釋文字，保留基本標點，清理裝飾性標點"""
        if not text:
            return text
        
        # 定義需要清理的裝飾性標點符號
        unwanted_punctuation = {
            '★', '☆', '※', '○', '●', '□', '■', '◆', '◇', '△', '▲', '▽', '▼',
            '「', '」', '『', '』', '"', '"', ''', ''', '"', "'", '〈', '〉', '《', '》',
            '（', '）', '(', ')', '【', '】', '[', ']', '〔', '〕', '{', '}',
            '～', '~', '…', '－', '—', '·', '_', '*', '#', '@', '&', '%', 
            '$', '^', '+', '=', '|', '\\', '/', '`'
        }
        
        # 清理文字，保留基本標點符號（逗號、句號、冒號、分號、問號、驚嘆號）
        cleaned_text = ''
        for char in text:
            if char in unwanted_punctuation:
                # 跳過裝飾性標點符號
                continue
            else:
                cleaned_text += char
        
        # 清理多餘的空格
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text

    def generate_divination_messages(
        self, 
        result: Dict[str, Any], 
        is_admin: bool = False,
        user_type: str = "free"  # 新增用戶類型參數：admin, premium, free
    ) -> List[FlexMessage]:
        """
        生成占卜結果消息列表 - 根據用戶類型控制顯示內容
        
        Args:
            result: 占卜結果數據
            is_admin: 是否為管理員（向下兼容）
            user_type: 用戶類型 - "admin"(管理員), "premium"(付費會員), "free"(免費會員)
            
        Returns:
            List[FlexMessage]: 消息列表
        """
        messages = []
        
        try:
            # 如果 is_admin 為 True，則覆蓋 user_type 為 admin
            if is_admin:
                user_type = "admin"
            
            logger.info(f"開始生成占卜Flex消息 - 用戶類型: {user_type}")
            
            # 1. 基本資訊摘要 - 所有用戶都可見，但內容根據用戶類型不同
            logger.info("生成基本資訊摘要...")
            summary_message = self._create_summary_message(result, user_type)
            if summary_message:
                messages.append(summary_message)
                logger.info("✅ 基本資訊摘要生成成功")
            
            # 2. 基本命盤資訊 (僅管理員可見) -> 已改為手動按鈕觸發
            # if user_type == "admin":
            #     logger.info("生成基本命盤資訊Carousel...")
            #     basic_chart_message = self._create_basic_chart_carousel(result)
            #     if basic_chart_message:
            #         messages.append(basic_chart_message)
            #         logger.info("✅ 基本命盤資訊Carousel生成成功")
            #     else:
            #         logger.warning("⚠️ 基本命盤資訊Carousel生成失敗")
            
            # 3. 太極點命宮資訊 已移除自動顯示，改為透過按鈕調用
            # 管理員可以透過快速按鈕「🏛️ 太極十二宮」查看詳細資訊
            
            # 4. 四化解析 (所有用戶可見，但內容不同)
            logger.info("生成四化解析Carousel...")
            sihua_message = self._create_sihua_carousel(result, user_type)
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
    
    def _create_summary_message(self, result: Dict[str, Any], user_type: str) -> Optional[FlexMessage]:
        """創建基本資訊摘要 - 根據用戶類型顯示不同內容"""
        try:
            # 基本資訊
            gender_text = "男性" if result.get("gender") == "M" else "女性"
            divination_time = result.get("divination_time", "")
            taichi_palace = result.get("taichi_palace", "")
            minute_dizhi = result.get("minute_dizhi", "")
            palace_tiangan = result.get("palace_tiangan", "")
            
            # 解析時間
            from datetime import datetime, timezone, timedelta
            if divination_time:
                try:
                    # 解析 ISO 格式時間
                    if '+' in divination_time or 'Z' in divination_time:
                        dt = datetime.fromisoformat(divination_time.replace('Z', '+00:00'))
                    else:
                        dt = datetime.fromisoformat(divination_time)
                    
                    # 確保轉換為台北時間
                    taipei_tz = timezone(timedelta(hours=8))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=taipei_tz)
                    else:
                        dt = dt.astimezone(taipei_tz)
                    
                    # 顯示完整日期時間格式
                    time_str = dt.strftime("%m/%d %H:%M (台北)")
                except Exception as e:
                    logger.warning(f"時間解析失敗: {divination_time}, 錯誤: {e}")
                    time_str = "現在"
            else:
                time_str = "現在"
            
            # 根據用戶類型設置標識
            if user_type == "admin":
                badge = "👑 管理員"
                badge_color = "#FFD700"
            elif user_type == "premium":
                badge = "💎 付費會員"
                badge_color = "#9B59B6"
            else:
                badge = ""
                badge_color = "#666666"
            
            # 構建基本資訊內容
            basic_info_contents = [
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
                )
            ]
            
            # 管理員顯示部分額外資訊，但排除太極宮，因其已有專屬按鈕
            if user_type == "admin":
                basic_info_contents.extend([
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
                ])
            
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
                                    text=badge,
                                    size="sm",
                                    color=badge_color,
                                    align="end",
                                    flex=0
                                ) if badge else FlexFiller()
                            ]
                        ),
                        
                        FlexSeparator(margin="md"),
                        
                        # 占卜基本資訊
                        FlexBox(
                            layout="vertical",
                            contents=basic_info_contents
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
        """創建基本命盤資訊 Carousel - 通過調整順序實現逆時針顯示"""
        try:
            basic_chart = result.get("basic_chart", {})
            if not basic_chart:
                return None
            
            bubbles = []
            
            # 傳統順序的宮位名稱
            traditional_order = [
                "命宮", "父母", "福德", "田宅", "官祿", "交友",
                "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"
            ]
            
            # 先按傳統順序創建所有bubble
            traditional_bubbles = []
            for palace_name in traditional_order:
                palace_data = basic_chart.get(palace_name, {})
                if not palace_data:
                    continue
                    
                bubble = self._create_palace_bubble(palace_name, palace_data)
                if bubble:
                    traditional_bubbles.append(bubble)
            
            # 如果沒有bubble，直接返回
            if not traditional_bubbles:
                return None
            
            # 調整順序：1, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
            # 即：命宮(1), 兄弟(12), 夫妻(11), 子女(10), 財帛(9), 疾厄(8), 遷移(7), 交友(6), 官祿(5), 田宅(4), 福德(3), 父母(2)
            reordered_bubbles = []
            if len(traditional_bubbles) >= 1:
                reordered_bubbles.append(traditional_bubbles[0])  # 命宮(1)
            
            # 從最後一個往前加
            for i in range(len(traditional_bubbles) - 1, 0, -1):
                reordered_bubbles.append(traditional_bubbles[i])
            
            # 限制最多12個bubble
            bubbles = reordered_bubbles[:12]
            
            carousel = FlexCarousel(contents=bubbles)
            
            return FlexMessage(
                alt_text="🏛️ 基本命盤資訊",
                contents=carousel
            )
            
        except Exception as e:
            logger.error(f"創建基本命盤Carousel失敗: {e}")
            return None
    
    def _create_taichi_palace_carousel(self, result: Dict[str, Any]) -> Optional[FlexMessage]:
        """創建太極點命宮資訊 Carousel - 通過調整順序實現逆時針顯示"""
        try:
            taichi_mapping = result.get("taichi_palace_mapping", {})
            basic_chart = result.get("basic_chart", {})
            
            logger.info(f"太極宮映射: {taichi_mapping}")
            logger.info(f"基本命盤宮位: {list(basic_chart.keys())}")
            
            if not taichi_mapping or not basic_chart:
                logger.error(f"數據不完整 - 太極映射: {bool(taichi_mapping)}, 基本命盤: {bool(basic_chart)}")
                return None
            
            # 太極點的傳統順序
            taichi_traditional_order = [
                "命宮", "父母宮", "福德宮", "田宅宮", "官祿宮", "交友宮",
                "遷移宮", "疾厄宮", "財帛宮", "子女宮", "夫妻宮", "兄弟宮"
            ]
            
            # 先按傳統順序創建所有bubble
            traditional_bubbles = []
            for new_palace_name in taichi_traditional_order:
                # 找到對應的原始地支
                original_branch = None
                for orig_branch, mapped_palace in taichi_mapping.items():
                    if mapped_palace == new_palace_name:
                        original_branch = orig_branch
                        break
                
                if not original_branch:
                    logger.warning(f"未找到宮位 {new_palace_name} 對應的原始地支")
                    continue
                
                logger.info(f"處理宮位: {new_palace_name} <- 原地支: {original_branch}")
                
                # 找到原始地支對應的宮位數據
                palace_data = None
                for palace_name, data in basic_chart.items():
                    palace_dizhi = data.get("dizhi", "")
                    logger.debug(f"檢查宮位 {palace_name}: dizhi={palace_dizhi}")
                    if palace_dizhi == original_branch:
                        palace_data = data
                        logger.info(f"找到匹配: {palace_name} (dizhi={palace_dizhi}) -> {new_palace_name}")
                        break
                
                if palace_data:
                    bubble = self._create_palace_bubble(
                        new_palace_name, 
                        palace_data, 
                        is_taichi=True
                    )
                    if bubble:
                        traditional_bubbles.append(bubble)
                        logger.info(f"成功創建 {new_palace_name} bubble")
                    else:
                        logger.warning(f"創建 {new_palace_name} bubble 失敗")
                else:
                    logger.error(f"未找到地支 {original_branch} 對應的宮位數據")
            
            # 如果沒有bubble，直接返回
            if not traditional_bubbles:
                logger.error("沒有成功創建任何 bubble")
                return None
            
            # 調整順序：1, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
            reordered_bubbles = []
            if len(traditional_bubbles) >= 1:
                reordered_bubbles.append(traditional_bubbles[0])  # 命宮(1)
            
            # 從最後一個往前加
            for i in range(len(traditional_bubbles) - 1, 0, -1):
                reordered_bubbles.append(traditional_bubbles[i])
            
            # 限制最多12個bubble  
            bubbles = reordered_bubbles[:12]
            
            logger.info(f"共創建 {len(bubbles)} 個 bubble")
            
            carousel = FlexCarousel(contents=bubbles)
            
            return FlexMessage(
                alt_text="🎯 太極點命宮資訊",
                contents=carousel
            )
            
        except Exception as e:
            logger.error(f"創建太極點Carousel失敗: {e}", exc_info=True)
            return None
    
    def _create_sihua_carousel(self, result: Dict[str, Any], user_type: str) -> Optional[FlexMessage]:
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
                    bubble = self._create_sihua_bubble(sihua_type, sihua_list, user_type)
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
                                        size="xs",  # 主星字體與輔星一樣大
                                        color="#444444",
                                        weight="bold",
                                        flex=1
                                    ),
                                    FlexText(
                                        text=star_line[1][:10],
                                        size="xs",  # 主星字體與輔星一樣大
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
                                size="xs",  # 主星字體與輔星一樣大
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
                size="micro",  # 改為最小尺寸，縮小bubble寬度
                body=FlexBox(
                    layout="vertical",
                    contents=body_contents,
                    spacing="none",
                    paddingAll="md"  # 減少內邊距以配合小尺寸
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
    
    def _create_sihua_bubble(self, sihua_type: str, sihua_list: List[Dict[str, Any]], user_type: str) -> Optional[FlexBubble]:
        """創建四化 bubble - 根據用戶類型控制顯示內容"""
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
                            size="xxl",
                            flex=0
                        ),
                        FlexText(
                            text=f"{str(sihua_type)}星解析",
                            weight="bold",
                            size="xxl",
                            color=color,
                            flex=1,
                            margin="md"
                        )
                    ],
                    backgroundColor="#F8F9FA",
                    paddingAll="lg"
                )
            )
            
            # 統一顯示「現象」字段 - 所有用戶都能看到
            body_contents.append(
                FlexText(
                    text="🎯 主要現象",
                    size="lg",
                    weight="bold",
                    color="#333333",
                    margin="lg"
                )
            )
            
            # 星曜概要列表 - 顯示現象字段
            for i, sihua_info in enumerate(sihua_list):
                if i >= 3:  # 增加到3個星曜，讓用戶看到更多現象
                    break
                    
                star = str(sihua_info.get("star", ""))
                palace = str(sihua_info.get("palace", ""))
                
                # 從解釋結構中提取現象字段
                phenomenon = self._extract_phenomenon_from_sihua(sihua_info)
                
                # 添加分隔線
                if i > 0:
                    body_contents.append(FlexSeparator(margin="md"))
                
                # 星曜和宮位資訊 - 只有管理員看得到完整星曜名稱
                if user_type == "admin":
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
                                    size="lg",
                                    color="#666666",
                                    weight="bold",
                                    flex=2,
                                    align="end"
                                )
                            ],
                            margin="md"
                        )
                    )
                else:
                    # 付費會員和免費會員：隱藏具體星曜名稱
                    body_contents.append(
                        FlexBox(
                            layout="horizontal",
                            contents=[
                                FlexText(
                                    text=f"⭐ {sihua_type}星 #{i+1}",
                                    weight="bold",
                                    size="lg",
                                    color="#333333",
                                    flex=2
                                ),
                                FlexText(
                                    text=f"📍 {palace}",
                                    size="lg",
                                    color="#666666",
                                    weight="bold",
                                    flex=2,
                                    align="end"
                                )
                            ],
                            margin="md"
                        )
                    )
                
                # 現象描述 - 所有用戶都能看到
                if phenomenon:
                    body_contents.append(
                        FlexText(
                            text=phenomenon,
                            size="md",
                            color="#444444",
                            wrap=True,
                            margin="sm"
                        )
                    )
            
            # 第二層：互動按鈕區域
            action_contents = []
            
            # 根據用戶類型決定按鈕內容
            if user_type in ["admin", "premium"]:
                # 管理員和付費會員：可以查看詳細解釋
                action_contents.append(
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text=f"📖 查看{sihua_type}星詳細解釋",
                                size="md",
                                color="#FFFFFF",
                                weight="bold",
                                align="center",
                                flex=1
                            )
                        ],
                        backgroundColor=color,
                        paddingAll="md",
                        action=MessageAction(
                            text=f"查看{sihua_type}星更多解釋"
                        )
                    )
                )
                
                # 如果有多個四化星，顯示數量
                if len(sihua_list) > 3:
                    action_contents.append(
                        FlexText(
                            text=f"還有 {len(sihua_list) - 3} 顆{sihua_type}星未顯示",
                            size="sm",
                            color="#888888",
                            align="center",
                            margin="sm"
                        )
                    )
                    
            elif user_type == "free":
                # 免費會員：顯示升級提示，但仍能看到基本現象
                action_contents.extend([
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text="🔒 升級會員查看完整解釋",
                                size="md",
                                color="#FFFFFF",
                                weight="bold",
                                align="center",
                                flex=1
                            )
                        ],
                        backgroundColor="#95A5A6",
                        paddingAll="md"
                    ),
                    FlexText(
                        text="💎 付費會員可查看四化詳細解釋、吉凶指引等完整內容",
                        size="sm",
                        color="#999999",
                        wrap=True,
                        align="center",
                        margin="sm"
                    )
                ])
                
                # 如果有多個四化星，顯示數量
                if len(sihua_list) > 3:
                    action_contents.append(
                        FlexText(
                            text=f"還有 {len(sihua_list) - 3} 顆{sihua_type}星，升級後可查看",
                            size="sm",
                            color="#888888",
                            align="center",
                            margin="sm"
                        )
                    )
            
            # 將互動按鈕添加到主內容
            if action_contents:
                body_contents.append(FlexSeparator(margin="lg"))
                body_contents.extend(action_contents)
            
            # 底部說明
            body_contents.append(
                FlexSeparator(margin="lg")
            )
            body_contents.append(
                FlexText(
                    text=self._get_sihua_description(sihua_type),
                    size="sm",
                    color="#999999",
                    wrap=True,
                    align="center",
                    margin="md"
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
            
            return bubble
            
        except Exception as e:
            logger.error(f"創建四化bubble失敗: {e}")
            return None
    
    def _extract_phenomenon_from_sihua(self, sihua_info: Dict[str, Any]) -> str:
        """從四化信息中提取現象字段"""
        try:
            # 方法1：檢查是否直接有「現象」字段（傳統四化格式）
            if "現象" in sihua_info:
                phenomenon = sihua_info.get("現象", "").strip()
                if phenomenon:
                    return phenomenon
            
            # 方法2：從explanation字典中獲取現象字段（太極盤格式）
            explanation = sihua_info.get("explanation", {})
            if isinstance(explanation, dict):
                phenomenon = explanation.get("現象", "").strip()
                if phenomenon:
                    return phenomenon
            
            # 方法3：從解釋文本中解析現象（字符串格式）
            explanation_text = str(explanation) if explanation else ""
            if explanation_text and explanation_text != "{}":
                # 嘗試解析結構化的解釋文本
                lines = explanation_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('現象：'):
                        phenomenon = line.replace('現象：', '').strip()
                        if phenomenon:
                            return phenomenon
                    elif '現象' in line and '：' in line:
                        parts = line.split('：', 1)
                        if len(parts) == 2 and '現象' in parts[0]:
                            phenomenon = parts[1].strip()
                            if phenomenon:
                                return phenomenon
                
                # 如果沒有找到現象字段，使用前半部分作為現象描述
                cleaned_text = self.clean_sihua_explanation(explanation_text)
                sentences = cleaned_text.split('。')
                if sentences and sentences[0].strip():
                    # 取第一句作為現象描述，限制長度
                    phenomenon = sentences[0].strip()
                    if len(phenomenon) > 60:
                        phenomenon = phenomenon[:60] + "..."
                    return phenomenon + "。" if not phenomenon.endswith("。") else phenomenon
            
            # 方法4：如果都沒有，生成基於星曜和四化類型的通用描述
            star = sihua_info.get("star", "此星")
            trans_type = sihua_info.get("type", sihua_info.get("transformation_type", "四化"))
            palace = sihua_info.get("palace", "相關宮位")
            
            if star != "此星" and trans_type != "四化":
                return f"{star}化{trans_type}在{palace}，帶來相應的能量變化。"
            else:
                return "此四化星帶來相關的影響與變化。"
            
        except Exception as e:
            logger.error(f"提取現象字段失敗: {e}")
            return "此四化星帶來相關的影響與變化。"
    
    def _extract_key_info(self, explanation: str, sihua_type: str) -> str:
        """提取四化的關鍵信息"""
        try:
            if not explanation:
                return ""
            
            # 清理標點符號
            explanation = self.clean_sihua_explanation(explanation)
            
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
            cleaned = self.clean_sihua_explanation(explanation[:50])
            return cleaned + "..." if len(cleaned) > 50 else cleaned
    
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
        result: Dict[str, Any],
        sihua_type: str,
        user_type: str = "free"  # 新增用戶類型參數
    ) -> Optional[Union[FlexMessage, List[TextMessage]]]:
        """
        生成四化詳細解釋消息 - 優化排版版本，支援超長內容分割
        
        Args:
            result: 占卜結果數據
            sihua_type: 四化類型 (祿/權/科/忌)
            user_type: 用戶類型 - "admin"(管理員), "premium"(付費會員), "free"(免費會員)
            
        Returns:
            包含完整解釋的 FlexMessage 或 TextMessage列表（當內容過長時）
        """
        try:
            # 從占卜結果中提取四化數據
            sihua_results = result.get("sihua_results", [])
            sihua_list = []
            
            for sihua_info in sihua_results:
                if sihua_info.get("type") == sihua_type:
                    sihua_list.append(sihua_info)
            
            if not sihua_list:
                return None
                
            color = self.SIHUA_COLORS.get(sihua_type, "#95A5A6")
            emoji = self.SIHUA_EMOJIS.get(sihua_type, "⭐")
            
            # 估算總內容長度，包含 JSON 結構開銷
            total_content_length = self._estimate_flex_message_size(sihua_list, sihua_type)
            
            # LINE Flex Message 建議限制約 10KB-20KB
            # 為安全起見，我們設定在 5000 字符以內使用 Flex Message
            if total_content_length > 5000:
                logger.info(f"內容過長 ({total_content_length} 字符)，使用文字訊息代替 Flex Message")
                return self._create_text_messages_for_long_content(sihua_list, sihua_type, user_type, emoji)
            else:
                logger.info(f"內容長度適中 ({total_content_length} 字符)，使用 Flex Message")
                return self._create_single_bubble_detail_message(sihua_list, sihua_type, user_type, color, emoji)
                
        except Exception as e:
            logger.error(f"生成四化詳細解釋失敗: {e}")
            return None
    
    def _estimate_flex_message_size(self, sihua_list: List[Dict], sihua_type: str) -> int:
        """估算 Flex Message 的大小（字符數）"""
        try:
            # 基礎結構開銷（JSON 格式、標籤等）
            base_overhead = 2000
            
            # 每個星曜的內容
            content_size = 0
            for sihua_info in sihua_list:
                star_name = str(sihua_info.get("star", ""))
                palace = str(sihua_info.get("palace", ""))
                explanation = str(sihua_info.get("explanation", ""))
                
                # 星曜名稱和宮位
                content_size += len(star_name) + len(palace) + 50  # 50 是格式開銷
                
                # 解釋內容
                content_size += len(explanation)
                
                # Flex 結構開銷（每個內容區塊）
                content_size += 500
            
            # 四化說明
            desc = self._get_detailed_sihua_description(sihua_type)
            content_size += len(desc)
            
            return base_overhead + content_size
            
        except Exception as e:
            logger.error(f"估算大小失敗: {e}")
            return 10000  # 保守估算，使用文字訊息
    
    def _create_text_messages_for_long_content(self, sihua_list: List[Dict], sihua_type: str, 
                                             user_type: str, emoji: str) -> List[TextMessage]:
        """為超長內容創建多個文字訊息"""
        try:
            from linebot.v3.messaging import TextMessage
            
            messages = []
            
            # 第一條訊息：標題和總體說明
            title_content = f"{emoji} {sihua_type}星完整解釋\n"
            title_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪\n\n"
            
            # 四化總體說明
            detailed_desc = self._get_detailed_sihua_description(sihua_type)
            title_content += f"📖 四化概述\n{detailed_desc}\n\n"
            title_content += f"✨ 您的命盤中共有 {len(sihua_list)} 顆{sihua_type}星\n"
            title_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪"
            
            messages.append(TextMessage(text=title_content))
            
            # 為每顆星創建獨立訊息（每條訊息最多1400字，留出安全邊界）
            for i, sihua_info in enumerate(sihua_list):
                star_name = sihua_info.get("star", "未知星曜")
                palace = sihua_info.get("palace", "")
                explanation = sihua_info.get("explanation", "")
                
                # 星曜內容標題
                star_content = f"⭐ {star_name} 在 {palace}\n"
                star_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪\n\n"
                
                if explanation:
                    # 將解釋按段落分組，並添加分類標籤
                    explanation_parts = self._split_text_with_limit(explanation, 180)  # 每段180字
                    
                    current_category = ""  # 記錄當前分類，避免重複標籤
                    
                    for j, part in enumerate(explanation_parts):
                        if not part.strip():
                            continue
                            
                        # 獲取內容標籤
                        label, _ = self._get_content_label(part)
                        
                        # 提取 emoji 和分類名稱
                        if ' ' in label:
                            emoji_part = label.split(' ')[0]
                            category_name = label.split(' ', 1)[1]
                        else:
                            emoji_part = "📝"
                            category_name = "詳細說明"
                        
                        # 只在分類改變時顯示新標籤
                        if category_name != current_category:
                            if current_category:  # 不是第一個分類，加個空行
                                star_content += "\n"
                            star_content += f"{emoji_part} {category_name}\n"
                            star_content += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
                            current_category = category_name
                        
                        star_content += f"{part.strip()}\n\n"
                        
                        # 檢查當前訊息長度，避免超過 LINE 文字訊息限制
                        if len(star_content) > 1400:
                            # 保存當前訊息
                            star_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪"
                            messages.append(TextMessage(text=star_content))
                            
                            # 開始新的訊息（如果還有剩餘內容）
                            if j < len(explanation_parts) - 1:
                                star_content = f"⭐ {star_name} 在 {palace} (續)\n"
                                star_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪\n\n"
                                current_category = ""  # 重置分類記錄
                            else:
                                star_content = ""
                                break
                
                # 如果還有內容未發送，發送最後一條
                if star_content and not star_content.endswith("▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪"):
                    star_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪"
                    messages.append(TextMessage(text=star_content))
            
            # 最後一條訊息：總結（如果訊息數量多）
            if len(messages) > 3:  # 超過3條訊息時添加總結
                summary_content = f"📋 {sihua_type}星解釋完畢\n"
                summary_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪\n\n"
                summary_content += f"✅ 已完整顯示 {len(sihua_list)} 顆{sihua_type}星解釋\n"
                summary_content += f"📨 共發送 {len(messages)} 條詳細訊息\n\n"
                summary_content += "💡 內容按類型分段，便於閱讀\n"
                summary_content += "🔮 如需其他四化星解釋，請重新查看\n"
                summary_content += "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪"
                
                messages.append(TextMessage(text=summary_content))
            
            return messages
            
        except Exception as e:
            logger.error(f"創建文字訊息失敗: {e}")
            # 後備方案：簡單的文字訊息
            fallback_text = f"{emoji} {sihua_type}星詳細解釋\n\n"
            fallback_text += f"您的命盤中有 {len(sihua_list)} 顆{sihua_type}星，"
            fallback_text += "內容較多，建議透過其他方式查看完整解釋。\n\n"
            fallback_text += "如有疑問，請重新進行占卜。"
            
            return [TextMessage(text=fallback_text)]
    
    def _create_single_bubble_detail_message(self, sihua_list: List[Dict], sihua_type: str, 
                                           user_type: str, color: str, emoji: str) -> FlexMessage:
        """創建單個bubble的詳細解釋"""
        body_contents = []
        
        # 詳細解釋標題 - 優化設計
        body_contents.append(
            FlexBox(
                layout="horizontal",
                contents=[
                    FlexText(
                        text=str(emoji),
                        size="xxl",
                        flex=0,
                        color=color
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
                paddingAll="lg",
                cornerRadius="8px"
            )
        )
        
        # 四化總體說明 - 優化字數
        detailed_desc = self._get_detailed_sihua_description(sihua_type)
        if len(detailed_desc) > 120:  # 進一步減少總體說明字數
            detailed_desc = detailed_desc[:120] + "..."
        
        body_contents.append(
            FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="📖 四化概述",
                        size="md",
                        weight="bold",
                        color="#34495E",
                        margin="lg"
                    ),
                    FlexText(
                        text=detailed_desc,
                        size="sm",
                        color="#5D6D7E",
                        wrap=True,
                        margin="sm"
                    )
                ],
                backgroundColor="#FAFBFC",
                paddingAll="md",
                cornerRadius="6px",
                margin="md"
            )
        )
        
        # 顯示具體星曜 - 限制數量並優化排版
        max_stars = 3  # 減少顯示數量，避免過長
        
        for i, sihua_info in enumerate(sihua_list[:max_stars]):
            star_name = sihua_info.get("star", "未知星曜")
            palace = sihua_info.get("palace", "")
            explanation = sihua_info.get("explanation", "")
            
            # 星曜標題區域
            star_header = FlexBox(
                layout="horizontal",
                contents=[
                    FlexText(
                        text="⭐",
                        size="lg",
                        color=color,
                        flex=0
                    ),
                    FlexText(
                        text=f"{star_name} 在 {palace}",
                        weight="bold",
                        size="md",
                        color="#2C3E50",
                        flex=1,
                        margin="sm"
                    )
                ],
                backgroundColor=color,
                paddingAll="sm",
                cornerRadius="6px",
                margin="lg"
            )
            
            # 修改文字顏色為白色以在有色背景上顯示
            star_header.contents[1].color = "#FFFFFF"
            
            body_contents.append(star_header)
            
            # 完整解釋內容 - 優化分段和排版
            if explanation:
                # 處理字典格式的explanation
                if isinstance(explanation, dict):
                    # 將字典內容格式化為文字
                    explanation_text = ""
                    for key, value in explanation.items():
                        if value:  # 確保值不為空
                            explanation_text += f"{key}：{value}\n\n"
                    explanation = explanation_text.strip()
                
                # 確保explanation是字串
                if not isinstance(explanation, str):
                    explanation = str(explanation)
                
                # 將解釋分段顯示，減少每段字數
                explanation_parts = self._split_text_with_limit(explanation, 80)  # 減少到80字每段
                
                for j, part in enumerate(explanation_parts):
                    if j >= 6:  # 增加段落限制，但減少每段字數
                        break
                        
                    if part.strip():
                        # 區分不同類型的內容
                        label, label_color = self._get_content_label(part)
                        
                        # 為每段內容創建獨立的區塊
                        content_block = FlexBox(
                            layout="vertical",
                            contents=[
                                FlexText(
                                    text=label,
                                    size="xs",
                                    color=label_color,
                                    weight="bold",
                                    margin="none"
                                ),
                                FlexText(
                                    text=part.strip(),
                                    size="sm",
                                    color="#444444",
                                    wrap=True,
                                    margin="xs",
                                    lineSpacing="sm"
                                )
                            ],
                            backgroundColor="#FFFFFF",
                            paddingAll="sm",
                            cornerRadius="4px",
                            margin="sm",
                            borderWidth="1px",
                            borderColor="#E8E8E8"
                        )
                        
                        body_contents.append(content_block)
        
        # 如果有更多星曜未顯示，添加提示
        if len(sihua_list) > max_stars:
            body_contents.append(
                FlexBox(
                    layout="vertical",
                    contents=[
                        FlexSeparator(margin="lg", color="#E8E8E8"),
                        FlexText(
                            text=f"📚 另有 {len(sihua_list) - max_stars} 顆{sihua_type}星",
                            size="sm",
                            color="#7B8794",
                            align="center",
                            margin="md"
                        ),
                        FlexText(
                            text="完整內容已精簡顯示，如需更多詳情請重新占卜",
                            size="xs",
                            color="#95A5A6",
                            align="center",
                            margin="xs"
                        )
                    ]
                )
            )
        
        # 底部總結 - 優化設計
        body_contents.append(
            FlexBox(
                layout="vertical",
                contents=[
                    FlexSeparator(margin="xl", color="#BDC3C7"),
                    FlexBox(
                        layout="horizontal",
                        contents=[
                            FlexText(
                                text="📖",
                                size="sm",
                                color=color,
                                flex=0
                            ),
                            FlexText(
                                text="以上為完整的四化解釋內容",
                                size="sm",
                                color="#7B8794",
                                flex=1,
                                margin="sm"
                            )
                        ],
                        margin="md"
                    )
                ]
            )
        )
        
        bubble = FlexBubble(
            size="giga",  # 使用大尺寸
            body=FlexBox(
                layout="vertical",
                contents=body_contents,
                spacing="none",
                paddingAll="lg"
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
    
    def _create_multi_bubble_detail_message(self, sihua_list: List[Dict], sihua_type: str,
                                          user_type: str, color: str, emoji: str) -> FlexMessage:
        """創建多個bubble的詳細解釋（內容過長時使用）"""
        # 這個功能可以後續實現，目前先使用單bubble版本
        return self._create_single_bubble_detail_message(sihua_list, sihua_type, user_type, color, emoji)
    
    def _split_text_with_limit(self, text: str, max_length: int) -> List[str]:
        """
        將文字按指定長度分割，確保不超過字數限制 - 優化版本
        
        Args:
            text: 要分割的文字
            max_length: 每段的最大字數
            
        Returns:
            分割後的文字列表
        """
        if not text or len(text) <= max_length:
            return [text] if text else []
        
        # 優先按標點符號分割（句號、問號、驚嘆號）
        major_punctuation = ['。', '？', '！', '；']
        minor_punctuation = ['，', '、']
        
        # 先按主要標點分割
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in major_punctuation:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # 如果還有剩餘文字
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # 組合句子為段落，確保不超過字數限制
        result = []
        current_part = ""
        
        for sentence in sentences:
            if not sentence:
                continue
                
            # 檢查是否可以加入當前段落
            test_part = current_part + sentence if current_part else sentence
            
            if len(test_part) <= max_length:
                current_part = test_part
            else:
                # 如果當前段落不為空，先保存
                if current_part:
                    result.append(current_part)
                    current_part = ""
                
                # 如果單句就超過限制，需要進一步分割
                if len(sentence) > max_length:
                    # 嘗試按次要標點分割
                    sub_parts = []
                    current_sub = ""
                    
                    for char in sentence:
                        current_sub += char
                        if char in minor_punctuation and len(current_sub) >= max_length * 0.7:
                            sub_parts.append(current_sub.strip())
                            current_sub = ""
                    
                    if current_sub.strip():
                        sub_parts.append(current_sub.strip())
                    
                    # 如果還是太長，強制按字符分割
                    for sub_part in sub_parts:
                        if len(sub_part) <= max_length:
                            result.append(sub_part)
                        else:
                            # 強制分割
                            for i in range(0, len(sub_part), max_length):
                                part = sub_part[i:i + max_length]
                                if part:
                                    result.append(part)
                else:
                    current_part = sentence
        
        # 添加最後一段
        if current_part:
            result.append(current_part)
        
        return result
    
    def _get_content_label(self, text: str) -> Tuple[str, str]:
        """
        根據文字內容返回適當的標籤和顏色 - 增強版本
        
        Args:
            text: 文字內容
            
        Returns:
            (標籤, 顏色) 的元組
        """
        # 心理特質相關
        if any(keyword in text for keyword in ["心理", "個性", "性格", "內心", "情緒", "脾氣", "態度"]):
            return "🧠 心理特質", "#9B59B6"
        
        # 外在表現相關
        elif any(keyword in text for keyword in ["現象", "表現", "行為", "舉止", "外表", "形象"]):
            return "🎭 外在表現", "#3498DB"
        
        # 事業財運相關
        elif any(keyword in text for keyword in ["事業", "工作", "財運", "賺錢", "收入", "投資", "生意"]):
            return "💼 事業財運", "#2E86C1"
        
        # 感情婚姻相關
        elif any(keyword in text for keyword in ["感情", "婚姻", "愛情", "配偶", "戀愛", "夫妻", "伴侶"]):
            return "💕 感情婚姻", "#E91E63"
        
        # 健康養生相關
        elif any(keyword in text for keyword in ["健康", "身體", "疾病", "養生", "醫療", "病痛"]):
            return "🏥 健康養生", "#4CAF50"
        
        # 人際關係相關
        elif any(keyword in text for keyword in ["人際", "朋友", "社交", "貴人", "小人", "關係", "交友"]):
            return "👥 人際關係", "#FF9800"
        
        # 學習考試相關
        elif any(keyword in text for keyword in ["學習", "考試", "讀書", "教育", "知識", "文昌", "智慧"]):
            return "📚 學習考試", "#607D8B"
        
        # 可能事件
        elif any(keyword in text for keyword in ["事件", "發生", "情況", "遭遇", "經歷", "機會"]):
            return "📅 可能事件", "#FF5722"
        
        # 建議提示
        elif any(keyword in text for keyword in ["提示", "建議", "注意", "應該", "需要", "適合", "避免"]):
            return "💡 行運建議", "#8BC34A"
        
        # 吉凶判斷
        elif any(keyword in text for keyword in ["吉", "凶", "好運", "壞運", "順利", "阻礙", "困難"]):
            return "⚖️ 吉凶分析", "#795548"
        
        # 默認分類
        else:
            return "📝 詳細說明", "#7F8C8D"
    
    def _get_detailed_sihua_description(self, sihua_type: str) -> str:
        """獲取四化類型的詳細說明 - 優化字數限制"""
        descriptions = {
            "祿": "祿星代表財富、好運與機會。化祿的星曜通常能帶來順利發展，有賺錢機會，容易得到貴人幫助，也代表人際關係和諧。",
            "權": "權星代表權力、領導力與掌控能力。化權的星曜會增強主導性，有助於事業發展和地位提升，但需注意不要過於專斷。",
            "科": "科星代表名聲、聲望與學習能力。化科的星曜能提升個人名氣和社會地位，有利於學習考試，也象徵貴人相助。",
            "忌": "忌星代表阻礙、困難與挑戰。化忌會帶來考驗，但也能促使成長學習。關鍵在於如何化解和轉化困難。"
        }
        return descriptions.get(sihua_type, "四化星對運勢產生重要影響，需要仔細分析。") 

    def _create_basic_result_bubble(self, result: Dict[str, Any], user_type: str = "free") -> FlexBubble:
        """創建基本占卜結果泡泡"""
        
        # 根據用戶類型選擇背景圖片
        if user_type == "admin":
            background_image = self.background_images.get("admin", self.fallback_images["admin"])
        elif user_type == "premium":
            background_image = self.background_images.get("premium", self.fallback_images["premium"])
        else:
            background_image = self.background_images.get("basic", self.fallback_images["basic"])
        
        # 基本資訊
        gender_text = "男性" if result.get("gender") == "M" else "女性"
        divination_time = result.get("divination_time", "")
        taichi_palace = result.get("taichi_palace", "")
        minute_dizhi = result.get("minute_dizhi", "")
        palace_tiangan = result.get("palace_tiangan", "")
        
        # 解析時間
        from datetime import datetime, timezone, timedelta
        if divination_time:
            try:
                # 解析 ISO 格式時間
                if '+' in divination_time or 'Z' in divination_time:
                    dt = datetime.fromisoformat(divination_time.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(divination_time)
                
                # 確保轉換為台北時間
                taipei_tz = timezone(timedelta(hours=8))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=taipei_tz)
                else:
                    dt = dt.astimezone(taipei_tz)
                
                # 顯示完整日期時間格式
                time_str = dt.strftime("%m/%d %H:%M (台北)")
            except Exception as e:
                logger.warning(f"時間解析失敗: {divination_time}, 錯誤: {e}")
                time_str = "現在"
        else:
            time_str = "現在"
        
        # 根據用戶類型設置標識
        if user_type == "admin":
            badge = "👑 管理員"
            badge_color = "#FFD700"
        elif user_type == "premium":
            badge = "💎 付費會員"
            badge_color = "#9B59B6"
        else:
            badge = ""
            badge_color = "#666666"
        
        # 創建標題區域內容
        header_contents = [
            FlexText(
                text="🔮 占卜結果 ✨",
                weight="bold",
                size="xl",
                color=self.colors["star_gold"],
                align="center"
            )
        ]
        
        # 如果有會員標識，添加到標題
        if badge:
            header_contents.append(
                FlexText(
                    text=badge,
                    size="xs",
                    color=badge_color,
                    align="center",
                    margin="xs"
                )
            )
        
        bubble = FlexBubble(
            size="mega",
            hero=FlexBox(
                layout="vertical",
                contents=header_contents,
                background_image=background_image,
                background_size="cover",
                background_position="center",
                padding_all="20px",
                height="100px"
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # 基本資訊
                    FlexBox(
                        layout="vertical",
                        contents=[
                            FlexText(
                                text="📊 基本資訊",
                                weight="bold",
                                size="md",
                                color=self.colors["star_gold"],
                                margin="none"
                            ),
                            self._create_info_row("📅", "時間", time_str),
                            self._create_info_row("👤", "性別", gender_text),
                            self._create_info_row("☯️", "太極點", taichi_palace),
                            self._create_info_row("🌌", "宮干", palace_tiangan)
                        ],
                        spacing="sm",
                        padding_all="12px"
                    )
                ],
                spacing="md",
                padding_all="16px"
            )
        )
        
        return bubble

    def _create_info_row(self, emoji: str, label: str, value: str) -> FlexBox:
        """創建基本資訊行"""
        return FlexBox(
            layout="horizontal",
            contents=[
                FlexText(text=emoji, size="sm", color="#666666", flex=0),
                FlexText(text=f"{label}:", size="sm", color="#666666", flex=1),
                FlexText(text=value, size="sm", weight="bold", flex=2, align="end")
            ],
            margin="sm"
        )

    def generate_taichi_palace_message(self, result: Dict[str, Any]) -> Optional[FlexMessage]:
        """
        生成太極十二宮 Flex Message
        
        Args:
            result: 占卜結果數據，必須包含 taichi_palace_mapping 和 basic_chart
            
        Returns:
            FlexMessage: 太極十二宮 Carousel 或 None
        """
        try:
            logger.info("開始生成太極十二宮 Flex Message")
            
            taichi_message = self._create_taichi_palace_carousel(result)
            
            if taichi_message:
                logger.info("✅ 太極十二宮 Flex Message 生成成功")
                return taichi_message
            else:
                logger.warning("❌ 太極十二宮 Flex Message 生成失敗")
                return None
                
        except Exception as e:
            logger.error(f"生成太極十二宮 Flex Message 時發生錯誤: {e}")
            return None 