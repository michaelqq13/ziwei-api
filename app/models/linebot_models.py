"""
LINE Bot 資料庫模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.config.linebot_config import LineBotConfig

Base = declarative_base()

class LineBotUser(Base):
    """LINE Bot 用戶表"""
    __tablename__ = LineBotConfig.Tables.USERS
    
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255))
    profile_picture_url = Column(String(500))
    
    # 會員等級
    membership_level = Column(String(50), default=LineBotConfig.MembershipLevel.FREE)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    divination_history = relationship("DivinationHistory", back_populates="user")
    chart_binding = relationship("ChartBinding", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<LineBotUser(line_user_id='{self.line_user_id}', membership='{self.membership_level}')>"
    
    def is_admin(self):
        """檢查是否為管理員"""
        return self.membership_level == LineBotConfig.MembershipLevel.ADMIN
    
    def is_premium(self):
        """檢查是否為付費會員"""
        return self.membership_level in [LineBotConfig.MembershipLevel.PREMIUM, LineBotConfig.MembershipLevel.ADMIN]
    
    def can_use_divination(self, db_session):
        """檢查是否可以使用占卜功能"""
        if self.is_premium():
            return True
        
        # 免費會員檢查週限制
        week_start = datetime.utcnow() - timedelta(days=7)
        weekly_count = db_session.query(DivinationHistory).filter(
            DivinationHistory.user_id == self.id,
            DivinationHistory.created_at >= week_start
        ).count()
        
        return weekly_count < LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT

class DivinationHistory(Base):
    """占卜歷史記錄表"""
    __tablename__ = LineBotConfig.Tables.DIVINATION_HISTORY
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(f"{LineBotConfig.Tables.USERS}.id"), nullable=False)
    
    # 占卜參數
    gender = Column(String(10), nullable=False)  # M/F
    divination_time = Column(DateTime, nullable=False)
    taichi_palace = Column(String(50))  # 太極點命宮
    minute_dizhi = Column(String(10))   # 分鐘地支
    
    # 四化結果 (JSON格式存儲)
    sihua_results = Column(Text)  # 存儲四化結果的JSON
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("LineBotUser", back_populates="divination_history")
    
    def __repr__(self):
        return f"<DivinationHistory(user_id={self.user_id}, time='{self.divination_time}')>"

class ChartBinding(Base):
    """命盤綁定表"""
    __tablename__ = LineBotConfig.Tables.CHART_BINDINGS
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(f"{LineBotConfig.Tables.USERS}.id"), nullable=False)
    
    # 出生資料
    birth_year = Column(Integer, nullable=False)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    birth_hour = Column(Integer, nullable=False)
    birth_minute = Column(Integer, nullable=False)
    
    # 性別和曆法
    gender = Column(String(10), nullable=False)  # M/F
    calendar_type = Column(String(20), default="lunar")  # lunar/solar
    
    # 命盤資料 (JSON格式存儲完整命盤)
    chart_data = Column(Text)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("LineBotUser", back_populates="chart_binding")
    
    # 確保一個用戶只能有一個命盤綁定
    __table_args__ = (UniqueConstraint('user_id', name='_user_chart_binding_uc'),)
    
    def __repr__(self):
        return f"<ChartBinding(user_id={self.user_id}, birth={self.birth_year}/{self.birth_month}/{self.birth_day})>"

class UserSession(Base):
    """用戶對話狀態表"""
    __tablename__ = "linebot_user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # 對話狀態
    current_state = Column(String(100), default="idle")
    state_data = Column(Text)  # JSON格式存儲狀態相關資料
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserSession(line_user_id='{self.line_user_id}', state='{self.current_state}')>"

# 會話管理類 (記憶體版本，用於臨時狀態)
class MemoryUserSession:
    """記憶體版本的用戶會話，用於處理對話狀態"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.state = "idle"
        self.data = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_state(self, state: str, data: dict = None):
        """設定對話狀態"""
        self.state = state
        self.data = data or {}
        self.updated_at = datetime.utcnow()
    
    def get_data(self, key: str, default=None):
        """獲取狀態資料"""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value):
        """設定狀態資料"""
        self.data[key] = value
        self.updated_at = datetime.utcnow()
    
    def clear(self):
        """清除狀態"""
        self.state = "idle"
        self.data = {}
        self.updated_at = datetime.utcnow()

# 導出
__all__ = [
    "Base",
    "LineBotUser", 
    "DivinationHistory",
    "ChartBinding",
    "UserSession",
    "MemoryUserSession"
] 