"""
用戶綁定邏輯
處理 LINE 用戶與系統用戶的綁定關係
"""
import logging
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.linebot_models import LineBotUser
from app.models.pending_binding import PendingBinding
from app.db.database import get_db

logger = logging.getLogger(__name__)

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

class UserBindingManager:
    """用戶綁定管理器"""
    
    def __init__(self):
        self.binding_code_length = 6
        self.binding_expiry_minutes = 10
    
    def generate_binding_code(self, db: Session, line_user_id: str) -> Dict[str, Any]:
        """
        生成綁定碼
        
        Args:
            db: 數據庫會話
            line_user_id: LINE 用戶 ID
            
        Returns:
            Dict: 包含綁定碼和過期時間的字典
        """
        try:
            # 生成隨機綁定碼
            binding_code = self._generate_random_code()
            
            # 設置過期時間
            expires_at = get_current_taipei_time() + timedelta(minutes=self.binding_expiry_minutes)
            
            # 檢查是否已有待處理的綁定
            existing_binding = db.query(PendingBinding).filter(
                PendingBinding.line_user_id == line_user_id
            ).first()
            
            if existing_binding:
                # 更新現有綁定
                existing_binding.binding_code = binding_code
                existing_binding.expires_at = expires_at
                existing_binding.is_used = False
            else:
                # 創建新的綁定記錄
                new_binding = PendingBinding(
                    line_user_id=line_user_id,
                    binding_code=binding_code,
                    expires_at=expires_at
                )
                db.add(new_binding)
            
            db.commit()
            
            return {
                "success": True,
                "binding_code": binding_code,
                "expires_at": expires_at.isoformat(),
                "expires_in_minutes": self.binding_expiry_minutes
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"生成綁定碼失敗: {e}")
            return {
                "success": False,
                "error": "生成綁定碼失敗"
            }
    
    def verify_binding_code(self, db: Session, binding_code: str, target_user_id: str) -> Dict[str, Any]:
        """
        驗證綁定碼並執行綁定
        
        Args:
            db: 數據庫會話
            binding_code: 綁定碼
            target_user_id: 目標用戶 ID
            
        Returns:
            Dict: 綁定結果
        """
        try:
            # 查找有效的綁定記錄
            binding = db.query(PendingBinding).filter(
                PendingBinding.binding_code == binding_code,
                PendingBinding.is_used == False,
                PendingBinding.expires_at > get_current_taipei_time(),
            ).first()
            
            if not binding:
                return {
                    "success": False,
                    "error": "綁定碼無效或已過期"
                }
            
            # 查找 LINE 用戶
            line_user = db.query(LineBotUser).filter(
                LineBotUser.line_user_id == binding.line_user_id
            ).first()
            
            if not line_user:
                return {
                    "success": False,
                    "error": "找不到對應的 LINE 用戶"
                }
            
            # 執行綁定
            line_user.system_user_id = target_user_id
            binding.is_used = True
            binding.used_at = get_current_taipei_time()
            
            db.commit()
            
            return {
                "success": True,
                "message": "綁定成功",
                "line_user_id": line_user.line_user_id,
                "system_user_id": target_user_id
            }
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"綁定時發生完整性錯誤: {e}")
            return {
                "success": False,
                "error": "該用戶已被綁定"
            }
        except Exception as e:
            db.rollback()
            logger.error(f"驗證綁定碼失敗: {e}")
            return {
                "success": False,
                "error": "綁定過程發生錯誤"
            }
    
    def cleanup_expired_bindings(self, db: Session) -> int:
        """
        清理過期的綁定記錄
        
        Args:
            db: 數據庫會話
            
        Returns:
            int: 清理的記錄數量
        """
        try:
            expired_count = db.query(PendingBinding).filter(
                PendingBinding.expires_at < get_current_taipei_time()
            ).count()
            
            db.query(PendingBinding).filter(
                PendingBinding.expires_at < get_current_taipei_time()
            ).delete()
            
            db.commit()
            
            logger.info(f"清理了 {expired_count} 條過期綁定記錄")
            return expired_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"清理過期綁定記錄失敗: {e}")
            return 0 