from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime, timedelta

class UserDevice(Base):
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # 設備識別資訊
    device_fingerprint = Column(String(255), nullable=False)  # 設備指紋
    device_name = Column(String(100), nullable=True)          # 設備名稱（可選）
    user_agent = Column(String(500), nullable=True)           # 瀏覽器資訊
    ip_address = Column(String(45), nullable=True)            # IP地址
    
    # 使用狀態
    is_active = Column(Boolean, default=True)                 # 是否活躍
    first_seen = Column(DateTime, default=func.now())         # 首次使用時間
    last_seen = Column(DateTime, default=func.now())          # 最後使用時間
    last_activity = Column(DateTime, default=func.now())      # 最後活動時間
    
    # 使用統計
    total_sessions = Column(Integer, default=1)               # 總使用次數
    total_api_calls = Column(Integer, default=0)              # 總API調用次數
    
    def is_recently_active(self, hours: int = 24) -> bool:
        """檢查設備是否在指定時間內活躍"""
        from datetime import datetime, timezone, timedelta
        TAIPEI_TZ = timezone(timedelta(hours=8))
        threshold = datetime.now(TAIPEI_TZ) - timedelta(hours=hours)
        return self.last_seen > threshold
    
    def update_activity(self):
        """更新設備活動時間"""
        from datetime import datetime, timezone, timedelta
        TAIPEI_TZ = timezone(timedelta(hours=8))
        self.last_seen = datetime.now(TAIPEI_TZ)
        self.last_activity = datetime.now(TAIPEI_TZ)
        self.total_sessions += 1
    
    def get_device_info(self) -> str:
        """獲取設備資訊摘要"""
        if self.device_name:
            return self.device_name
        elif self.user_agent:
            # 簡化的瀏覽器識別
            if 'Mobile' in self.user_agent:
                return "手機設備"
            elif 'iPad' in self.user_agent:
                return "iPad"
            elif 'Chrome' in self.user_agent:
                return "Chrome瀏覽器"
            elif 'Safari' in self.user_agent:
                return "Safari瀏覽器"
            else:
                return "未知設備"
        else:
            return f"設備-{self.device_fingerprint[:8]}" 