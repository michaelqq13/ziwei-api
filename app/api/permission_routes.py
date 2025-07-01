from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.db.database import get_db
from app.logic.permission_manager import PermissionManager
from app.logic.device_manager import DeviceManager

logger = logging.getLogger(__name__)

router = APIRouter()

class UpgradeRequest(BaseModel):
    subscription_days: int = 30

class AdminSetRequest(BaseModel):
    target_user_id: str

class UserStatusResponse(BaseModel):
    user_id: str
    role: str
    is_admin: bool
    is_premium: bool
    subscription_status: str
    daily_api_calls: int
    daily_api_limit: int

@router.get("/status/{user_id}", response_model=UserStatusResponse)
async def get_user_status(user_id: str, db: Session = Depends(get_db)):
    """獲取用戶權限狀態"""
    try:
        status = PermissionManager.get_user_status_summary(user_id, db)
        
        if "error" in status:
            raise HTTPException(status_code=500, detail=status["error"])
        
        return UserStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"獲取用戶狀態失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取用戶狀態失敗")

@router.post("/check-premium/{user_id}")
async def check_premium_access(user_id: str, db: Session = Depends(get_db)):
    """檢查用戶付費權限"""
    try:
        has_access = PermissionManager.check_premium_access(user_id, db)
        is_admin = PermissionManager.check_admin_access(user_id, db)
        
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
        limit_info = PermissionManager.check_api_rate_limit(user_id, db)
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
        if not PermissionManager.check_admin_access(admin_user_id, db):
            raise HTTPException(status_code=403, detail="需要管理員權限")
        
        success = PermissionManager.upgrade_to_premium(
            user_id, 
            request.subscription_days, 
            db
        )
        
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
        if not PermissionManager.check_admin_access(admin_user_id, db):
            raise HTTPException(status_code=403, detail="需要管理員權限")
        
        success = PermissionManager.set_admin_permissions(request.target_user_id, db)
        
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
        # 簡單的安全檢查（生產環境應該使用更安全的方式）
        import os
        if secret_key != os.getenv("ADMIN_INIT_SECRET", "your-secret-key"):
            raise HTTPException(status_code=403, detail="無效的密鑰")
        
        success = PermissionManager.set_admin_permissions(user_id, db)
        
        if success:
            return {"success": True, "message": f"管理員權限初始化成功: {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="初始化失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"初始化管理員權限失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="初始化過程發生錯誤")

@router.post("/check-device-access/{user_id}")
async def check_device_access(
    user_id: str,
    user_agent: str = None,
    ip_address: str = None,
    db: Session = Depends(get_db)
):
    """檢查設備訪問權限"""
    try:
        # 生成設備指紋
        device_fingerprint = DeviceManager.generate_device_fingerprint(
            user_agent or "", ip_address or ""
        )
        
        # 檢查設備權限
        access_result = DeviceManager.check_device_access(
            user_id, device_fingerprint, user_agent, ip_address, db
        )
        
        return access_result
        
    except Exception as e:
        logger.error(f"檢查設備權限失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="檢查設備權限失敗")

@router.get("/devices/{user_id}")
async def get_user_devices(user_id: str, db: Session = Depends(get_db)):
    """獲取用戶設備列表"""
    try:
        devices = DeviceManager.get_user_devices(user_id, db)
        stats = DeviceManager.get_device_usage_stats(user_id, db)
        
        return {
            "devices": devices,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"獲取設備列表失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取設備列表失敗")

@router.post("/devices/{user_id}/deactivate/{device_id}")
async def deactivate_device(
    user_id: str, 
    device_id: int, 
    db: Session = Depends(get_db)
):
    """停用指定設備"""
    try:
        success = DeviceManager.deactivate_device(user_id, device_id, db)
        
        if success:
            return {"success": True, "message": "設備已停用"}
        else:
            raise HTTPException(status_code=404, detail="找不到指定設備")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停用設備失敗 {user_id}, {device_id}: {e}")
        raise HTTPException(status_code=500, detail="停用設備失敗") 