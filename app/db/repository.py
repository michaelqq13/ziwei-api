from typing import Optional
from sqlalchemy.orm import Session
from app.models.calendar import CalendarData
from app.models.birth_info import BirthInfo

class CalendarRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_calendar_data(self, birth_info: BirthInfo) -> Optional[CalendarData]:
        # 對於觸機占卜或排盤，我們只需要當天的天干地支資料，
        # 這些資料在一天之內是不會變的。
        # 因此，我們只用年、月、日來查詢，以確保能找到資料，
        # 避免因精確到小時而找不到記錄的問題。
        return self.db_session.query(CalendarData).filter(
            CalendarData.gregorian_year == birth_info.year,
            CalendarData.gregorian_month == birth_info.month,
            CalendarData.gregorian_day == birth_info.day
        ).first() 