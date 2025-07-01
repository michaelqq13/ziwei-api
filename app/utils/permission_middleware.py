from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional, Callable, Any
from functools import wraps
import logging

from app.db.database import get_db
from app.logic.permission_manager import PermissionManager
from app.logic.device_manager import DeviceManager

logger = logging.getLogger(__name__)

class PermissionLevel:
    """權限等級常量"""
    FREE = "free"           # 免費功能
    PREMIUM = "premium"     # 付費功能
    ADMIN = "admin"         # 管理員功能

def extract_user_id_from_request(request: Request) -> Optional[str]:
    """從請求中提取用戶ID"""
    # 嘗試從header中獲取
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    
    # 嘗試從query參數中獲取
    user_id = request.query_params.get("user_id")
    if user_id:
        return user_id
    
    # 嘗試從路徑參數中獲取（需要在路由中定義）
    path_params = request.path_params
    if "user_id" in path_params:
        return path_params["user_id"]
    
    return None

# 簡化的權限檢查依賴注入函數
def get_user_permission_check(level: str = PermissionLevel.FREE, check_device: bool = True):
    """權限檢查依賴注入函數"""
    def permission_dependency(
        request: Request,
        db: Session = Depends(get_db)
    ) -> str:
        # 提取用戶ID
        user_id = extract_user_id_from_request(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="用戶ID未提供")
        
        try:
            # 檢查API調用頻率限制
            rate_limit_result = PermissionManager.check_api_rate_limit(user_id, db)
            if not rate_limit_result["can_call"]:
                raise HTTPException(
                    status_code=429, 
                    detail={
                        "error": "API調用次數已達每日限制",
                        "daily_limit": rate_limit_result["daily_limit"],
                        "remaining_calls": rate_limit_result["remaining_calls"]
                    }
                )
            
            # 檢查設備限制
            if check_device:
                device_fingerprint = request.headers.get("X-Device-Fingerprint")
                if device_fingerprint:
                    device_check = DeviceManager.check_device_permission(user_id, device_fingerprint, db)
                    if not device_check["can_access"]:
                        raise HTTPException(
                            status_code=403,
                            detail={
                                "error": "設備數量超過限制",
                                "message": device_check["message"],
                                "registered_devices": device_check["registered_devices"],
                                "max_devices": device_check["max_devices"]
                            }
                        )
            
            # 檢查功能權限
            if level == PermissionLevel.ADMIN:
                if not PermissionManager.check_admin_access(user_id, db):
                    raise HTTPException(status_code=403, detail="需要管理員權限")
                    
            elif level == PermissionLevel.PREMIUM:
                if not PermissionManager.check_premium_access(user_id, db):
                    raise HTTPException(
                        status_code=402, 
                        detail={
                            "error": "需要付費會員權限",
                            "message": "此功能僅限付費會員使用",
                            "upgrade_url": "/upgrade"
                        }
                    )
            
            return user_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"權限檢查失敗 {user_id}: {e}")
            raise HTTPException(status_code=500, detail="權限檢查失敗")
    
    return permission_dependency

# 便捷的權限依賴注入
RequireFree = Depends(get_user_permission_check(PermissionLevel.FREE))
RequirePremium = Depends(get_user_permission_check(PermissionLevel.PREMIUM))
RequireAdmin = Depends(get_user_permission_check(PermissionLevel.ADMIN))

# 便捷的權限檢查函數
def check_user_permissions(user_id: str, db: Session) -> dict:
    """檢查用戶完整權限狀態"""
    try:
        permissions = PermissionManager.get_or_create_user_permissions(user_id, db)
        
        return {
            "user_id": user_id,
            "is_premium": permissions.can_use_premium_feature(),
            "is_admin": permissions.is_admin(),
            "role": permissions.role,
            "subscription_status": permissions.subscription_status,
            "subscription_end": permissions.subscription_end,
            "daily_api_calls": permissions.daily_api_calls,
            "daily_api_limit": permissions.get_daily_api_limit(),
            "remaining_calls": permissions.get_daily_api_limit() - permissions.daily_api_calls,
            "max_devices": permissions.max_device_count,
            "can_unlimited_divination": permissions.can_unlimited_divination
        }
        
    except Exception as e:
        logger.error(f"檢查用戶權限失敗 {user_id}: {e}")
        return {"error": str(e)}

# 付費功能限制響應
def create_premium_required_response():
    """創建需要付費的標準響應"""
    return {
        "error": "premium_required",
        "message": "此功能需要付費會員才能使用",
        "features_available": {
            "free": [
                "基本排盤",
                "星曜名稱顯示", 
                "每週一次占卜"
            ],
            "premium": [
                "四化詳細解釋",
                "流年/流月/流日功能",
                "Line綁定快速查詢",
                "無限制占卜"
            ]
        },
        "upgrade_options": [
            {"plan": "monthly", "price": 199, "description": "月費方案"},
            {"plan": "quarterly", "price": 499, "description": "季費方案"}, 
            {"plan": "yearly", "price": 1599, "description": "年費方案"}
        ]
    } 