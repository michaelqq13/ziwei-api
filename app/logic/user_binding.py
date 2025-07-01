from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user_preferences import UserPreferences
from app.models.user_birth_info import UserBirthInfo
import logging

logger = logging.getLogger(__name__)

class UserBindingManager:
    """用戶綁定狀態管理器"""
    
    @staticmethod
    def is_user_bound(user_id: str, db: Session) -> bool:
        """檢查用戶是否已綁定命盤"""
        try:
            # 檢查是否有用戶偏好記錄且有綁定的生辰資料
            user_pref = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if not user_pref:
                return False
                
            # 檢查是否有對應的生辰資料記錄
            birth_info = db.query(UserBirthInfo).filter(
                UserBirthInfo.user_id == user_id
            ).first()
            
            return birth_info is not None
            
        except Exception as e:
            logger.error(f"檢查用戶綁定狀態失敗 {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_birth_info(user_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """獲取用戶的生辰資料"""
        try:
            birth_info = db.query(UserBirthInfo).filter(
                UserBirthInfo.user_id == user_id
            ).first()
            
            if birth_info:
                return {
                    "year": birth_info.year,
                    "month": birth_info.month,
                    "day": birth_info.day,
                    "hour": birth_info.hour,
                    "minute": birth_info.minute,
                    "gender": birth_info.gender,
                    "longitude": birth_info.longitude,
                    "latitude": birth_info.latitude,
                    "created_at": birth_info.created_at
                }
            return None
            
        except Exception as e:
            logger.error(f"獲取用戶生辰資料失敗 {user_id}: {e}")
            return None
    
    @staticmethod
    def bind_user_birth_info(user_id: str, birth_data: Dict[str, Any], db: Session) -> bool:
        """綁定用戶生辰資料"""
        try:
            # 檢查是否已存在記錄
            existing_birth = db.query(UserBirthInfo).filter(
                UserBirthInfo.user_id == user_id
            ).first()
            
            if existing_birth:
                # 更新現有記錄
                existing_birth.year = birth_data.get("year")
                existing_birth.month = birth_data.get("month")
                existing_birth.day = birth_data.get("day")
                existing_birth.hour = birth_data.get("hour")
                existing_birth.minute = birth_data.get("minute", 30)
                existing_birth.gender = birth_data.get("gender")
                existing_birth.longitude = birth_data.get("longitude", 121.5654)
                existing_birth.latitude = birth_data.get("latitude", 25.0330)
            else:
                # 創建新記錄
                new_birth = UserBirthInfo(
                    user_id=user_id,
                    year=birth_data.get("year"),
                    month=birth_data.get("month"),
                    day=birth_data.get("day"),
                    hour=birth_data.get("hour"),
                    minute=birth_data.get("minute", 30),
                    gender=birth_data.get("gender"),
                    longitude=birth_data.get("longitude", 121.5654),
                    latitude=birth_data.get("latitude", 25.0330)
                )
                db.add(new_birth)
            
            # 確保用戶偏好記錄存在
            user_pref = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if not user_pref:
                new_pref = UserPreferences(
                    user_id=user_id,
                    divination_gender=birth_data.get("gender")
                )
                db.add(new_pref)
            else:
                # 同步占卜性別偏好
                if not user_pref.divination_gender:
                    user_pref.divination_gender = birth_data.get("gender")
            
            db.commit()
            logger.info(f"用戶 {user_id} 綁定成功")
            return True
            
        except Exception as e:
            logger.error(f"綁定用戶生辰資料失敗 {user_id}: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def create_pending_binding(birth_data: Dict[str, Any], db: Session) -> bool:
        """創建待綁定記錄（時間窗口綁定）"""
        try:
            from app.models.pending_binding import PendingBinding
            from datetime import datetime, timedelta
            
            # 創建待綁定記錄，1分鐘後過期
            pending_binding = PendingBinding(
                birth_data=birth_data,
                expires_at=datetime.now() + timedelta(minutes=1)
            )
            
            db.add(pending_binding)
            db.commit()
            
            logger.info("待綁定記錄創建成功")
            return True
            
        except Exception as e:
            logger.error(f"創建待綁定記錄失敗: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def process_binding_request(user_id: str, db: Session) -> Dict[str, Any]:
        """處理綁定請求（用戶輸入「綁定」時）"""
        try:
            from app.models.pending_binding import PendingBinding
            from datetime import datetime
            
            # 檢查用戶是否已經綁定過
            if UserBindingManager.is_user_bound(user_id, db):
                return {
                    "success": False,
                    "reason": "already_bound",
                    "message": "您的帳號已綁定命盤，如需修改請聯繫客服"
                }
            
            # 查找1分鐘內未使用的待綁定記錄
            pending_binding = db.query(PendingBinding).filter(
                PendingBinding.expires_at > datetime.now(),
                PendingBinding.is_used == 'N'
            ).order_by(PendingBinding.created_at.desc()).first()
            
            if not pending_binding:
                return {
                    "success": False,
                    "reason": "no_pending",
                    "message": "找不到待綁定的命盤資料"
                }
            
            # 執行綁定
            success = UserBindingManager.bind_user_birth_info(
                user_id, 
                pending_binding.birth_data, 
                db
            )
            
            if success:
                # 標記為已使用
                pending_binding.is_used = 'Y'
                db.commit()
                logger.info(f"用戶 {user_id} 時間窗口綁定成功")
                return {
                    "success": True,
                    "reason": "success",
                    "message": "綁定成功"
                }
            else:
                return {
                    "success": False,
                    "reason": "bind_failed",
                    "message": "綁定過程發生錯誤"
                }
            
        except Exception as e:
            logger.error(f"處理綁定請求失敗 {user_id}: {e}")
            db.rollback()
            return {
                "success": False,
                "reason": "error",
                "message": "系統錯誤"
            }
    
    @staticmethod
    def cleanup_expired_bindings(db: Session):
        """清理過期的待綁定記錄"""
        try:
            from app.models.pending_binding import PendingBinding
            from datetime import datetime
            
            # 刪除過期的記錄
            expired_count = db.query(PendingBinding).filter(
                PendingBinding.expires_at < datetime.now()
            ).delete()
            
            db.commit()
            
            if expired_count > 0:
                logger.info(f"清理了 {expired_count} 條過期的待綁定記錄")
            
        except Exception as e:
            logger.error(f"清理過期綁定記錄失敗: {e}")
            db.rollback() 