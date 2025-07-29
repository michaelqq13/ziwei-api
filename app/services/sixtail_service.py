"""
6tail時間資料整合服務
提供與舊計算方法相同的接口，但使用lunar_python系統查詢準確資料
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 使用 lunar_adapter 替代 sxtwl
try:
    from .lunar_adapter import lunar_adapter
    HAS_LUNAR_ADAPTER = True
except ImportError:
    HAS_LUNAR_ADAPTER = False
    lunar_adapter = None

logger = logging.getLogger(__name__)


class SixTailService:
    """6tail時間資料服務 - 使用 lunar_python 實現"""

    def __init__(self):
        """初始化6tail服務"""
        self.available = HAS_LUNAR_ADAPTER and lunar_adapter and lunar_adapter.is_available()
        
        if not self.available:
            logger.error("Lunar adapter 不可用，農曆計算功能將無法使用")
            logger.error("請確保已安裝 lunar_python: pip install lunar_python")
        else:
            logger.info("6tail時間資料服務初始化成功 (使用 lunar_python)")

    def is_available(self) -> bool:
        """檢查服務是否可用"""
        return self.available

    def get_lunar_info(self, year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict[str, Any]:
        """
        獲取指定時間的完整農曆信息
        
        Args:
            year: 公曆年
            month: 公曆月  
            day: 公曆日
            hour: 公曆時
            minute: 公曆分
            
        Returns:
            包含完整農曆信息的字典
        """
        if not self.available:
            raise RuntimeError("6tail服務不可用，無法計算農曆信息")
            
        try:
            logger.info(f"查詢農曆信息: {year}-{month}-{day} {hour}:{minute}")
            
            # 使用 lunar_adapter 獲取數據
            lunar_data = lunar_adapter.get_lunar_data(year, month, day, hour, minute)
            
            # 轉換為與原有 sxtwl 兼容的格式
            result = {
                'solar_year': year,
                'solar_month': month,
                'solar_day': day,
                'solar_hour': hour,
                'solar_minute': minute,
                'lunar_year': lunar_data['lunar_year'],
                'lunar_month': lunar_data['lunar_month'],
                'lunar_day': lunar_data['lunar_day'],
                'is_leap_month': lunar_data['is_leap_month'],
                'lunar_month_in_chinese': lunar_data['lunar_month_in_chinese'],
                'lunar_day_in_chinese': lunar_data['lunar_day_in_chinese'],
                'year_ganzhi': lunar_data['year_ganzhi'],
                'month_ganzhi': lunar_data['month_ganzhi'], 
                'day_ganzhi': lunar_data['day_ganzhi'],
                'hour_ganzhi': lunar_data['hour_ganzhi'],
                'full_string': lunar_data['full_lunar_string']
            }
            
            logger.info(f"成功獲取農曆信息: {result['lunar_year']}年{result['lunar_month_in_chinese']}{result['lunar_day_in_chinese']}")
            return result
            
        except Exception as e:
            logger.error(f"獲取農曆信息失敗: {e}")
            raise RuntimeError(f"農曆信息計算失敗: {e}")

    def get_ganzhi_info(self, year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict[str, str]:
        """
        獲取干支信息
        
        Args:
            year: 公曆年
            month: 公曆月
            day: 公曆日
            hour: 公曆時
            minute: 公曆分
            
        Returns:
            包含年月日時干支的字典
        """
        if not self.available:
            raise RuntimeError("6tail服務不可用，無法計算干支信息")
            
        try:
            lunar_info = self.get_lunar_info(year, month, day, hour, minute)
            
            return {
                'year_ganzhi': lunar_info['year_ganzhi'],
                'month_ganzhi': lunar_info['month_ganzhi'],
                'day_ganzhi': lunar_info['day_ganzhi'],
                'hour_ganzhi': lunar_info['hour_ganzhi']
            }
            
        except Exception as e:
            logger.error(f"獲取干支信息失敗: {e}")
            raise RuntimeError(f"干支信息計算失敗: {e}")

    def format_time_for_query(self, dt: datetime) -> str:
        """
        格式化時間用於查詢
        
        Args:
            dt: datetime 對象
            
        Returns:
            格式化的時間字符串
        """
        return f"{dt.year}-{dt.month}-{dt.day} {dt.hour}:{dt.minute}"


# 創建全局實例
sixtail_service = SixTailService() 