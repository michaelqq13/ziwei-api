"""
占卜 API 路由 - 重構版
簡化邏輯，確保穩定運行
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from app.db.database import get_db
from app.logic.permission_manager import permission_manager
from app.logic.divination import (
    can_divination_this_week,
    get_this_week_divination,
    get_user_divination_gender,
    save_user_divination_gender,
    calculate_divination,
    save_divination_result
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/divination", tags=["divination"])

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

@router.post("/check/{user_id}")
async def check_divination_status(user_id: str, db: Session = Depends(get_db)):
    """檢查用戶的占卜狀態"""
    try:
        # 獲取或創建用戶
        user = permission_manager.get_or_create_user(db, user_id)
        
        # 檢查占卜權限
        permission_result = permission_manager.check_divination_permission(db, user)
        
        if permission_result["allowed"]:
            # 檢查是否有性別偏好
            gender = get_user_divination_gender(user_id, db)
            return {
                "can_divinate": True,
                "has_gender_preference": gender is not None,
                "gender": gender,
                "is_premium": user.is_premium(),
                "reason": permission_result.get("reason", "allowed")
            }
        else:
            # 獲取本週的占卜記錄
            this_week_record = get_this_week_divination(user_id, db)
            this_week_result = this_week_record.divination_result if this_week_record else None
            
            return {
                "can_divinate": False,
                "reason": permission_result["reason"],
                "days_until_reset": get_days_until_next_monday(),
                "this_week_result": this_week_result,
                "is_premium": user.is_premium()
            }
            
    except Exception as e:
        logger.error(f"檢查占卜狀態失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用，請稍後再試")

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
        
        # 執行占卜計算 - 使用台北時間
        current_time = get_current_taipei_time()
        divination_result = calculate_divination(current_time, gender, db=db)
        
        # 保存占卜記錄
        success = save_divination_result(user_id, divination_result, db)
        
        # 保存性別偏好（如果用戶之前沒有設定）
        existing_gender = get_user_divination_gender(user_id, db)
        if not existing_gender:
            save_user_divination_gender(user_id, gender, db)
        
        if success:
            return {
                "success": True,
                "message": "占卜完成",
                "result": divination_result,
                "next_divination_available": "下週一"
            }
        else:
            return {
                "success": False,
                "error": "保存占卜結果失敗"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"執行占卜失敗 {user_id}: {e}")
        raise HTTPException(status_code=500, detail="占卜服務暫時不可用，請稍後再試")

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