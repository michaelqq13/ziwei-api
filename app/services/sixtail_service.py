"""
6tail時間資料整合服務
提供與舊計算方法相同的接口，但使用6tail系統查詢準確資料
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# 嘗試導入main.py中的SixTailCalendar，考慮不同的路徑
try:
    # 方法1：直接從項目根目錄導入
    from main import SixTailCalendar
except ImportError:
    try:
        # 方法2：添加項目根目錄到路徑後導入
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from main import SixTailCalendar
    except ImportError:
        # 如果都無法導入，設置為None，觸發維修模式
        SixTailCalendar = None

logger = logging.getLogger(__name__)

class SixTailService:
    """6tail時間資料服務"""
    
    def __init__(self):
        """初始化6tail服務"""
        try:
            if SixTailCalendar is None:
                raise ImportError("無法導入SixTailCalendar")
            self.calendar = SixTailCalendar()
            logger.info("6tail時間資料服務初始化成功")
        except Exception as e:
            logger.error(f"6tail服務初始化失敗: {e}")
            self.calendar = None
    
    def get_complete_info(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> Dict[str, Any]:
        """
        獲取完整的時間資料
        
        Args:
            year: 年
            month: 月
            day: 日
            hour: 時
            minute: 分
            
        Returns:
            完整的時間資料字典
            
        Raises:
            RuntimeError: 當6tail服務不可用時
        """
        if not self.calendar:
            logger.error("6tail服務未初始化，系統進入維修模式")
            raise RuntimeError("占卜系統目前維修中，請稍後再試。我們正在升級時間計算系統以提供更準確的服務。")
        
        try:
            return self.calendar.get_complete_calendar_info(year, month, day, hour, minute)
        except Exception as e:
            logger.error(f"6tail查詢失敗: {e}")
            raise RuntimeError("占卜系統目前維修中，請稍後再試。我們正在升級時間計算系統以提供更準確的服務。")
    
    def get_year_ganzhi(self, year: int) -> str:
        """獲取年干支"""
        info = self.get_complete_info(year, 1, 1)
        return info.get("ganzhi", {}).get("year", "甲子")
    
    def get_month_ganzhi(self, year: int, month: int) -> str:
        """獲取月干支"""
        info = self.get_complete_info(year, month, 1)
        return info.get("ganzhi", {}).get("month", "甲子")
    
    def get_day_ganzhi(self, year: int, month: int, day: int) -> str:
        """獲取日干支"""
        info = self.get_complete_info(year, month, day)
        return info.get("ganzhi", {}).get("day", "甲子")
    
    def get_hour_ganzhi(self, year: int, month: int, day: int, hour: int) -> str:
        """獲取時干支"""
        info = self.get_complete_info(year, month, day, hour)
        return info.get("ganzhi", {}).get("hour", "甲子")
    
    def get_minute_ganzhi(self, year: int, month: int, day: int, hour: int, minute: int) -> str:
        """獲取分干支"""
        info = self.get_complete_info(year, month, day, hour, minute)
        # 6tail系統暫時沒有分干支，使用時干支
        return info.get("ganzhi", {}).get("hour", "甲子")
    
    def get_lunar_info(self, year: int, month: int, day: int) -> Dict[str, Any]:
        """獲取農曆資訊"""
        info = self.get_complete_info(year, month, day)
        return info.get("lunar", {})
    
    def get_ganzhi_info(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> Dict[str, str]:
        """
        獲取完整干支資訊
        
        Returns:
            包含年月日時分干支的字典
            
        Raises:
            RuntimeError: 當6tail服務不可用時
        """
        info = self.get_complete_info(year, month, day, hour, minute)
        ganzhi = info.get("ganzhi", {})
        
        return {
            "year_ganzhi": ganzhi.get("year", "甲子"),
            "month_ganzhi": ganzhi.get("month", "甲子"),
            "day_ganzhi": ganzhi.get("day", "甲子"),
            "hour_ganzhi": ganzhi.get("hour", "甲子"),
            "minute_ganzhi": ganzhi.get("hour", "甲子"),  # 暫時使用時干支
            "data_source": "6tail"
        }
    
    def is_available(self) -> bool:
        """檢查6tail服務是否可用"""
        return self.calendar is not None

# 創建全局實例
sixtail_service = SixTailService() 