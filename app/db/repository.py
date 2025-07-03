from typing import Optional
from sqlalchemy.orm import Session
from app.models.calendar import CalendarData
from app.models.birth_info import BirthInfo
from app.utils.lunar_data_generator import get_or_create_lunar_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CalendarRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_calendar_data(self, birth_info: BirthInfo) -> Optional[CalendarData]:
        # 對於觸機占卜或排盤，我們只需要當天的天干地支資料，
        # 這些資料在一天之內是不會變的。
        # 因此，我們只用年、月、日來查詢，以確保能找到資料，
        # 避免因精確到小時而找不到記錄的問題。
        
        # 首先嘗試從現有數據中獲取
        existing_data = self.db_session.query(CalendarData).filter(
            CalendarData.gregorian_year == birth_info.year,
            CalendarData.gregorian_month == birth_info.month,
            CalendarData.gregorian_day == birth_info.day
        ).first()
        
        if existing_data:
            logger.info(f"找到現有農曆數據：{birth_info.year}-{birth_info.month}-{birth_info.day}")
            return existing_data
        
        # 如果沒有找到現有數據，嘗試動態生成
        logger.info(f"未找到農曆數據，嘗試動態生成：{birth_info.year}-{birth_info.month}-{birth_info.day}")
        
        try:
            # 創建目標日期時間對象
            target_date = datetime(birth_info.year, birth_info.month, birth_info.day, birth_info.hour or 12)
            
            # 使用動態生成器獲取或創建農曆數據
            generated_data = get_or_create_lunar_data(self.db_session, target_date)
            
            if generated_data:
                logger.info(f"成功生成農曆數據：{birth_info.year}-{birth_info.month}-{birth_info.day}")
                return generated_data
            else:
                logger.error(f"動態生成農曆數據失敗：{birth_info.year}-{birth_info.month}-{birth_info.day}")
                return None
                
        except Exception as e:
            logger.error(f"動態生成農曆數據時發生錯誤：{e}")
            return None 