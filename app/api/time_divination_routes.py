"""
指定時間占卜 API 路由 - 重構版本
使用統一的 TimeDivinationService
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.models.linebot_models import LineBotUser
from app.services.time_divination_service import (
    TimeDivinationService, 
    TimeDivinationRequest, 
    TimeDivinationResponse
)

logger = logging.getLogger(__name__)

# 限流器
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/api/time-divination", response_model=TimeDivinationResponse)
@limiter.limit("10/minute")  # 限制每分鐘 10 次
async def perform_time_divination(
    request: Request,
    divination_request: TimeDivinationRequest,
    db: Session = Depends(get_db)
):
    """
    執行指定時間占卜 - 重構版本
    
    Args:
        divination_request: 占卜請求參數
        db: 數據庫會話
        
    Returns:
        TimeDivinationResponse: 占卜結果
    """
    try:
        logger.info(f"🎯 收到指定時間占卜 API 請求 - 性別: {divination_request.gender}, 時間: {divination_request.target_time}")
        
        # 1. 驗證用戶存在（API 需要額外的用戶 ID 參數）
        # 注意：這裡需要添加用戶 ID 到請求模型中
        # 暫時使用測試用戶或從請求中獲取
        user_id = getattr(divination_request, 'user_id', None)
        if not user_id:
            raise HTTPException(status_code=400, detail="缺少用戶 ID")
            
        user = db.query(LineBotUser).filter(
            LineBotUser.line_user_id == user_id
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 2. 使用統一服務執行占卜
        result = TimeDivinationService.execute_time_divination(
            user=user,
            gender=divination_request.gender,
            target_time=divination_request.target_time,
            db=db,
            purpose=divination_request.purpose
        )
        
        logger.info(f"✅ API 占卜完成 - 成功: {result.success}")
        return result
        
    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        logger.error(f"❌ API 指定時間占卜失敗: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"占卜服務錯誤: {str(e)}"
        )

# 為了向後兼容，保留舊的請求模型（添加 user_id 字段）
class LegacyTimeDivinationRequest(TimeDivinationRequest):
    """向後兼容的請求模型"""
    user_id: str  # 添加用戶 ID 字段

@router.post("/api/time-divination-legacy", response_model=TimeDivinationResponse)
@limiter.limit("10/minute")
async def perform_time_divination_legacy(
    request: Request,
    divination_request: LegacyTimeDivinationRequest,
    db: Session = Depends(get_db)
):
    """
    執行指定時間占卜 - 向後兼容版本
    包含用戶 ID 字段
    """
    try:
        logger.info(f"🎯 收到舊版 API 請求 - 用戶: {divination_request.user_id}")
        
        # 驗證用戶
        user = db.query(LineBotUser).filter(
            LineBotUser.line_user_id == divination_request.user_id
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 使用統一服務
        result = TimeDivinationService.execute_time_divination(
            user=user,
            gender=divination_request.gender,
            target_time=divination_request.target_time,
            db=db,
            purpose=divination_request.purpose
        )
        
        logger.info(f"✅ 舊版 API 占卜完成 - 成功: {result.success}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 舊版 API 指定時間占卜失敗: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"占卜服務錯誤: {str(e)}"
        )

# 導出
__all__ = ["router"] 