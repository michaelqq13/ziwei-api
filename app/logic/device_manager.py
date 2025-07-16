"""
設備管理邏輯
管理用戶設備限制和設備清理
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.user_devices import UserDevice
from app.models.linebot_models import LineBotUser

logger = logging.getLogger(__name__)

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

class DeviceManager:
    """設備管理器"""
    
    def __init__(self):
        self.max_devices_per_user = 3  # 每個用戶最多3台設備
        self.device_inactive_days = 7  # 設備非活躍天數閾值
    
    def get_user_devices(self, user_id: str, db: Session) -> List[UserDevice]:
        """獲取用戶的所有設備"""
        try:
            devices = db.query(UserDevice).filter(
                UserDevice.user_id == user_id
            ).order_by(UserDevice.last_activity.desc()).all()
            
            return devices
            
        except Exception as e:
            logger.error(f"獲取用戶設備失敗 {user_id}: {e}")
            return []
    
    def get_active_devices(self, user_id: str, hours: int = 24, db: Session = None) -> List[UserDevice]:
        """獲取指定時間內活躍的設備"""
        try:
            threshold = get_current_taipei_time() - timedelta(hours=hours)
            
            devices = db.query(UserDevice).filter(
                and_(
                    UserDevice.user_id == user_id,
                    UserDevice.last_seen > threshold
                )
            ).order_by(UserDevice.last_activity.desc()).all()
            
            return devices
            
        except Exception as e:
            logger.error(f"獲取活躍設備失敗 {user_id}: {e}")
            return []
    
    def register_device(self, user_id: str, device_info: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """註冊新設備"""
        try:
            device_id = device_info.get("device_id")
            device_name = device_info.get("device_name", "Unknown Device")
            device_type = device_info.get("device_type", "mobile")
            
            # 檢查設備是否已存在
            existing_device = db.query(UserDevice).filter(
                and_(
                    UserDevice.user_id == user_id,
                    UserDevice.device_id == device_id
                )
            ).first()
            
            current_time = get_current_taipei_time()
            
            if existing_device:
                # 更新現有設備的活動時間
                existing_device.last_seen = current_time
                existing_device.last_activity = current_time
                existing_device.device_name = device_name  # 更新設備名稱
                device = existing_device
            else:
                # 檢查用戶設備數量限制
                user_device_count = db.query(UserDevice).filter(
                    UserDevice.user_id == user_id
                ).count()
                
                if user_device_count >= self.max_devices_per_user:
                    # 移除最舊的非活躍設備
                    oldest_device = db.query(UserDevice).filter(
                        UserDevice.user_id == user_id
                    ).order_by(UserDevice.last_activity.asc()).first()
                    
                    if oldest_device and oldest_device.last_activity < get_current_taipei_time() - timedelta(days=7):
                        db.delete(oldest_device)
                        logger.info(f"移除用戶 {user_id} 的舊設備: {oldest_device.device_id}")
                    else:
                        return {
                            "success": False,
                            "error": "設備數量已達上限",
                            "max_devices": self.max_devices_per_user
                        }
                
                # 創建新設備記錄
                device = UserDevice(
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    device_type=device_type,
                    first_seen=current_time,
                    last_seen=current_time,
                    last_activity=current_time
                )
                db.add(device)
            
            db.commit()
            
            return {
                "success": True,
                "device_id": device_id,
                "device_name": device_name,
                "is_new": existing_device is None
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"註冊設備失敗 {user_id}: {e}")
            return {
                "success": False,
                "error": "註冊設備失敗"
            } 