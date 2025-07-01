from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class UserBirthInfo(Base):
    __tablename__ = "user_birth_info"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, default=30)
    gender = Column(String(1), nullable=False)  # 'M' or 'F'
    longitude = Column(Float, default=121.5654)  # 台北經度
    latitude = Column(Float, default=25.0330)   # 台北緯度
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 