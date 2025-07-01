from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from app.db.database import get_db
from app.logic.divination import (
    can_divination_this_week,
    get_this_week_divination,
    get_user_divination_gender,
    save_user_divination_gender,
    calculate_divination,
    save_divination_record,
    get_days_until_next_monday
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/divination", tags=["divination"])

@router.post("/check/{user_id}")
async def check_divination_status(user_id: str, db: Session = Depends(get_db)):
    """檢查用戶的占卜狀態"""
    try:
        from app.logic.permission_manager import PermissionManager
        
        # 檢查權限和限制
        permission_result = PermissionManager.check_divination_permission(user_id, db)
        
        if permission_result["can_divinate"]:
            # 檢查是否有性別偏好
            gender = get_user_divination_gender(user_id, db)
            return {
                "can_divinate": True,
                "has_gender_preference": gender is not None,
                "gender": gender,
                "is_premium": permission_result.get("is_premium", False),
                "reason": permission_result.get("reason", "allowed")
            }
        else:
            # 獲取本週的占卜記錄（如果是週限制）
            this_week_result = None
            if permission_result["reason"] == "weekly_limit_reached":
                this_week_record = get_this_week_divination(user_id, db)
                this_week_result = this_week_record.divination_result if this_week_record else None
            
            return {
                "can_divinate": False,
                "reason": permission_result["reason"],
                "days_until_reset": permission_result.get("days_until_reset", 0),
                "this_week_result": this_week_result,
                "is_premium": permission_result.get("is_premium", False)
            }
            
    except Exception as e:
        logger.error(f"檢查占卜狀態失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="檢查占卜狀態失敗")

@router.post("/perform/{user_id}")
async def perform_divination(user_id: str, gender: str, db: Session = Depends(get_db)):
    """執行占卜"""
    try:
        # 檢查週限制
        if not can_divination_this_week(user_id, db):
            raise HTTPException(status_code=400, detail="本週已經占卜過了")
        
        # 驗證性別參數
        if gender not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="性別參數無效")
        
        # 執行占卜計算
        current_time = datetime.now()
        divination_result = calculate_divination(current_time, gender, db=db)
        
        # 保存占卜記錄
        record = save_divination_record(user_id, current_time, gender, divination_result, db)
        
        # 保存性別偏好（如果用戶之前沒有設定）
        if not get_user_divination_gender(user_id, db):
            save_user_divination_gender(user_id, gender, db)
        
        return {
            "success": True,
            "result": divination_result,
            "record_id": record.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"執行占卜失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="占卜計算失敗")

@router.post("/set-gender/{user_id}")
async def set_divination_gender(user_id: str, gender: str, db: Session = Depends(get_db)):
    """設定用戶的占卜性別偏好"""
    try:
        if gender not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="性別參數無效")
        
        save_user_divination_gender(user_id, gender, db)
        
        return {
            "success": True,
            "message": "性別偏好已保存"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"設定性別偏好失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="設定失敗")

@router.get("/history/{user_id}")
async def get_divination_history(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """獲取用戶的占卜歷史記錄"""
    try:
        from app.models.divination import DivinationRecord
        
        records = db.query(DivinationRecord).filter(
            DivinationRecord.user_id == user_id
        ).order_by(DivinationRecord.divination_time.desc()).limit(limit).all()
        
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "divination_time": record.divination_time.isoformat(),
                "week_start_date": record.week_start_date.isoformat(),
                "gender": record.gender,
                "result": record.divination_result
            })
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"獲取占卜歷史失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取歷史記錄失敗") 