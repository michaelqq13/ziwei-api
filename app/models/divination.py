from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, Float, Text
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

class TimeDivinationHistory(Base):
    """指定時間占卜歷史記錄"""
    __tablename__ = "time_divination_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 關聯到 LineBotUser.id
    target_time = Column(DateTime, nullable=False, index=True)  # 目標占卜時間
    current_time = Column(DateTime, nullable=False, default=func.now())  # 實際占卜時間
    gender = Column(String(1), nullable=False)  # 'M' or 'F'
    purpose = Column(String(200), nullable=True)  # 占卜目的
    taichi_palace = Column(String(10), nullable=False)  # 太極宮位
    minute_dizhi = Column(String(2), nullable=False)  # 分鐘地支
    sihua_results = Column(Text, nullable=True)  # 四化結果 JSON
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TimeDivinationHistory(user_id={self.user_id}, target_time={self.target_time})>" 