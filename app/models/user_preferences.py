from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    divination_gender = Column(String(1))  # 'M' or 'F'
    location_longitude = Column(Float, default=121.5654)  # 台北經度
    location_latitude = Column(Float, default=25.0330)   # 台北緯度
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 