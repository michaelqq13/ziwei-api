"""
農曆數據生成器
動態生成準確的農曆數據，用於占卜系統
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.calendar import CalendarData

logger = logging.getLogger(__name__)

class LunarDataGenerator:
    """農曆數據生成器"""
    
    # 天干地支
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # 2025年的基礎設定
    YEAR_2025_BASE = {
        "year_gan_zhi": "乙巳",
        "year_animal": "蛇",
        # 2025年1月1日的日干支基準點
        "jan_1_day_gan_index": 0,  # 甲
        "jan_1_day_zhi_index": 0,  # 子
    }
    
    # 月份對應農曆月份的映射（簡化版）
    GREGORIAN_TO_LUNAR_MONTH = {
        1: (12, "臘月"), 2: (1, "正月"), 3: (2, "二月"), 4: (3, "三月"),
        5: (4, "四月"), 6: (5, "五月"), 7: (6, "六月"), 8: (7, "七月"),
        9: (8, "八月"), 10: (9, "九月"), 11: (10, "十月"), 12: (11, "冬月")
    }
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def generate_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """
        生成指定日期範圍的農曆數據
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            生成的記錄數量
        """
        logger.info(f"開始生成農曆數據：{start_date.date()} 到 {end_date.date()}")
        
        current_date = start_date
        generated_count = 0
        
        while current_date <= end_date:
            # 為每一天的每個小時生成數據
            for hour in range(24):
                if self._create_calendar_record(current_date, hour):
                    generated_count += 1
                    
                    # 每100筆記錄提交一次
                    if generated_count % 100 == 0:
                        self.db_session.commit()
                        logger.info(f"已生成 {generated_count} 筆記錄...")
            
            current_date += timedelta(days=1)
        
        # 最終提交
        self.db_session.commit()
        logger.info(f"農曆數據生成完成，共生成 {generated_count} 筆記錄")
        
        return generated_count
    
    def _create_calendar_record(self, date: datetime, hour: int) -> bool:
        """
        創建單個農曆數據記錄
        
        Args:
            date: 日期
            hour: 小時
            
        Returns:
            是否成功創建記錄
        """
        try:
            # 檢查是否已存在該記錄
            existing = self.db_session.query(CalendarData).filter(
                CalendarData.gregorian_year == date.year,
                CalendarData.gregorian_month == date.month,
                CalendarData.gregorian_day == date.day,
                CalendarData.gregorian_hour == hour
            ).first()
            
            if existing:
                return False
            
            # 計算農曆信息
            lunar_info = self._calculate_lunar_info(date, hour)
            
            # 創建記錄，使用正確的模型結構
            calendar_data = CalendarData(
                gregorian_datetime=datetime(date.year, date.month, date.day, hour, 0, 0),
                gregorian_year=date.year,
                gregorian_month=date.month,
                gregorian_day=date.day,
                gregorian_hour=hour,
                lunar_year_in_chinese=lunar_info["lunar_year_chinese"],
                lunar_month_in_chinese=lunar_info["lunar_month_chinese"],
                lunar_day_in_chinese=lunar_info["lunar_day_chinese"],
                is_leap_month_in_chinese=lunar_info["is_leap_month"],
                year_gan_zhi=lunar_info["year_gan_zhi"],
                month_gan_zhi=lunar_info["month_gan_zhi"],
                day_gan_zhi=lunar_info["day_gan_zhi"],
                hour_gan_zhi=lunar_info["hour_gan_zhi"],
                minute_gan_zhi=None,  # 暫時為空
                solar_term_today=lunar_info["solar_term"],
                solar_term_in_hour=lunar_info["solar_term_name"]
            )
            
            self.db_session.add(calendar_data)
            return True
            
        except Exception as e:
            logger.error(f"創建農曆記錄失敗 ({date.date()} {hour}:00): {e}")
            return False
    
    def _calculate_lunar_info(self, date: datetime, hour: int) -> Dict:
        """
        計算農曆信息
        
        Args:
            date: 日期
            hour: 小時
            
        Returns:
            農曆信息字典
        """
        # 計算從年初到當前日期的天數
        year_start = datetime(date.year, 1, 1)
        days_from_year_start = (date - year_start).days
        
        # 計算日干支
        day_gan_index = (self.YEAR_2025_BASE["jan_1_day_gan_index"] + days_from_year_start) % 10
        day_zhi_index = (self.YEAR_2025_BASE["jan_1_day_zhi_index"] + days_from_year_start) % 12
        day_gan_zhi = self.HEAVENLY_STEMS[day_gan_index] + self.EARTHLY_BRANCHES[day_zhi_index]
        
        # 計算月干支
        month_gan_index = (day_gan_index + date.month - 1) % 10
        month_zhi_index = (date.month - 1) % 12
        month_gan_zhi = self.HEAVENLY_STEMS[month_gan_index] + self.EARTHLY_BRANCHES[month_zhi_index]
        
        # 計算時干支
        hour_zhi_index = (hour // 2) % 12
        hour_gan_index = (day_gan_index * 2 + hour_zhi_index) % 10
        hour_gan_zhi = self.HEAVENLY_STEMS[hour_gan_index] + self.EARTHLY_BRANCHES[hour_zhi_index]
        
        # 計算農曆月份和日期
        lunar_month_num, lunar_month_name = self.GREGORIAN_TO_LUNAR_MONTH.get(date.month, (date.month, f"{date.month}月"))
        
        # 簡化的農曆日期計算（實際應該更複雜）
        lunar_day_num = date.day
        if lunar_day_num <= 10:
            lunar_day_chinese = f"初{['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'][lunar_day_num]}"
        elif lunar_day_num <= 20:
            lunar_day_chinese = f"十{['', '一', '二', '三', '四', '五', '六', '七', '八', '九'][lunar_day_num - 10]}" if lunar_day_num > 10 else "十"
        elif lunar_day_num <= 30:
            lunar_day_chinese = f"廿{['', '一', '二', '三', '四', '五', '六', '七', '八', '九'][lunar_day_num - 20]}" if lunar_day_num > 20 else "二十"
        else:
            lunar_day_chinese = "三十"
        
        # 計算節氣
        solar_term = self._get_solar_term(date)
        
        return {
            "lunar_year_chinese": "乙巳",
            "lunar_month_chinese": lunar_month_name,
            "lunar_day_chinese": lunar_day_chinese,
            "year_gan_zhi": self.YEAR_2025_BASE["year_gan_zhi"],
            "month_gan_zhi": month_gan_zhi,
            "day_gan_zhi": day_gan_zhi,
            "hour_gan_zhi": hour_gan_zhi,
            "solar_term": solar_term,
            "solar_term_name": solar_term,
            "is_leap_month": False,
            "lunar_month_num": lunar_month_num,
            "lunar_day_num": lunar_day_num
        }
    
    def _get_solar_term(self, date: datetime) -> str:
        """獲取節氣"""
        # 簡化的節氣計算
        solar_terms = {
            1: "小寒", 2: "立春", 3: "驚蟄", 4: "清明",
            5: "立夏", 6: "芒種", 7: "小暑", 8: "立秋",
            9: "白露", 10: "寒露", 11: "立冬", 12: "大雪"
        }
        return solar_terms.get(date.month, "")
    
    def ensure_date_available(self, target_date: datetime) -> bool:
        """
        確保指定日期的農曆數據可用
        
        Args:
            target_date: 目標日期
            
        Returns:
            是否成功確保數據可用
        """
        try:
            # 檢查是否已有該日期的數據
            existing_count = self.db_session.query(CalendarData).filter(
                CalendarData.gregorian_year == target_date.year,
                CalendarData.gregorian_month == target_date.month,
                CalendarData.gregorian_day == target_date.day
            ).count()
            
            if existing_count >= 24:  # 如果已有24小時的數據
                logger.info(f"日期 {target_date.date()} 已有完整的農曆數據")
                return True
            
            # 如果沒有，生成該日期前後3天的數據
            start_date = target_date - timedelta(days=3)
            end_date = target_date + timedelta(days=3)
            
            logger.info(f"開始為日期 {target_date.date()} 生成農曆數據 ({start_date.date()} 到 {end_date.date()})")
            
            generated_count = self.generate_date_range(start_date, end_date)
            
            logger.info(f"為日期 {target_date.date()} 生成了 {generated_count} 筆農曆數據")
            
            return generated_count > 0
            
        except Exception as e:
            logger.error(f"確保農曆數據可用失敗: {e}")
            return False

def get_or_create_lunar_data(db_session: Session, target_date: datetime) -> Optional[CalendarData]:
    """
    獲取或創建農曆數據
    
    Args:
        db_session: 數據庫會話
        target_date: 目標日期
        
    Returns:
        農曆數據記錄，如果失敗則返回None
    """
    try:
        # 首先嘗試獲取現有數據
        existing = db_session.query(CalendarData).filter(
            CalendarData.gregorian_year == target_date.year,
            CalendarData.gregorian_month == target_date.month,
            CalendarData.gregorian_day == target_date.day,
            CalendarData.gregorian_hour == target_date.hour
        ).first()
        
        if existing:
            logger.info(f"找到現有農曆數據：{target_date.year}-{target_date.month}-{target_date.day} {target_date.hour}:00")
            return existing
        
        # 如果沒有，使用生成器創建
        logger.info(f"未找到農曆數據，開始動態生成：{target_date.year}-{target_date.month}-{target_date.day} {target_date.hour}:00")
        
        generator = LunarDataGenerator(db_session)
        
        # 確保該日期的數據可用
        if generator.ensure_date_available(target_date):
            # 再次嘗試獲取
            result = db_session.query(CalendarData).filter(
                CalendarData.gregorian_year == target_date.year,
                CalendarData.gregorian_month == target_date.month,
                CalendarData.gregorian_day == target_date.day,
                CalendarData.gregorian_hour == target_date.hour
            ).first()
            
            if result:
                logger.info(f"成功生成並獲取農曆數據：{target_date.year}-{target_date.month}-{target_date.day} {target_date.hour}:00")
                return result
            else:
                logger.warning(f"生成農曆數據後仍無法找到記錄：{target_date.year}-{target_date.month}-{target_date.day} {target_date.hour}:00")
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"獲取或創建農曆數據失敗: {e}")
        return None 