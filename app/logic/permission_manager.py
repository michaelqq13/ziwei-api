"""
權限管理系統
處理用戶角色、會員等級和功能存取控制
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.linebot_models import LineBotUser, DivinationHistory
from app.config.linebot_config import LineBotConfig

logger = logging.getLogger(__name__)

class PermissionManager:
    """權限管理核心類"""
    
    def __init__(self):
        self.config = LineBotConfig()
    
    def get_or_create_user(self, db: Session, line_user_id: str, user_profile: Dict = None) -> LineBotUser:
        """
        獲取或創建用戶
        """
        # 查找現有用戶
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        
        if user:
            # 更新最後活動時間
            user.last_active_at = datetime.utcnow()
            if user_profile:
                user.display_name = user_profile.get("displayName", user.display_name)
                user.profile_picture_url = user_profile.get("pictureUrl", user.profile_picture_url)
            db.commit()
            return user
        
        # 創建新用戶
        new_user = LineBotUser(
            line_user_id=line_user_id,
            display_name=user_profile.get("displayName", "") if user_profile else "",
            profile_picture_url=user_profile.get("pictureUrl", "") if user_profile else "",
            membership_level=LineBotConfig.MembershipLevel.FREE
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    def authenticate_admin(self, secret_phrase: str, password: str) -> bool:
        """
        管理員身份驗證
        """
        return (secret_phrase == LineBotConfig.ADMIN_SECRET_PHRASE and 
                password == LineBotConfig.ADMIN_PASSWORD)
    
    def promote_to_admin(self, db: Session, line_user_id: str) -> bool:
        """
        提升用戶為管理員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user:
            user.membership_level = LineBotConfig.MembershipLevel.ADMIN
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    @staticmethod
    def set_admin_permissions(line_user_id: str, db: Session) -> bool:
        """
        設定管理員權限（靜態方法，用於管理腳本）
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user:
            user.membership_level = LineBotConfig.MembershipLevel.ADMIN
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def update_user_nickname(self, db: Session, line_user_id: str, nickname: str) -> bool:
        """
        更新用戶暱稱
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user:
            user.display_name = nickname.strip()
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def upgrade_to_premium(self, db: Session, line_user_id: str) -> bool:
        """
        升級為付費會員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user and user.membership_level != LineBotConfig.MembershipLevel.ADMIN:
            user.membership_level = LineBotConfig.MembershipLevel.PREMIUM
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def downgrade_to_free(self, db: Session, line_user_id: str) -> bool:
        """
        降級為免費會員
        """
        user = db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()
        if user and user.membership_level != LineBotConfig.MembershipLevel.ADMIN:
            user.membership_level = LineBotConfig.MembershipLevel.FREE
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def check_divination_permission(self, db: Session, user: LineBotUser) -> Dict[str, Any]:
        """
        檢查占卜功能權限
        """
        # 管理員和付費會員無限制
        if user.is_premium():
            return {
                "allowed": True,
                "reason": "unlimited",
                "remaining_count": -1  # -1 表示無限制
            }
        
        # 免費會員檢查週限制
        week_start = datetime.utcnow() - timedelta(days=7)
        weekly_count = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id,
            DivinationHistory.created_at >= week_start
        ).count()
        
        remaining = LineBotConfig.FREE_DIVINATION_WEEKLY_LIMIT - weekly_count
        
        if remaining > 0:
            return {
                "allowed": True,
                "reason": "within_limit",
                "remaining_count": remaining,
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
        # 占卜統計
        total_divinations = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id
        ).count()
        
        # 本週占卜次數
        week_start = datetime.utcnow() - timedelta(days=7)
        weekly_divinations = db.query(DivinationHistory).filter(
            DivinationHistory.user_id == user.id,
            DivinationHistory.created_at >= week_start
        ).count()
        
        # 權限檢查
        divination_permission = self.check_divination_permission(db, user)
        
        return {
            "user_info": {
                "line_user_id": user.line_user_id,
                "display_name": user.display_name,
                "membership_level": user.membership_level,
                "created_at": user.created_at.isoformat(),
                "last_active_at": user.last_active_at.isoformat()
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
                "level_name": self._get_level_name(user.membership_level)
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