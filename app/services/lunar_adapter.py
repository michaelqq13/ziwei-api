"""
Lunar 適配器 - 使用 lunar_python 替代 sxtwl
提供與原有 sxtwl 相容的接口
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from lunar_python import Lunar, Solar
    HAS_LUNAR_PYTHON = True
except ImportError:
    HAS_LUNAR_PYTHON = False

logger = logging.getLogger(__name__)


class LunarAdapter:
    """使用 lunar_python 庫的農曆適配器"""
    
    def __init__(self):
        """初始化適配器"""
        self.available = HAS_LUNAR_PYTHON
        if not self.available:
            logger.error("lunar_python 庫未安裝，農曆計算功能不可用")
    
    def is_available(self) -> bool:
        """檢查適配器是否可用"""
        return self.available
    
    def get_lunar_data(self, year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict[str, Any]:
        """
        獲取農曆數據
        
        Args:
            year: 公曆年
            month: 公曆月
            day: 公曆日
            hour: 公曆時
            minute: 公曆分
            
        Returns:
            包含農曆數據的字典
        """
        if not self.available:
            raise RuntimeError("lunar_python 庫不可用")
            
        try:
            # 創建陽曆對象
            solar = Solar(year, month, day, hour, minute, 0)
            
            # 轉換為陰曆
            lunar = solar.getLunar()
            
            # 組織返回數據，與原有 sxtwl 格式保持一致
            lunar_year = lunar.getYear()
            lunar_month = abs(lunar.getMonth())  # 取絕對值
            lunar_day = lunar.getDay()
            is_leap = lunar.getMonth() < 0  # 負數表示閏月
            
            # 獲取干支數據
            year_ganzhi = lunar.getYearInGanZhi()
            month_ganzhi = lunar.getMonthInGanZhi()  
            day_ganzhi = lunar.getDayInGanZhi()
            
            # 處理時辰干支 - 需要根據時間計算
            hour_ganzhi = self._get_hour_ganzhi(hour)
            
            # 獲取中文農曆表示
            lunar_month_chinese = self._get_lunar_month_chinese(lunar_month, is_leap)
            lunar_day_chinese = self._get_lunar_day_chinese(lunar_day)
            
            return {
                'lunar_year': lunar_year,
                'lunar_month': lunar_month,
                'lunar_day': lunar_day,
                'is_leap_month': is_leap,
                'lunar_month_in_chinese': lunar_month_chinese,
                'lunar_day_in_chinese': lunar_day_chinese,
                'year_ganzhi': year_ganzhi,
                'month_ganzhi': month_ganzhi,
                'day_ganzhi': day_ganzhi,
                'hour_ganzhi': hour_ganzhi,
                'solar_date': f"{year}-{month:02d}-{day:02d}",
                'lunar_date': f"{lunar_year}-{lunar_month:02d}-{lunar_day:02d}",
                'full_lunar_string': lunar.toString()
            }
            
        except Exception as e:
            logger.error(f"獲取農曆數據失敗: {e}")
            raise RuntimeError(f"農曆數據計算失敗: {e}")
    
    def _get_hour_ganzhi(self, hour: int) -> str:
        """
        根據時間獲取時辰干支
        
        Args:
            hour: 小時 (0-23)
            
        Returns:
            時辰地支
        """
        # 時辰對應表
        hour_branches = [
            "子", "丑", "丑", "寅", "寅", "卯", 
            "卯", "辰", "辰", "巳", "巳", "午",
            "午", "未", "未", "申", "申", "酉", 
            "酉", "戌", "戌", "亥", "亥", "子"
        ]
        
        return hour_branches[hour]
    
    def _get_lunar_month_chinese(self, month: int, is_leap: bool) -> str:
        """
        獲取農曆月份的中文表示
        
        Args:
            month: 農曆月份數字
            is_leap: 是否閏月
            
        Returns:
            中文月份表示
        """
        month_names = {
            1: "正月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月",
            7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "冬月", 12: "腊月"
        }
        
        base_name = month_names.get(month, f"{month}月")
        return f"閏{base_name}" if is_leap else base_name
    
    def _get_lunar_day_chinese(self, day: int) -> str:
        """
        獲取農曆日期的中文表示
        
        Args:
            day: 農曆日期數字
            
        Returns:
            中文日期表示
        """
        if day <= 10:
            return f"初{['十', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'][day]}"
        elif day < 20:
            return f"十{['十', '一', '二', '三', '四', '五', '六', '七', '八', '九'][day - 10]}"
        elif day == 20:
            return "二十"
        elif day < 30:
            return f"廿{['十', '一', '二', '三', '四', '五', '六', '七', '八', '九'][day - 20]}"
        elif day == 30:
            return "三十"
        else:
            return f"{day}日"


# 創建全局實例
lunar_adapter = LunarAdapter() 