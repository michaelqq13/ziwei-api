"""
占卜邏輯系統
實現基於當下時間和性別的太極點占卜算法
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
import traceback

from app.logic.purple_star_chart import PurpleStarChart
from app.config.linebot_config import LineBotConfig
from app.utils.chinese_calendar import ChineseCalendar
from app.models.birth_info import BirthInfo
from app.models.divination import DivinationRecord
from app.models.user_preferences import UserPreferences
from app.db.repository import CalendarRepository
from app.data.heavenly_stems.four_transformations import four_transformations_explanations

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

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
                    raw_name = star.get("name", "") if isinstance(star, dict) else str(star)
                    if not raw_name:
                        continue
                    # 移除四化標記及括號描述
                    clean_name = raw_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
                    if "（" in clean_name:
                        clean_name = clean_name.split("（")[0]
                    clean_name = clean_name.strip()
                    star_palace_map[clean_name] = palace_name
            
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
        
        def _get_detailed_explanation(star_name: str, trans_type: str, palace: str) -> Optional[dict]:
            """嘗試從完整資料庫 four_transformations_explanations 取得對應解釋"""
            fallback_entry = None
            for stem_data in four_transformations_explanations.values():
                if trans_type not in stem_data:
                    continue
                trans_info = stem_data[trans_type]
                # 1) 精準：主星 + 宮位
                if trans_info.get("主星") == star_name:
                    for entry in trans_info.get("解釋", []):
                        if entry.get("宮位") == palace:
                            return entry
                # 2) 次精準：僅宮位 (先記下，若沒主星版本才用)
                for entry in trans_info.get("解釋", []):
                    if entry.get("宮位") == palace and fallback_entry is None:
                        fallback_entry = entry
            return fallback_entry
        
        results = []
        for sihua_info in sihua_results:
            sihua_type = sihua_info["type"]
            palace = sihua_info["palace"]
            star = sihua_info["star"]
            
            # 獲取解釋，先嘗試詳細資料庫
            detailed = _get_detailed_explanation(star, sihua_type, palace)
            if detailed:
                explanation_text = detailed.get("現象", "")
                psych = detailed.get("心理傾向", "")
                event = detailed.get("可能事件", "")
                tip = detailed.get("提示", "")
                advice = detailed.get("來意不明建議", "")
                combined = "\n".join([t for t in [explanation_text, psych, event, tip, advice] if t])
            else:
                # 回退到僅宮位匹配（或簡化版）
                type_explanations = explanations.get(sihua_type, {})
                combined = type_explanations.get(palace, type_explanations.get("default", "運勢平穩。"))
            
            results.append({
                "type": sihua_type,
                "transformation_type": sihua_type,
                "star": star,
                "star_name": star,
                "palace": palace,
                "original_palace": sihua_info["original_palace"],
                "taichi_palace": sihua_info["taichi_palace"],
                "star_branch": sihua_info["star_branch"],
                "explanation": combined
            })
        
        return results
    
    def get_taichi_palace_mapping(self, taichi_branch: str) -> Dict[str, str]:
        """
        根據太極點命宮地支重新分佈十二宮位
        
        Args:
            taichi_branch: 太極點命宮的地支
            
        Returns:
            Dict[str, str]: 地支到新宮位名稱的映射
        """
        # 十二地支順序
        branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 十二宮位順序（以命宮為起點）
        palace_names = ["命宮", "父母宮", "福德宮", "田宅宮", "官祿宮", "交友宮", 
                       "遷移宮", "疾厄宮", "財帛宮", "子女宮", "夫妻宮", "兄弟宮"]
        
        # 找到太極點命宮地支的索引
        try:
            taichi_index = branches.index(taichi_branch)
        except ValueError:
            logger.error(f"無效的太極點地支: {taichi_branch}")
            taichi_index = 0  # 默認從子開始
        
        # 建立新的地支到宮位映射
        branch_to_palace = {}
        for i in range(12):
            branch_index = (taichi_index + i) % 12
            branch = branches[branch_index]
            palace = palace_names[i]
            branch_to_palace[branch] = palace
            
        logger.info(f"太極點命宮 {taichi_branch} 的宮位重新分佈: {branch_to_palace}")
        return branch_to_palace

    def perform_divination(self, gender: str, current_time: datetime = None, db: Optional[Session] = None) -> Dict:
        """
        執行占卜邏輯
        
        Args:
            gender: 性別
            current_time: 指定時間（可選，默認使用當前時間）
            db: 數據庫會話（可選）
            
        Returns:
            Dict: 占卜結果
        """
        try:
            # 1. 獲取當前時間（台北時間）
            if current_time is None:
                current_time = get_current_taipei_time()
            
            logger.info(f"開始占卜 - 時間：{current_time}，性別：{gender}，數據庫：{'有' if db else '無'}")
            
            # 2. 計算太極點命宮
            taichi_palace_name, taichi_info = self.calculate_taichi_palace(gender, current_time, db)
            minute_dizhi = taichi_info["minute_dizhi"]
            palace_tiangan = taichi_info["palace_tiangan"]
            
            logger.info(f"太極點計算完成 - 命宮：{taichi_palace_name}，地支：{minute_dizhi}，天干：{palace_tiangan}")
            
            # 3. 計算四化星
            sihua_stars = self.calculate_sihua(palace_tiangan)
            logger.info(f"四化星：{sihua_stars}")
            
            # 4. 創建命盤獲取星曜位置
            chart = PurpleStarChart(
                year=current_time.year,
                month=current_time.month,
                day=current_time.day,
                hour=current_time.hour,
                minute=current_time.minute,
                gender=gender,
                db=db
            )
            
            chart_data = chart.get_chart()
            
            # 5. 獲取星曜宮位對應
            star_palace_map = self.get_star_palace_mapping(chart_data)
            
            # 6. 計算太極點宮位映射
            taichi_mapping = self.get_taichi_palace_mapping(minute_dizhi)
            
            # 7. 產生四化結果
            sihua_results = []
            for trans_type, star_name in sihua_stars.items():
                # 獲取該星在命盤的地支位置
                star_branch = self.get_star_branch_from_chart(chart_data, star_name)
                # 原本落宮
                original_palace = star_palace_map.get(star_name, "命宮")
                if star_name not in star_palace_map:
                    logger.warning(f"未找到星曜 {star_name} 的宮位，使用預設宮位")
                # 根據太極點重新對應宮位：使用星曜地支映射
                taichi_palace = taichi_mapping.get(star_branch, original_palace)
                
                sihua_result = {
                    "type": trans_type,  # 四化類型（祿、權、科、忌）
                    "transformation_type": trans_type,  # 與舊版字段兼容
                    "star": star_name,   # 星曜名稱
                    "star_name": star_name,  # 與舊版字段兼容
                    "palace": taichi_palace,  # 依太極點轉換後的宮位
                    "original_palace": original_palace,  # 原本落宮
                    "taichi_palace": taichi_palace,  # 太極點後落宮（語義相同，向後兼容）
                    "star_branch": star_branch
                }
                
                sihua_results.append(sihua_result)
            
            # 8. 獲取四化解釋
            explanations = self.get_sihua_explanations(sihua_results)
            for i, explanation in enumerate(explanations):
                sihua_results[i]["explanation"] = explanation["explanation"]
            
            # 9. 保存占卜記錄（僅在有數據庫時）
            divination_id = None
            if db is not None:
                try:
                    from app.models.divination import DivinationRecord
                    
                    divination_record = DivinationRecord(
                        trigger_time=current_time,
                        trigger_stem=palace_tiangan,
                        trigger_branch=minute_dizhi,
                        taichi_palace=taichi_palace_name,
                        sihua_explanations=str(sihua_results)
                    )
                    
                    db.add(divination_record)
                    db.commit()
                    divination_id = divination_record.id
                    logger.info(f"占卜記錄已保存，ID：{divination_id}")
                except Exception as e:
                    logger.warning(f"保存占卜記錄失敗（將繼續占卜功能）：{e}")
                    if db:
                        db.rollback()
            else:
                logger.info("簡化模式：跳過占卜記錄保存")
            
            # 10. 返回結果
            result = {
                "success": True,
                "divination_id": divination_id,
                "divination_time": current_time.isoformat(),  # 與其他模組保持一致
                "trigger_time": current_time.isoformat(),      # 向後兼容
                "gender": gender,
                "taichi_palace": taichi_palace_name,
                "minute_dizhi": minute_dizhi,
                "palace_tiangan": palace_tiangan,
                "sihua_stars": sihua_stars,
                "basic_chart": chart_data.get("palaces", {}),
                "taichi_palace_mapping": taichi_mapping,
                "taichi_mapping": taichi_mapping,  # 向後兼容
                "sihua_results": sihua_results,
                "simplified_mode": getattr(chart, 'simplified_mode', False)
            }
            
            logger.info(f"占卜完成，模式：{'簡化' if result.get('simplified_mode', False) else '正常'}")
            return result
            
        except Exception as e:
            logger.error(f"占卜過程發生錯誤：{e}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "message": "占卜過程發生錯誤，請稍後重試"
            }

    def get_star_branch_from_chart(self, chart_data: Dict, star_name: str) -> str:
        """
        從命盤數據中獲取指定星曜所在的地支
        
        Args:
            chart_data: 命盤數據
            star_name: 星曜名稱
            
        Returns:
            str: 星曜所在的地支
        """
        try:
            palaces = chart_data.get("palaces", {})
            logger.info(f"開始查找星曜 {star_name} 的地支")
            logger.info(f"命盤宮位數量：{len(palaces)}")
            
            # 清理目標星曜名稱，去除可能的四化標記
            clean_target_star = star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
            if "（" in clean_target_star:
                clean_target_star = clean_target_star.split("（")[0]
            clean_target_star = clean_target_star.strip()
            
            logger.info(f"清理後的目標星曜名稱：{clean_target_star}")
            
            # 遍歷所有宮位查找星曜
            for palace_name, palace_info in palaces.items():
                if isinstance(palace_info, dict):
                    # 獲取宮位的地支
                    palace_branch = palace_info.get("dizhi", palace_info.get("branch", ""))
                    logger.info(f"檢查宮位 {palace_name}，地支：{palace_branch}")
                    
                    # 獲取宮位內的星曜
                    stars = palace_info.get("stars", [])
                    logger.info(f"宮位 {palace_name} 內的星曜：{stars}")
                    
                    for star in stars:
                        # 清理星曜名稱，去除狀態描述和四化標記
                        clean_star = str(star)
                        if isinstance(star, dict):
                            clean_star = star.get("name", str(star))
                        
                        # 移除四化標記
                        clean_star = clean_star.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
                        # 移除狀態描述（如入廟、旺等）
                        if "（" in clean_star:
                            clean_star = clean_star.split("（")[0]
                        clean_star = clean_star.strip()
                        
                        logger.info(f"比對星曜：{clean_star} vs {clean_target_star}")
                        
                        if clean_star == clean_target_star:
                            logger.info(f"✅ 找到星曜 {star_name} 在地支 {palace_branch}（宮位：{palace_name}）")
                            return palace_branch
                else:
                    logger.warning(f"宮位 {palace_name} 的資料格式不正確：{type(palace_info)}")
            
            logger.warning(f"❌ 未找到星曜 {star_name} 的地支，可能的原因：")
            logger.warning("1. 星曜名稱不匹配")
            logger.warning("2. 星曜不在基本十四主星中")
            logger.warning("3. 資料結構問題")
            
            # 打印所有宮位的星曜以供調試
            logger.info("=== 所有宮位星曜列表 ===")
            for palace_name, palace_info in palaces.items():
                if isinstance(palace_info, dict):
                    stars = palace_info.get("stars", [])
                    branch = palace_info.get("dizhi", palace_info.get("branch", ""))
                    logger.info(f"{palace_name}（{branch}）：{stars}")
            
            # 如果是基本十四主星，應該能找到，如果找不到說明有問題
            main_stars = ["紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"]
            if clean_target_star in main_stars:
                logger.error(f"⚠️ 主星 {clean_target_star} 未找到，這可能是系統錯誤")
            
            return "子"  # 默認值
            
        except Exception as e:
            logger.error(f"獲取星曜地支錯誤: {e}")
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
            return "子"  # 默認值

# 全局實例
divination_logic = DivinationLogic()

def get_divination_result(db: Optional[Session], gender: str, current_time: datetime = None) -> Dict:
    """
    執行占卜並返回結果（支持可選數據庫）
    
    Args:
        db: 數據庫會話（可選）
        gender: 性別
        current_time: 指定時間（可選）
        
    Returns:
        Dict: 占卜結果
    """
    try:
        divination_logic = DivinationLogic()
        result = divination_logic.perform_divination(gender, current_time, db)
        
        logger.info(f"占卜結果獲取完成，成功：{result.get('success', False)}")
        return result
        
    except Exception as e:
        logger.error(f"獲取占卜結果錯誤：{e}")
        return {
            "success": False,
            "error": str(e),
            "message": "占卜服務暫時不可用，請稍後重試"
        }

# 導出
__all__ = ["DivinationLogic", "divination_logic", "get_divination_result"] 