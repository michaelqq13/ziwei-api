from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.db.database import Base
from enum import Enum

class UserRole(str, Enum):
    """用戶角色枚舉"""
    ADMIN = "admin"           # 系統管理員
    PREMIUM = "premium"       # 付費用戶
    FREE = "free"            # 免費用戶
    BANNED = "banned"        # 封禁用戶

class SubscriptionStatus(str, Enum):
    """訂閱狀態枚舉"""
    ACTIVE = "active"         # 有效訂閱
    EXPIRED = "expired"       # 訂閱過期
    CANCELLED = "cancelled"   # 已取消
    TRIAL = "trial"          # 試用期
    NONE = "none"            # 無訂閱

class UserPermissions(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # 用戶角色和等級
    role = Column(String(20), default=UserRole.FREE, nullable=False)
    subscription_status = Column(String(20), default=SubscriptionStatus.NONE, nullable=False)
    
    # 付費相關
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    subscription_price = Column(Float, default=0.0)
    
    # 權限標記
    can_access_premium_features = Column(Boolean, default=False)
    can_unlimited_divination = Column(Boolean, default=False)
    can_access_admin_panel = Column(Boolean, default=False)
    
    # 使用限制（防濫用）
    daily_api_calls = Column(Integer, default=0)
    daily_api_limit = Column(Integer, default=100)  # 免費用戶每日API調用限制
    last_api_call_date = Column(DateTime, nullable=True)
    
    # 設備和安全
    registered_device_count = Column(Integer, default=0)
    max_device_count = Column(Integer, default=1)  # 免費用戶1個設備，付費用戶2個設備
    last_login_ip = Column(String(45), nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @property
    def is_subscription_active(self) -> bool:
        """檢查訂閱是否有效"""
        if not self.subscription_end:
            return False
        from datetime import datetime, timezone, timedelta
        TAIPEI_TZ = timezone(timedelta(hours=8))
        return datetime.now(TAIPEI_TZ) < self.subscription_end
    
    def is_premium_active(self) -> bool:
        """檢查付費訂閱是否有效"""
        if self.role == UserRole.ADMIN:
            return True
        
        if self.subscription_status != SubscriptionStatus.ACTIVE:
            return False
            
        if self.subscription_end:
            from datetime import datetime
            return datetime.now() < self.subscription_end
            
        return False
    
    def can_use_premium_feature(self) -> bool:
        """檢查是否可以使用付費功能"""
        return (
            self.role == UserRole.ADMIN or 
            self.can_access_premium_features or 
            self.is_premium_active()
        )
    
    def is_admin(self) -> bool:
        """檢查是否為管理員"""
        return self.role == UserRole.ADMIN
    
    def get_daily_api_limit(self) -> int:
        """獲取每日API調用限制"""
        if self.role == UserRole.ADMIN:
            return 999999  # 管理員無限制
        elif self.is_premium_active():
            return 1000    # 付費用戶高限制
        else:
            return self.daily_api_limit  # 免費用戶限制 