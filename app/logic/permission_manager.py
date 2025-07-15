"""
權限管理系統
處理用戶角色、會員等級和功能存取控制
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from app.models.linebot_models import LineBotUser, DivinationHistory
from app.config.linebot_config import LineBotConfig

logger = logging.getLogger(__name__)

class PermissionManager:
    """
    權限管理器，負責用戶權限檢查和管理
    """
    def __init__(self):
        self.admin_secret = LineBotConfig.ADMIN_SECRET_PHRASE
        self.admin_password = LineBotConfig.ADMIN_PASSWORD

    def get_or_create_user(self, db: Session, line_user_id: str, user_profile: Dict = None) -> LineBotUser:
        """
        獲取或創建用戶
        """
        try:
            # 查找現有用戶
            user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
            
            if not user:
                # 創建新用戶
                user = LineBotUser(
                    line_user_id=line_user_id,
                    display_name=user_profile.get("displayName", "新用戶") if user_profile else "新用戶",
                    profile_picture_url=user_profile.get("pictureUrl") if user_profile else None,
                    membership_level=LineBotConfig.MembershipLevel.FREE
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"創建新用戶：{line_user_id}")
            else:
                # 更新最後活動時間
                user.last_active_at = datetime.utcnow()
                db.commit()
                
            return user
            
        except Exception as e:
            logger.error(f"獲取或創建用戶失敗：{e}")
            db.rollback()
            raise
    
    def authenticate_admin(self, secret_phrase: str, password: str) -> bool:
        """
        驗證管理員身份
        """
        return secret_phrase == self.admin_secret and password == self.admin_password
    
    def promote_to_admin(self, db: Session, line_user_id: str) -> bool:
        """
        提升用戶為管理員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user:
            user.membership_level = LineBotConfig.MembershipLevel.ADMIN
            user.updated_at = datetime.utcnow()
            db.commit()
            
            # 自動更新 Rich Menu
            self._update_user_rich_menu(line_user_id, is_admin=True)
            
            return True
        return False
    
    @staticmethod
    def set_admin_permissions(line_user_id: str, db: Session) -> bool:
        """
        設置管理員權限（靜態方法）
        """
        try:
            user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
            if user:
                user.membership_level = LineBotConfig.MembershipLevel.ADMIN
                user.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"✅ 管理員權限設置成功: {line_user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"設置管理員權限失敗: {e}")
            return False
    
    def update_user_nickname(self, db: Session, line_user_id: str, nickname: str) -> bool:
        """
        更新用戶暱稱
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user:
            user.display_name = nickname
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def upgrade_to_premium(self, db: Session, line_user_id: str) -> bool:
        """
        升級用戶為付費會員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user and user.membership_level == LineBotConfig.MembershipLevel.FREE:
            user.membership_level = LineBotConfig.MembershipLevel.PREMIUM
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def downgrade_to_free(self, db: Session, line_user_id: str) -> bool:
        """
        降級用戶為免費會員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user and user.membership_level == LineBotConfig.MembershipLevel.PREMIUM:
            user.membership_level = LineBotConfig.MembershipLevel.FREE
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def check_divination_permission(self, db: Session, user: LineBotUser) -> Dict[str, Any]:
        """
        檢查占卜權限
        """
        # 管理員和付費會員無限制
        if user.is_premium():
            return {
                "allowed": True,
                "reason": "unlimited",
                "remaining_count": -1,
                "weekly_count": 0,
                "limit": -1
            }
        
        # 免費會員檢查週限制
        today = datetime.utcnow()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        weekly_count = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id,  # 使用 user.id 而不是 line_user_id
            DivinationHistory.divination_time >= week_start  # 修正：使用 divination_time 而不是 created_at
        ).count()
        
        if weekly_count < LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT:
            return {
                "allowed": True,
                "reason": "within_limit",
                "remaining_count": LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT - weekly_count,
                "weekly_count": weekly_count,
                "limit": LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT
            }
        else:
            return {
                "allowed": False,
                "reason": "limit_exceeded",
                "remaining_count": 0,
                "weekly_count": weekly_count,
                "limit": LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT
            }
    
    def check_fortune_permission(self, db: Session, user: LineBotUser, fortune_type: str) -> Dict[str, Any]:
        """
        檢查運勢查詢權限（流年/流月/流日）
        """
        # 只有付費會員和管理員可以使用
        if user.is_premium():
            return {
                "allowed": True,
                "reason": "premium_member",
                "feature": fortune_type
            }
        else:
            return {
                "allowed": False,
                "reason": "premium_required",
                "feature": fortune_type,
                "current_level": user.membership_level
            }
    
    def check_chart_binding_permission(self, db: Session, user: LineBotUser) -> Dict[str, Any]:
        """
        檢查命盤綁定權限
        """
        # 所有會員都可以綁定命盤（基本功能）
        return {
            "allowed": True,
            "reason": "basic_feature",
            "membership_level": user.membership_level
        }
    
    def check_admin_access(self, line_user_id: str, db: Session) -> bool:
        """
        檢查用戶是否為管理員
        """
        try:
            user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
            if user:
                return user.is_admin()
            return False
        except Exception as e:
            logger.error(f"檢查管理員權限失敗: {e}")
            return False
    
    def get_user_stats(self, db: Session, user: LineBotUser) -> Dict[str, Any]:
        """
        獲取用戶統計資訊
        """
        from datetime import datetime, timedelta
        
        # 占卜統計 - 使用 DivinationHistory 模型和正確的字段
        total_divinations = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id  # 使用 user.id 而不是 line_user_id
        ).count()
        
        # 本週占卜次數
        today = datetime.utcnow()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        weekly_divinations = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id,  # 使用 user.id 而不是 line_user_id
            DivinationHistory.divination_time >= week_start  # 修正：使用 divination_time 而不是 created_at
        ).count()
        
        # 權限檢查
        divination_permission = self.check_divination_permission(db, user)
        
        return {
            "user_info": {
                "line_user_id": user.line_user_id,
                "display_name": user.display_name,
                "membership_level": user.membership_level,
                "is_admin": user.is_admin(),
                "is_premium": user.is_premium(),
                "is_active": user.is_active,  # 添加活躍狀態
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None
            },
            "statistics": {
                "total_divinations": total_divinations,
                "weekly_divinations": weekly_divinations,
                "weekly_limit": LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT if not user.is_premium() else -1
            },
            "permissions": {
                "divination": divination_permission,
                "yearly_fortune": self.check_fortune_permission(db, user, "yearly"),
                "monthly_fortune": self.check_fortune_permission(db, user, "monthly"),
                "daily_fortune": self.check_fortune_permission(db, user, "daily"),
                "chart_binding": self.check_chart_binding_permission(db, user)
            },
            "membership_info": {
                "is_admin": user.is_admin(),
                "is_premium": user.is_premium(),
                "level_name": self._get_level_name(user.membership_level),
                "expires_at": None  # 添加會員到期日（目前為永久）
            },
            "divination_stats": {
                "total_divinations": total_divinations,
                "last_divination_time": self._get_last_divination_time(db, user)
            }
        }
    
    def _get_level_name(self, level: str) -> str:
        """
        獲取會員等級中文名稱
        """
        level_names = {
            LineBotConfig.MembershipLevel.FREE: "免費會員",
            LineBotConfig.MembershipLevel.PREMIUM: "付費會員",
            LineBotConfig.MembershipLevel.ADMIN: "管理員"
        }
        return level_names.get(level, "未知等級")
    
    def get_feature_access_summary(self, user: LineBotUser) -> Dict[str, bool]:
        """
        獲取功能存取權限摘要
        """
        return {
            "divination": True,  # 所有會員都可以占卜（但有次數限制）
            "yearly_fortune": user.is_premium(),
            "monthly_fortune": user.is_premium(),
            "daily_fortune": user.is_premium(),
            "chart_binding": True,  # 所有會員都可以綁定命盤
            "unlimited_divination": user.is_premium()
        }
    
    def format_permission_message(self, permission_result: Dict[str, Any], feature_name: str) -> str:
        """
        格式化權限檢查結果為用戶友好的訊息
        """
        if permission_result["allowed"]:
            if feature_name == "divination":
                if permission_result["reason"] == "unlimited":
                    return "✅ 您可以無限次使用占卜功能"
                else:
                    remaining = permission_result["remaining_count"]
                    return f"✅ 您還可以占卜 {remaining} 次（本週）"
            else:
                return f"✅ 您可以使用{feature_name}功能"
        else:
            if permission_result["reason"] == "limit_exceeded":
                return f"❌ 本週占卜次數已用完\n\n免費會員每週限制 {permission_result['limit']} 次\n升級付費會員可無限使用"
            elif permission_result["reason"] == "premium_required":
                return f"❌ {feature_name}功能需要付費會員\n\n目前等級：{self._get_level_name(permission_result['current_level'])}\n請聯繫管理員升級會員"
            else:
                return f"❌ 無法使用{feature_name}功能"
    
    def downgrade_from_admin(self, db: Session, line_user_id: str) -> bool:
        """
        從管理員降級為付費會員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user and user.membership_level == LineBotConfig.MembershipLevel.ADMIN:
            user.membership_level = LineBotConfig.MembershipLevel.PREMIUM
            user.updated_at = datetime.utcnow()
            db.commit()
            
            # 自動更新 Rich Menu
            self._update_user_rich_menu(line_user_id, is_admin=False)
            
            return True
        return False
    
    def _update_user_rich_menu(self, line_user_id: str, is_admin: bool) -> None:
        """
        更新用戶的 Rich Menu（私有方法）
        """
        try:
            from app.utils.rich_menu_manager import update_user_rich_menu
            success = update_user_rich_menu(line_user_id, is_admin)
            if success:
                logger.info(f"成功更新用戶 {line_user_id} 的 Rich Menu (管理員: {is_admin})")
            else:
                logger.warning(f"更新用戶 {line_user_id} Rich Menu 失敗")
        except Exception as e:
            logger.error(f"更新用戶 {line_user_id} Rich Menu 時發生錯誤: {e}")

    def _get_last_divination_time(self, db: Session, user: LineBotUser) -> Optional[str]:
        """獲取最後一次占卜時間"""
        try:
            last_record = db.query(DivinationHistory).filter(
                DivinationHistory.user_id == user.id
            ).order_by(DivinationHistory.divination_time.desc()).first()
            
            if last_record:
                return last_record.divination_time.isoformat()
            return None
        except Exception as e:
            logger.error(f"獲取最後占卜時間失敗: {e}")
            return None

# 全局實例
permission_manager = PermissionManager()

def get_user_with_permissions(db: Session, line_user_id: str, user_profile: Dict = None) -> tuple[LineBotUser, Dict]:
    """
    獲取用戶及其權限資訊的便捷函數
    """
    user = permission_manager.get_or_create_user(db, line_user_id, user_profile)
    stats = permission_manager.get_user_stats(db, user)
    return user, stats

# 導出
__all__ = [
    "PermissionManager", 
    "permission_manager", 
    "get_user_with_permissions"
] 