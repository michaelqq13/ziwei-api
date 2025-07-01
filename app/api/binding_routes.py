from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.db.database import get_db
from app.logic.user_binding import UserBindingManager

logger = logging.getLogger(__name__)

router = APIRouter()

class BindingCheckResponse(BaseModel):
    is_bound: bool
    message: str

class CreateBindingRequest(BaseModel):
    birth_data: Dict[str, Any]

class CreateBindingResponse(BaseModel):
    success: bool
    message: str
    expires_in_seconds: int = 0

@router.get("/check/{user_id}", response_model=BindingCheckResponse)
async def check_binding_status(user_id: str, db: Session = Depends(get_db)):
    """檢查用戶綁定狀態"""
    try:
        is_bound = UserBindingManager.is_user_bound(user_id, db)
        
        if is_bound:
            return BindingCheckResponse(
                is_bound=True,
                message="帳號已綁定命盤"
            )
        else:
            return BindingCheckResponse(
                is_bound=False,
                message="帳號尚未綁定命盤"
            )
            
    except Exception as e:
        logger.error(f"檢查綁定狀態失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="系統錯誤")

@router.post("/create-pending", response_model=CreateBindingResponse)
async def create_pending_binding(request: CreateBindingRequest, db: Session = Depends(get_db)):
    """創建待綁定記錄（網頁端調用）"""
    try:
        # 創建待綁定記錄
        success = UserBindingManager.create_pending_binding(request.birth_data, db)
        
        if success:
            return CreateBindingResponse(
                success=True,
                message="待綁定記錄已創建，請在1分鐘內到Line Bot輸入「綁定」",
                expires_in_seconds=60
            )
        else:
            return CreateBindingResponse(
                success=False,
                message="創建待綁定記錄失敗"
            )
            
    except Exception as e:
        logger.error(f"創建待綁定記錄失敗: {e}")
        raise HTTPException(status_code=500, detail="系統錯誤")

@router.get("/info/{user_id}")
async def get_user_binding_info(user_id: str, db: Session = Depends(get_db)):
    """獲取用戶綁定資訊"""
    try:
        info = UserBindingManager.get_user_birth_info(user_id, db)
        
        if info:
            return {
                "success": True,
                "data": info
            }
        else:
            return {
                "success": False,
                "message": "找不到綁定資料"
            }
            
    except Exception as e:
        logger.error(f"獲取用戶綁定資訊失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="系統錯誤") 