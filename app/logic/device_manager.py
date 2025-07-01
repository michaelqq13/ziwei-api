from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import hashlib
import logging

from app.models.user_devices import UserDevice
from app.models.user_permissions import UserPermissions, UserRole

logger = logging.getLogger(__name__)

class DeviceManager:
    """智能設備管理器"""
    
    @staticmethod
    def generate_device_fingerprint(user_agent: str, ip_address: str, additional_info: str = "") -> str:
        """生成設備指紋"""
        # 組合多個資訊生成唯一指紋
        raw_data = f"{user_agent}|{ip_address}|{additional_info}"
        return hashlib.sha256(raw_data.encode()).hexdigest()
    
    @staticmethod
    def check_device_access(
        user_id: str, 
        device_fingerprint: str, 
        user_agent: str = None,
        ip_address: str = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """檢查設備訪問權限（智能策略）"""
        try:
            from app.logic.permission_manager import PermissionManager
            
            # 獲取用戶權限
            permissions = PermissionManager.get_or_create_user_permissions(user_id, db)
            
            # 管理員無限制
            if permissions.is_admin():
                DeviceManager._update_or_create_device(
                    user_id, device_fingerprint, user_agent, ip_address, db
                )
                return {
                    "allowed": True,
                    "reason": "admin_unlimited",
                    "message": "管理員權限，無設備限制"
                }
            
            # 查找現有設備
            existing_device = db.query(UserDevice).filter(
                UserDevice.user_id == user_id,
                UserDevice.device_fingerprint == device_fingerprint
            ).first()
            
            if existing_device:
                # 已知設備，更新活動時間
                existing_device.update_activity()
                db.commit()
                return {
                    "allowed": True,
                    "reason": "known_device",
                    "message": f"歡迎回來！{existing_device.get_device_info()}"
                }
            
            # 新設備，檢查限制
            return DeviceManager._check_new_device_access(user_id, device_fingerprint, user_agent, ip_address, permissions, db)
            
        except Exception as e:
            logger.error(f"檢查設備訪問權限失敗 {user_id}: {e}")
            return {
                "allowed": False,
                "reason": "error",
                "message": "系統錯誤，請稍後再試"
            }
    
    @staticmethod
    def _check_new_device_access(
        user_id: str,
        device_fingerprint: str,
        user_agent: str,
        ip_address: str,
        permissions: UserPermissions,
        db: Session
    ) -> Dict[str, Any]:
        """檢查新設備訪問權限"""
        
        # 獲取用戶所有活躍設備（24小時內有活動）
        active_devices = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.is_active == True,
            UserDevice.last_activity > datetime.now() - timedelta(hours=24)
        ).all()
        
        active_count = len(active_devices)
        max_devices = permissions.max_device_count
        
        # 檢查設備數量限制
        if active_count >= max_devices:
            # 免費用戶：嚴格限制
            if permissions.role == UserRole.FREE:
                return {
                    "allowed": False,
                    "reason": "device_limit_exceeded",
                    "message": f"免費用戶只能使用 {max_devices} 個設備。如需更多設備，請升級至付費版本。",
                    "active_devices": [d.get_device_info() for d in active_devices],
                    "suggestion": "upgrade_premium"
                }
            
            # 付費用戶：智能替換策略
            elif permissions.role == UserRole.PREMIUM:
                # 找到最久未使用的設備
                oldest_device = min(active_devices, key=lambda d: d.last_activity)
                
                # 如果最久未使用的設備超過7天沒活動，自動替換
                if oldest_device.last_activity < datetime.now() - timedelta(days=7):
                    oldest_device.is_active = False
                    db.commit()
                    
                    DeviceManager._update_or_create_device(
                        user_id, device_fingerprint, user_agent, ip_address, db
                    )
                    
                    return {
                        "allowed": True,
                        "reason": "device_replaced",
                        "message": f"已自動替換長期未使用的設備：{oldest_device.get_device_info()}"
                    }
                else:
                    return {
                        "allowed": False,
                        "reason": "premium_device_limit",
                        "message": f"付費用戶最多可使用 {max_devices} 個設備。",
                        "active_devices": [d.get_device_info() for d in active_devices],
                        "suggestion": "manage_devices"
                    }
        
        # 設備數量未超限，允許新設備
        DeviceManager._update_or_create_device(
            user_id, device_fingerprint, user_agent, ip_address, db
        )
        
        return {
            "allowed": True,
            "reason": "new_device_allowed",
            "message": "新設備已註冊"
        }
    
    @staticmethod
    def _update_or_create_device(
        user_id: str,
        device_fingerprint: str,
        user_agent: str,
        ip_address: str,
        db: Session
    ):
        """更新或創建設備記錄"""
        device = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.device_fingerprint == device_fingerprint
        ).first()
        
        if device:
            device.update_activity()
            device.user_agent = user_agent
            device.ip_address = ip_address
        else:
            device = UserDevice(
                user_id=user_id,
                device_fingerprint=device_fingerprint,
                user_agent=user_agent,
                ip_address=ip_address
            )
            db.add(device)
        
        db.commit()
        return device
    
    @staticmethod
    def get_user_devices(user_id: str, db: Session, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """獲取用戶設備列表"""
        try:
            query = db.query(UserDevice).filter(UserDevice.user_id == user_id)
            
            if not include_inactive:
                query = query.filter(UserDevice.is_active == True)
            
            devices = query.order_by(desc(UserDevice.last_activity)).all()
            
            return [
                {
                    "id": device.id,
                    "device_info": device.get_device_info(),
                    "device_fingerprint": device.device_fingerprint[:12] + "...",
                    "first_seen": device.first_seen,
                    "last_seen": device.last_seen,
                    "last_activity": device.last_activity,
                    "is_active": device.is_active,
                    "is_recently_active": device.is_recently_active(),
                    "total_sessions": device.total_sessions,
                    "ip_address": device.ip_address
                }
                for device in devices
            ]
            
        except Exception as e:
            logger.error(f"獲取用戶設備列表失敗 {user_id}: {e}")
            return []
    
    @staticmethod
    def deactivate_device(user_id: str, device_id: int, db: Session) -> bool:
        """停用指定設備"""
        try:
            device = db.query(UserDevice).filter(
                UserDevice.user_id == user_id,
                UserDevice.id == device_id
            ).first()
            
            if device:
                device.is_active = False
                db.commit()
                logger.info(f"用戶 {user_id} 停用設備 {device_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"停用設備失敗 {user_id}, {device_id}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_device_usage_stats(user_id: str, db: Session) -> Dict[str, Any]:
        """獲取設備使用統計"""
        try:
            from app.logic.permission_manager import PermissionManager
            
            permissions = PermissionManager.get_or_create_user_permissions(user_id, db)
            devices = DeviceManager.get_user_devices(user_id, db, include_inactive=True)
            
            active_devices = [d for d in devices if d["is_active"]]
            recently_active = [d for d in active_devices if d["is_recently_active"]]
            
            return {
                "total_devices": len(devices),
                "active_devices": len(active_devices),
                "recently_active_devices": len(recently_active),
                "max_allowed_devices": permissions.max_device_count,
                "usage_percentage": (len(recently_active) / permissions.max_device_count) * 100 if permissions.max_device_count > 0 else 0,
                "devices": devices
            }
            
        except Exception as e:
            logger.error(f"獲取設備統計失敗 {user_id}: {e}")
            return {"error": str(e)} 