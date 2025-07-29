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
from app.models.linebot_models import DivinationHistory, LineBotUser
from app.data.heavenly_stems.four_transformations import four_transformations_explanations

# 設置日誌
import logging
from datetime import datetime, timezone, timedelta

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

class TaipeiFormatter(logging.Formatter):
    """台北時區的日誌格式化器"""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=TAIPEI_TZ)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

# 設置日誌，使用台北時區
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 為所有處理程序設置台北時區格式化器  
for handler in logging.root.handlers:
    handler.setFormatter(TaipeiFormatter('%(asctime)s - %(levelname)s - %(message)s'))

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

    def perform_divination(self, user: LineBotUser, gender: str, current_time: datetime = None, db: Optional[Session] = None) -> Dict:
        """
        執行占卜邏輯 - 簡化版本，使用太極盤架構
        
        Args:
            user: 進行占卜的用戶物件
            gender: 性別
            current_time: 指定時間（可選，默認使用當前時間）
            db: 數據庫會話（可選）
            
        Returns:
            Dict: 占卜結果
        """
        try:
            logger.info(f"🔍 perform_divination 收到參數 - current_time: {current_time}")
            
            # 1. 獲取當前時間（台北時間）
            if current_time is None:
                current_time = get_current_taipei_time()
                logger.info(f"⚠️ current_time 為 None，使用當前時間: {current_time}")
            else:
                logger.info(f"✅ 使用指定時間: {current_time}")
            
            logger.info(f"開始占卜 - User: {user.line_user_id if user else 'N/A'}, 時間：{current_time}，性別：{gender}，數據庫：{'有' if db else '無'}")
            
            # 2. 計算分鐘地支（太極點）
            minute_dizhi = self.get_minute_dizhi(current_time)
            logger.info(f"太極點地支：{minute_dizhi}")
            
            # 3. 創建原盤
            chart = PurpleStarChart(
                year=current_time.year,
                month=current_time.month,
                day=current_time.day,
                hour=current_time.hour,
                minute=current_time.minute,
                gender=gender,
                db=db
            )
            
            logger.info("原盤創建完成")
            
            # 4. 應用太極點旋轉，將原盤轉換為太極盤
            chart.apply_taichi(minute_dizhi)
            logger.info("太極盤轉換完成")
            
            # 5. 獲取太極點天干（現在太極盤的命宮天干）
            taichi_palace = chart.palaces.get("命宮")
            if not taichi_palace:
                raise ValueError("太極盤中未找到命宮")
            
            palace_tiangan = taichi_palace.stem
            logger.info(f"太極點天干：{palace_tiangan}")
            
            # 6. 取得太極盤資料（在保存前先獲取）
            taichi_chart_data = chart.get_chart()
            logger.info("太極盤資料獲取完成")
            
            # 調試：檢查太極盤數據結構
            palaces_data = taichi_chart_data.get("palaces", {})
            logger.info(f"太極盤宮位數量: {len(palaces_data)}")
            logger.info(f"太極盤宮位名稱: {list(palaces_data.keys())}")
            
            # 顯示前3個宮位的詳細數據（避免日誌過長）
            for i, (palace_name, palace_data) in enumerate(palaces_data.items()):
                if i < 3:
                    logger.info(f"宮位 {palace_name} 數據: tiangan={palace_data.get('tiangan')}, dizhi={palace_data.get('dizhi')}, stars={len(palace_data.get('stars', []))}")
                if i >= 3:
                    break
            
            # 7. 基於太極盤獲取四化解釋
            sihua_results = chart.get_taichi_sihua_explanations(palace_tiangan)
            logger.info(f"四化解釋獲取完成，共 {len(sihua_results)} 個")
            
            # 8. 保存占卜記錄（僅在有數據庫且用戶存在時）
            divination_id = None
            if db is not None and user and hasattr(user, 'id') and user.id is not None:
                try:
                    sihua_json = json.dumps(sihua_results, ensure_ascii=False)
                    taichi_mapping_json = json.dumps(chart.taichi_palace_mapping, ensure_ascii=False)
                    taichi_chart_json = json.dumps(taichi_chart_data.get("palaces", {}), ensure_ascii=False)
                    
                    # 調試：檢查要保存的數據
                    logger.info(f"準備保存 - 太極映射: {len(chart.taichi_palace_mapping)} 個")
                    logger.info(f"準備保存 - 太極盤宮位: {len(taichi_chart_data.get('palaces', {}))} 個")
                    logger.info(f"太極映射 JSON 長度: {len(taichi_mapping_json)} 字符")
                    logger.info(f"太極盤 JSON 長度: {len(taichi_chart_json)} 字符")
                    
                    divination_record = DivinationHistory(
                        user_id=user.id,
                        gender=gender,
                        divination_time=current_time,
                        taichi_palace=f"{minute_dizhi}宮",
                        minute_dizhi=minute_dizhi,
                        sihua_results=sihua_json,
                        taichi_palace_mapping=taichi_mapping_json,
                        taichi_chart_data=taichi_chart_json
                    )
                    
                    db.add(divination_record)
                    db.commit()
                    divination_id = divination_record.id
                    logger.info(f"占卜記錄已保存，ID：{divination_id}，包含太極宮對映資訊")
                except Exception as e:
                    logger.warning(f"保存占卜記錄失敗（將繼續占卜功能）：{e}")
                    if db:
                        db.rollback()
            else:
                logger.info("簡化模式或無用戶信息：跳過占卜記錄保存")
            
            # 9. 構建四化星對應表（為了向後兼容）
            sihua_stars = {}
            for result in sihua_results:
                sihua_stars[result["type"]] = result["star"]
            
            # 10. 返回結果
            result = {
                "success": True,
                "divination_id": divination_id,
                "divination_time": current_time.isoformat(),
                "trigger_time": current_time.isoformat(),
                "gender": gender,
                "taichi_palace": f"{minute_dizhi}宮",
                "minute_dizhi": minute_dizhi,
                "palace_tiangan": palace_tiangan,
                "sihua_stars": sihua_stars,
                "taichi_chart": taichi_chart_data.get("palaces", {}),  # 太極盤資料
                "basic_chart": taichi_chart_data.get("palaces", {}),   # 向後兼容
                "sihua_results": sihua_results,
                "taichi_palace_mapping": chart.taichi_palace_mapping,
                "simplified_mode": getattr(chart, 'simplified_mode', False)
            }
            
            logger.info(f"占卜完成，模式：{'簡化' if result.get('simplified_mode', False) else '正常'}")
            logger.info(f"太極盤四化結果：{[(r['star'], r['type'], r['palace']) for r in sihua_results]}")
            
            return result
            
        except Exception as e:
            logger.error(f"占卜過程發生錯誤：{e}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "message": "占卜過程發生錯誤，請稍後重試"
            }

# 全局實例
divination_logic = DivinationLogic()

def get_divination_result(db: Optional[Session], user: LineBotUser, gender: str, current_time: datetime = None) -> Dict:
    """
    執行占卜並返回結果（支持可選數據庫）
    
    Args:
        db: 數據庫會話（可選）
        user: LineBotUser 物件
        gender: 性別
        current_time: 指定時間（可選）
        
    Returns:
        Dict: 占卜結果
    """
    try:
        logger.info(f"🔍 get_divination_result 收到參數 - current_time: {current_time}")
        
        divination_logic = DivinationLogic()
        result = divination_logic.perform_divination(user, gender, current_time, db)
        
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