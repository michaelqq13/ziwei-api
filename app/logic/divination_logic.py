"""
占卜邏輯系統
實現基於當下時間和性別的太極點占卜算法
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.logic.purple_star_chart import PurpleStarChart
from app.config.linebot_config import LineBotConfig
from app.utils.chinese_calendar import ChineseCalendar

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DivinationLogic:
    """占卜邏輯核心類"""
    
    def __init__(self):
        # 不在初始化時創建 chart_calculator，而是在需要時創建
        pass
    
    def get_chart_calculator(self, db: Optional[Session] = None) -> Optional[PurpleStarChart]:
        """
        獲取命盤計算器，如果沒有數據庫會話則返回 None
        """
        try:
            if db:
                return PurpleStarChart(db)
            return None
        except Exception:
            return None
    
    def get_minute_dizhi(self, current_time: datetime) -> str:
        """
        根據當前時間計算分鐘地支
        每10分鐘為一個單位，一個時辰120分鐘分成12個地支
        """
        try:
            # 獲取當前小時和分鐘
            hour = current_time.hour
            minute = current_time.minute
            
            logger.info(f"計算分鐘地支 - 時間：{hour}:{minute:02d}")
            
            # 使用 ChineseCalendar 類計算分鐘地支
            minute_dizhi = ChineseCalendar.get_minute_branch(hour, minute)
            
            logger.info(f"計算結果：{minute_dizhi}")
            
            return minute_dizhi
            
        except Exception as e:
            logger.error(f"計算分鐘地支錯誤：{e}")
            raise
    
    def calculate_taichi_palace(self, gender: str, current_time: datetime, db: Optional[Session] = None) -> Tuple[str, Dict]:
        """
        計算太極點命宮
        根據性別和當前時間排出命盤，然後根據分鐘地支變換命宮
        """
        try:
            logger.info(f"開始計算太極點命宮 - 時間：{current_time}, 性別：{gender}")
            
            # 獲取分鐘地支
            minute_dizhi = self.get_minute_dizhi(current_time)
            logger.info(f"分鐘地支：{minute_dizhi}")
            
            # 根據測試案例，太極點命宮應該是分鐘地支加"宮"
            # 例如：分鐘地支"亥" -> "亥宮"
            taichi_palace_name = f"{minute_dizhi}宮"
            
            logger.info(f"太極點命宮：{taichi_palace_name}")
            
            # 創建命盤計算器來獲取正確的宮干
            chart = PurpleStarChart(
                year=current_time.year,
                month=current_time.month,
                day=current_time.day,
                hour=current_time.hour,
                minute=current_time.minute,
                gender=gender,
                db=db
            )
            
            # 獲取完整命盤
            chart_data = chart.get_chart()
            
            # 根據分鐘地支找到對應的宮干
            palace_tiangan = self.get_palace_tiangan_by_branch(chart_data, minute_dizhi)
            logger.info(f"根據地支 {minute_dizhi} 找到宮干：{palace_tiangan}")
            
            return taichi_palace_name, {
                "minute_dizhi": minute_dizhi,
                "palace_tiangan": palace_tiangan
            }
            
        except Exception as e:
            logger.error(f"計算太極點命宮錯誤：{e}")
            raise
    
    def get_palace_tiangan_by_branch(self, chart_data: Dict, target_branch: str) -> str:
        """
        根據地支找到對應的宮干
        
        Args:
            chart_data: 命盤資料
            target_branch: 目標地支
            
        Returns:
            str: 對應的天干
        """
        if not chart_data or not target_branch:
            return "甲"  # 預設值
        
        try:
            # 從命盤資料中找到對應地支的天干
            palaces = chart_data.get("palaces", {})
            
            logger.info(f"開始搜尋地支 {target_branch} 對應的宮干")
            logger.info(f"命盤宮位數量：{len(palaces)}")
            
            for palace_name, palace_info in palaces.items():
                # 檢查對象屬性格式
                if hasattr(palace_info, 'branch') and palace_info.branch == target_branch:
                    logger.info(f"找到地支 {target_branch} 對應的宮位：{palace_name}，天干：{palace_info.stem}")
                    return palace_info.stem
                # 檢查字典格式 - 使用 dizhi 欄位
                elif isinstance(palace_info, dict):
                    palace_dizhi = palace_info.get("dizhi", palace_info.get("branch", ""))
                    if palace_dizhi == target_branch:
                        tiangan = palace_info.get("tiangan", palace_info.get("stem", ""))
                        logger.info(f"找到地支 {target_branch} 對應的宮位：{palace_name}，天干：{tiangan}")
                        return tiangan
                    else:
                        logger.debug(f"宮位 {palace_name} 地支：{palace_dizhi}，不匹配目標地支：{target_branch}")
            
            # 如果沒找到，使用簡化邏輯
            logger.warning(f"未找到地支 {target_branch} 對應的宮位，使用預設值")
            return "甲"
            
        except Exception as e:
            logger.error(f"根據地支獲取宮干錯誤：{e}")
            return "甲"
    
    def get_palace_tiangan(self, chart_data: Dict, palace_index: int) -> str:
        """
        獲取指定宮位的天干（宮干）
        """
        if not chart_data:
            # 如果沒有命盤資料，使用簡化邏輯
            # 根據時間推算天干
            tiangan_order = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            return tiangan_order[palace_index % 10]
        
        try:
            # 從命盤資料中獲取宮位天干
            palaces = chart_data.get("palaces", [])
            if palace_index < len(palaces):
                palace_info = palaces[palace_index]
                tiangan = palace_info.get("tiangan", "")
                logger.info(f"宮干計算 - 宮位索引：{palace_index}")
                logger.info(f"宮位資訊：{palace_info}")
                logger.info(f"計算結果：{tiangan}")
                return tiangan
            return "甲"  # 預設值
        except Exception as e:
            logger.error(f"宮干計算錯誤：{e}")
            return "甲"  # 預設值
    
    def calculate_sihua(self, tiangan: str) -> Dict[str, str]:
        """
        根據天干計算四化星
        """
        # 四化表（簡化版本）
        sihua_table = {
            "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽"},
            "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰"},
            "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞"},
            "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門"},
            "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機"},
            "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲"},
            "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同"},
            "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌"},
            "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲"},
            "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼"}
        }
        
        return sihua_table.get(tiangan, sihua_table["甲"])
    
    def get_star_palace_mapping(self, chart_data: Dict) -> Dict[str, str]:
        """
        獲取星曜與宮位的對應關係
        """
        if not chart_data:
            # 簡化的星曜宮位對應
            return {
                "紫微": "命宮", "天機": "兄弟宮", "太陽": "夫妻宮", "武曲": "子女宮",
                "天同": "財帛宮", "廉貞": "疾厄宮", "天府": "遷移宮", "太陰": "奴僕宮",
                "貪狼": "官祿宮", "巨門": "田宅宮", "天相": "福德宮", "天梁": "父母宮",
                "七殺": "命宮", "破軍": "財帛宮", "文昌": "夫妻宮", "文曲": "疾厄宮",
                "左輔": "兄弟宮", "右弼": "子女宮"
            }
        
        try:
            # 從命盤資料中解析星曜位置
            star_palace_map = {}
            palaces = chart_data.get("palaces", [])
            palace_names = [
                "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
                "遷移宮", "奴僕宮", "官祿宮", "田宅宮", "福德宮", "父母宮"
            ]
            
            for i, palace_info in enumerate(palaces):
                palace_name = palace_names[i] if i < len(palace_names) else f"宮位{i+1}"
                stars = palace_info.get("stars", [])
                for star in stars:
                    star_name = star.get("name", "") if isinstance(star, dict) else str(star)
                    if star_name:
                        star_palace_map[star_name] = palace_name
            
            return star_palace_map
        except:
            # 發生錯誤時返回簡化對應
            return self.get_star_palace_mapping(None)
    
    def get_sihua_explanations(self, sihua_results: List[Dict]) -> List[Dict]:
        """
        獲取四化星的解釋
        """
        explanations = {
            "忌": {
                "命宮": "近期運勢略有波折，需謹慎行事，避免衝動決定。",
                "財帛宮": "財運略有阻礙，投資需謹慎，避免不必要的開支。",
                "事業宮": "工作上可能遇到挑戰，需要耐心處理人際關係。",
                "感情宮": "感情上容易有誤會，需要多溝通理解。",
                "default": "此方面需要特別注意，避免過度執著。"
            },
            "祿": {
                "命宮": "近期運勢亨通，是展現才能的好時機。",
                "財帛宮": "財運旺盛，適合投資理財，會有不錯的收穫。",
                "事業宮": "事業運佳，容易得到貴人相助，適合拓展業務。",
                "感情宮": "感情運勢良好，單身者有機會遇到心儀對象。",
                "default": "此方面運勢良好，把握機會必有收穫。"
            },
            "權": {
                "命宮": "領導能力增強，適合主導重要事務。",
                "財帛宮": "有機會增加收入來源，理財能力提升。",
                "事業宮": "在職場上有表現機會，容易獲得權威認可。",
                "感情宮": "在感情中較為主導，但要避免過於強勢。",
                "default": "此方面有主導權，可積極爭取機會。"
            },
            "科": {
                "命宮": "學習運佳，適合進修提升自己。",
                "財帛宮": "透過知識技能可以增加收入。",
                "事業宮": "專業能力受到肯定，有升遷或加薪機會。",
                "感情宮": "透過文化活動容易結識有緣人。",
                "default": "此方面適合學習成長，文書事務順利。"
            }
        }
        
        results = []
        for sihua_info in sihua_results:
            sihua_type = sihua_info["type"]
            palace = sihua_info["palace"]
            star = sihua_info["star"]
            
            # 獲取解釋
            type_explanations = explanations.get(sihua_type, {})
            explanation = type_explanations.get(palace, type_explanations.get("default", "運勢平穩。"))
            
            results.append({
                "type": sihua_type,
                "star": star,
                "palace": palace,
                "explanation": explanation
            })
        
        return results
    
    def perform_divination(self, gender: str, current_time: datetime = None, db: Optional[Session] = None) -> Dict:
        """
        執行占卜
        根據當前時間和性別計算太極點命宮和四化
        """
        if not current_time:
            current_time = datetime.now()
        
        try:
            logger.info(f"開始執行占卜 - 時間：{current_time}, 性別：{gender}")
            
            # 創建命盤計算器
            chart = PurpleStarChart(
                year=current_time.year,
                month=current_time.month,
                day=current_time.day,
                hour=current_time.hour,
                minute=current_time.minute,
                gender=gender,
                db=db
            )
            
            # 獲取分鐘地支
            minute_dizhi = self.get_minute_dizhi(current_time)
            logger.info(f"計算分鐘地支：{minute_dizhi}")
            
            # 計算太極點命宮
            taichi_palace, chart_info = self.calculate_taichi_palace(gender, current_time, db)
            logger.info(f"計算太極點命宮：{taichi_palace}")
            
            # 獲取太極點命宮的宮干
            palace_tiangan = chart_info.get("palace_tiangan", "")
            logger.info(f"獲取宮干：{palace_tiangan}")
            
            # 使用宮干計算四化（而不是年干）
            logger.info(f"使用宮干 {palace_tiangan} 計算四化")
            sihua_stars = chart.apply_custom_stem_transformations(palace_tiangan)
            logger.info(f"計算四化：{sihua_stars}")
            
            # 在應用宮干四化之後重新獲取完整命盤
            chart_data = chart.get_chart()
            logger.info(f"重新獲取命盤數據（應用宮干四化後）")
            
            # 格式化四化結果
            sihua_results = []
            for star_name, info in sihua_stars.items():
                # 整合完整的解釋資料，優化排版
                explanation_parts = []
                
                # 添加現象 🔮
                if info.get("現象"):
                    explanation_parts.append(f"🔮 **現象**\n   {info['現象']}")
                
                # 添加心理傾向 💭
                if info.get("心理傾向"):
                    explanation_parts.append(f"💭 **心理傾向**\n   {info['心理傾向']}")
                
                # 添加可能事件 🎯
                if info.get("可能事件"):
                    explanation_parts.append(f"🎯 **可能事件**\n   {info['可能事件']}")
                
                # 添加提示 💡
                if info.get("提示"):
                    explanation_parts.append(f"💡 **提示**\n   {info['提示']}")
                
                # 添加建議 🌟
                if info.get("來意不明建議"):
                    explanation_parts.append(f"🌟 **建議**\n   {info['來意不明建議']}")
                
                # 合併所有解釋，內部用雙換行分隔
                full_explanation = "\n\n".join(explanation_parts) if explanation_parts else ""
                
                sihua_results.append({
                    "type": info["四化"],
                    "star": star_name,
                    "palace": info["宮位"],
                    "explanation": full_explanation
                })
            
            return {
                "success": True,
                "gender": gender,
                "divination_time": current_time.isoformat(),
                "taichi_palace": taichi_palace,
                "minute_dizhi": minute_dizhi,
                "palace_tiangan": palace_tiangan,
                "sihua_results": sihua_results,
                "basic_chart": chart_data.get("palaces", {})
            }
            
        except Exception as e:
            logger.error(f"占卜計算錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_sihua_explanation(self, sihua_type: str, star: str, palace: str) -> str:
        """
        獲取四化解釋
        """
        # 四化解釋表（這裡應該從您的資料中讀取）
        explanations = {
            "祿": {
                "廉貞": "在事業上有突破性發展，但要注意壓力調節。",
                "天機": "智慧敏銳，善於規劃，易有意外收穫。",
                "天同": "人際關係良好，貴人相助，財運亨通。",
                "太陰": "適合從事藝術創作，易得女性貴人幫助。",
                "貪狼": "事業發展順利，但要注意財務管理。",
                "武曲": "財運亨通，善於理財，易有投資機會。",
                "太陽": "領導能力強，易得上司賞識。",
                "巨門": "口才出眾，善於談判，易得利益。",
                "天梁": "正直守信，得人信任，易有意外之財。",
                "破軍": "行動力強，創業有利，但要注意風險。"
            },
            "權": {
                "破軍": "決策果斷，行動力強，易有突破。",
                "天梁": "正直威嚴，易得人尊重。",
                "天機": "思維敏捷，善於謀劃。",
                "天同": "人緣極佳，易得支持。",
                "太陰": "直覺敏銳，易有好機會。",
                "貪狼": "魄力十足，易有成就。",
                "武曲": "管理能力強，善於統籌。",
                "太陽": "威望高，易得重用。",
                "紫微": "領導才能出眾，有大作為。",
                "巨門": "口才出眾，善於協調。"
            },
            "科": {
                "武曲": "理財有道，易得正財。",
                "紫微": "學習能力強，易有成就。",
                "文昌": "學術表現優異，利於考試。",
                "天機": "創新能力強，易有發明。",
                "右弼": "人際關係好，貴人相助。",
                "天梁": "正直守信，得人信賴。",
                "太陰": "藝術天賦高，易有成就。",
                "文曲": "才藝出眾，易得賞識。",
                "左輔": "助力很大，易有機遇。",
                "太陰": "感知敏銳，易有靈感。"
            },
            "忌": {
                "太陽": "易有小人阻礙，需謹慎行事。",
                "太陰": "情緒易波動，需注意調節。",
                "廉貞": "易有阻礙，需堅持不懈。",
                "巨門": "易遭誤解，需注意溝通。",
                "天機": "易有變故，需謹慎決策。",
                "文曲": "易有小人暗算，需提防。",
                "天同": "易有感情困擾，需理性對待。",
                "文昌": "易有學業壓力，需努力。",
                "武曲": "易有財務糾紛，需謹慎。",
                "貪狼": "易有衝突，需避免過激。"
            }
        }
        
        # 獲取對應的解釋
        type_explanations = explanations.get(sihua_type, {})
        explanation = type_explanations.get(star, f"{star}落在{palace}，具體影響需要綜合判斷。")
        
        return explanation

# 全局實例
divination_logic = DivinationLogic()

def get_divination_result(db: Session, gender: str, current_time: datetime = None) -> Dict:
    """
    獲取占卜結果的便捷函數
    """
    return divination_logic.perform_divination(gender, current_time, db)

# 導出
__all__ = ["DivinationLogic", "divination_logic", "get_divination_result"] 