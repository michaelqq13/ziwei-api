from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, Float
from sqlalchemy.sql import func
from app.db.database import Base

class DivinationRecord(Base):
    __tablename__ = "user_divination_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    divination_time = Column(DateTime, nullable=False)
    week_start_date = Column(Date, nullable=False, index=True)
    gender = Column(String(1), nullable=False)  # 'M' or 'F'
    longitude = Column(Float, default=121.5654)
    latitude = Column(Float, default=25.0330)
    divination_result = Column(JSON)
    created_at = Column(DateTime, default=func.now()) 