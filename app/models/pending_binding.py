from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class PendingBinding(Base):
    __tablename__ = "pending_bindings"
    
    id = Column(Integer, primary_key=True, index=True)
    birth_data = Column(JSON, nullable=False)  # 存儲生辰資料
    created_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # 過期時間（1分鐘後）
    is_used = Column(String(1), default='N')  # 'Y' or 'N' 