"""
權限管理 API 路由
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.logic.permission_manager import permission_manager
from app.models.linebot_models import LineBotUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/permissions", tags=["permissions"])

class UserStatusResponse(BaseModel):
    """用戶狀態響應模型"""
    user_id: str
    role: str
    is_premium: bool
    is_admin: bool
    subscription_status: str
    total_divinations: int
    weekly_divinations: int
    weekly_limit: int

class UpgradeRequest(BaseModel):
    """升級請求模型"""
    subscription_days: int

class AdminSetRequest(BaseModel):
    """管理員設置請求模型"""
    target_user_id: str

@router.get("/status/{user_id}")
async def get_user_status(user_id: str, db: Session = Depends(get_db)):
    """獲取用戶權限狀態"""
    try:
        # 獲取或創建用戶
        user = permission_manager.get_or_create_user(db, user_id)
        
        # 獲取用戶統計
        stats = permission_manager.get_user_stats(db, user)
        
        return {
            "user_id": user_id,
            "role": stats["membership_info"]["level_name"],
            "is_premium": stats["membership_info"]["is_premium"],
            "is_admin": stats["membership_info"]["is_admin"],
            "subscription_status": "active" if stats["membership_info"]["is_premium"] else "none",
            "total_divinations": stats["statistics"]["total_divinations"],
            "weekly_divinations": stats["statistics"]["weekly_divinations"],
            "weekly_limit": stats["statistics"]["weekly_limit"]
        }
        
    except Exception as e:
        logger.error(f"獲取用戶狀態失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取用戶狀態失敗")

@router.post("/check-premium/{user_id}")
async def check_premium_access(user_id: str, db: Session = Depends(get_db)):
    """檢查用戶付費權限"""
    try:
        user = permission_manager.get_or_create_user(db, user_id)
        
        has_access = user.is_premium()
        is_admin = user.is_admin()
        
        return {
            "has_premium_access": has_access,
            "is_admin": is_admin,
            "access_level": "admin" if is_admin else ("premium" if has_access else "free")
        }
        
    except Exception as e:
        logger.error(f"檢查付費權限失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="檢查權限失敗")

@router.post("/check-api-limit/{user_id}")
async def check_api_limit(user_id: str, db: Session = Depends(get_db)):
    """檢查API調用限制"""
    try:
        user = permission_manager.get_or_create_user(db, user_id)
        
        # 基本限制信息
        limit_info = {
            "user_id": user_id,
            "daily_limit": 1000 if user.is_premium() else 100,
            "is_premium": user.is_premium(),
            "is_admin": user.is_admin()
        }
        
        return limit_info
        
    except Exception as e:
        logger.error(f"檢查API限制失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="檢查API限制失敗")

@router.post("/upgrade/{user_id}")
async def upgrade_to_premium(
    user_id: str, 
    request: UpgradeRequest, 
    admin_user_id: str,
    db: Session = Depends(get_db)
):
    """升級用戶為付費會員（需要管理員權限）"""
    try:
        # 檢查操作者是否為管理員
        admin_user = permission_manager.get_or_create_user(db, admin_user_id)
        if not admin_user.is_admin():
            raise HTTPException(status_code=403, detail="需要管理員權限")
        
        # 升級用戶
        success = permission_manager.upgrade_to_premium(db, user_id)
        
        if success:
            return {"success": True, "message": f"用戶 {user_id} 已升級為付費會員"}
        else:
            raise HTTPException(status_code=500, detail="升級失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"升級付費會員失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="升級過程發生錯誤")

@router.post("/set-admin")
async def set_admin_permissions(
    request: AdminSetRequest,
    admin_user_id: str,
    db: Session = Depends(get_db)
):
    """設定管理員權限（需要現有管理員權限）"""
    try:
        # 檢查操作者是否為管理員
        admin_user = permission_manager.get_or_create_user(db, admin_user_id)
        if not admin_user.is_admin():
            raise HTTPException(status_code=403, detail="需要管理員權限")
        
        # 設定管理員權限
        success = permission_manager.set_admin_permissions(request.target_user_id, db)
        
        if success:
            return {"success": True, "message": f"用戶 {request.target_user_id} 已設定為管理員"}
        else:
            raise HTTPException(status_code=500, detail="設定管理員權限失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"設定管理員權限失敗: {e}")
        raise HTTPException(status_code=500, detail="設定權限過程發生錯誤")

@router.get("/admin/init/{user_id}")
async def init_admin(user_id: str, secret_key: str, db: Session = Depends(get_db)):
    """初始化管理員權限（僅供系統初始化使用）"""
    try:
        # 簡單的安全檢查
        import os
        if secret_key != os.getenv("ADMIN_INIT_SECRET", "ziwei-admin-2024"):
            raise HTTPException(status_code=403, detail="無效的密鑰")
        
        success = permission_manager.set_admin_permissions(user_id, db)
        
        if success:
            return {"success": True, "message": f"管理員權限初始化成功: {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="初始化失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"初始化管理員權限失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="初始化過程發生錯誤")

@router.get("/devices/{user_id}")
async def get_user_devices(user_id: str, db: Session = Depends(get_db)):
    """獲取用戶設備列表"""
    try:
        user = permission_manager.get_or_create_user(db, user_id)
        
        # 基本設備信息
        devices = {
            "devices": [
                {
                    "device_id": "default",
                    "device_name": "LINE App",
                    "last_active": datetime.utcnow().isoformat(),
                    "is_active": True
                }
            ],
            "stats": {
                "total_devices": 1,
                "active_devices": 1,
                "device_limit": 2 if user.is_premium() else 1
            }
        }
        
        return devices
        
    except Exception as e:
        logger.error(f"獲取設備列表失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取設備列表失敗") 