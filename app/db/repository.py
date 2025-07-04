from typing import Optional
from sqlalchemy.orm import Session
from app.models.calendar import CalendarData
from app.models.birth_info import BirthInfo
# 移除動態生成器的導入，停用動態生成功能
# from app.utils.lunar_data_generator import get_or_create_lunar_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CalendarRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_calendar_data(self, birth_info: BirthInfo) -> Optional[CalendarData]:
        # 修正查詢邏輯：需要查詢對應小時的記錄，因為時干支會隨時辰變化
        
        # 首先嘗試從現有數據中獲取對應小時的記錄
        existing_data = self.db_session.query(CalendarData).filter(
            CalendarData.gregorian_year == birth_info.year,
            CalendarData.gregorian_month == birth_info.month,
            CalendarData.gregorian_day == birth_info.day,
            CalendarData.gregorian_hour == birth_info.hour
        ).first()
        
        if existing_data:
            logger.info(f"找到現有農曆數據：{birth_info.year}-{birth_info.month}-{birth_info.day} {birth_info.hour}:00")
            return existing_data
        
        # 如果沒有找到對應小時的記錄，嘗試查找當天的任一記錄作為備選
        fallback_data = self.db_session.query(CalendarData).filter(
            CalendarData.gregorian_year == birth_info.year,
            CalendarData.gregorian_month == birth_info.month,
            CalendarData.gregorian_day == birth_info.day
        ).first()
        
        if fallback_data:
            logger.warning(f"未找到 {birth_info.hour}:00 的記錄，使用當天備選記錄：{fallback_data.gregorian_hour}:00")
            return fallback_data
        
        # 如果完全沒有找到數據，記錄錯誤並返回 None
        # 停用動態生成功能，避免產生錯誤的農曆數據
        logger.error(f"未找到農曆數據且已停用動態生成：{birth_info.year}-{birth_info.month}-{birth_info.day} {birth_info.hour}:00")
        logger.error("請確保數據庫中有正確的農曆數據，或聯繫管理員導入完整數據")
        
        return None 