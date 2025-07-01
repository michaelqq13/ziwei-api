from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CalendarData(Base):
    __tablename__ = "calendar_data"

    id = Column(Integer, primary_key=True, index=True)
    gregorian_datetime = Column(DateTime, nullable=False)
    gregorian_year = Column(Integer, nullable=False)
    gregorian_month = Column(Integer, nullable=False)
    gregorian_day = Column(Integer, nullable=False)
    gregorian_hour = Column(Integer, nullable=False)
    lunar_year_in_chinese = Column(String(50), nullable=False)
    lunar_month_in_chinese = Column(String(50), nullable=False)
    lunar_day_in_chinese = Column(String(50), nullable=False)
    is_leap_month_in_chinese = Column(Boolean, nullable=False)
    year_gan_zhi = Column(String(50), nullable=False)
    month_gan_zhi = Column(String(50), nullable=False)
    day_gan_zhi = Column(String(50), nullable=False)
    hour_gan_zhi = Column(String(50), nullable=False)
    minute_gan_zhi = Column(String(50), nullable=True)
    solar_term_today = Column(String(50), nullable=True)
    solar_term_in_hour = Column(String(50), nullable=True) 