"""
指定時間占卜 API 路由
支持對特定時間點進行占卜分析
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from app.db.database import get_db
from app.logic.divination_logic import divination_logic
from app.logic.permission_manager import permission_manager
from app.models.linebot_models import LineBotUser
from app.utils.divination_flex_message import DivinationFlexMessageGenerator
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

# 設定日誌
import logging
from datetime import datetime, timezone, timedelta

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

class TaipeiFormatter(logging.Formatter):
    """台北時區的日誌格式化器"""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=TAIPEI_TZ)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

# 設定日誌，使用台北時區
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 為所有處理程序設置台北時區格式化器
for handler in logging.root.handlers:
    handler.setFormatter(TaipeiFormatter('%(asctime)s - %(levelname)s - %(message)s'))

# 創建路由器
router = APIRouter()

# 速率限制器
limiter = Limiter(key_func=get_remote_address)


class TimeDivinationRequest(BaseModel):
    """指定時間占卜請求模型"""
    user_id: str = Field(..., description="用戶 ID")
    gender: str = Field(..., description="性別 (M/F)")
    target_time: str = Field(..., description="目標時間 (ISO 格式)")
    purpose: Optional[str] = Field(None, description="占卜目的")
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['M', 'F']:
            raise ValueError('性別必須是 M 或 F')
        return v
    
    @validator('target_time')
    def validate_target_time(cls, v):
        try:
            # 嘗試解析 ISO 格式時間
            parsed_time = datetime.fromisoformat(v.replace('Z', '+00:00'))
            
            # 檢查時間範圍（不能超過當前時間太久）
            now = datetime.now(TAIPEI_TZ)
            time_diff = now - parsed_time.astimezone(TAIPEI_TZ)
            
            # 限制在過去 30 天內
            if time_diff.days > 30:
                raise ValueError('目標時間不能超過 30 天前')
            
            # 限制在未來 7 天內
            if time_diff.days < -7:
                raise ValueError('目標時間不能超過 7 天後')
                
            return v
        except ValueError as e:
            raise ValueError(f'時間格式錯誤: {str(e)}')

class TimeDivinationResponse(BaseModel):
    """指定時間占卜回應模型"""
    success: bool
    divination_id: Optional[str] = None
    target_time: str
    current_time: str
    gender: str
    taichi_palace: str
    minute_dizhi: str
    palace_tiangan: str
    sihua_results: list
    purpose: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

@router.post("/api/time-divination", response_model=TimeDivinationResponse)
@limiter.limit("10/minute")  # 限制每分鐘 10 次
async def perform_time_divination(
    request: Request,
    divination_request: TimeDivinationRequest,
    db: Session = Depends(get_db)
):
    """
    執行指定時間占卜
    
    Args:
        divination_request: 占卜請求參數
        db: 數據庫會話
        
    Returns:
        TimeDivinationResponse: 占卜結果
    """
    try:
        logger.info(f"收到指定時間占卜請求 - 用戶: {divination_request.user_id}")
        
        # 1. 驗證用戶權限
        user = db.query(LineBotUser).filter(
            LineBotUser.line_user_id == divination_request.user_id
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 檢查用戶是否有權限使用指定時間占卜
        user_stats = permission_manager.get_user_stats(db, user)
        is_premium = user_stats["membership_info"]["is_premium"]
        is_admin = user_stats["user_info"]["is_admin"]
        
        # 只有管理員可以使用指定時間占卜
        if not is_admin:
            raise HTTPException(
                status_code=403, 
                detail="指定時間占卜功能僅限管理員使用"
            )
        
        # 2. 解析目標時間
        target_time = datetime.fromisoformat(
            divination_request.target_time.replace('Z', '+00:00')
        )
        
        # 轉換為台北時間
        if target_time.tzinfo is None:
            target_time = target_time.replace(tzinfo=timezone.utc)
        target_time = target_time.astimezone(TAIPEI_TZ)
        
        logger.info(f"目標時間: {target_time}")
        
        # 3. 執行占卜
        result = divination_logic.perform_divination(
            gender=divination_request.gender,
            current_time=target_time,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"占卜失敗: {result.get('error', '未知錯誤')}"
            )
        
        # 4. 記錄指定時間占卜歷史
        try:
            from app.models.divination import TimeDivinationHistory
            
            time_divination_record = TimeDivinationHistory(
                user_id=user.id,
                target_time=target_time,
                current_time=datetime.now(TAIPEI_TZ),
                gender=divination_request.gender,
                purpose=divination_request.purpose,
                taichi_palace=result["taichi_palace"],
                minute_dizhi=result["minute_dizhi"],
                sihua_results=json.dumps(result["sihua_results"], ensure_ascii=False)
            )
            
            db.add(time_divination_record)
            db.commit()
            logger.info("指定時間占卜記錄已保存")
            
        except Exception as e:
            logger.warning(f"保存指定時間占卜記錄失敗: {e}")
            db.rollback()
        
        # 5. 構建回應
        response = TimeDivinationResponse(
            success=True,
            divination_id=str(result.get("divination_id", "")),
            target_time=target_time.isoformat(),
            current_time=datetime.now(TAIPEI_TZ).isoformat(),
            gender=divination_request.gender,
            taichi_palace=result["taichi_palace"],
            minute_dizhi=result["minute_dizhi"],
            palace_tiangan=result["palace_tiangan"],
            sihua_results=result["sihua_results"],
            purpose=divination_request.purpose,
            message="指定時間占卜完成"
        )
        
        logger.info(f"指定時間占卜成功完成 - 用戶: {divination_request.user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"指定時間占卜錯誤: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"占卜系統錯誤: {str(e)}"
        )

@router.get("/api/time-divination/history/{user_id}")
@limiter.limit("20/minute")
async def get_time_divination_history(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    獲取用戶的指定時間占卜歷史
    
    Args:
        user_id: 用戶 ID
        db: 數據庫會話
        limit: 返回記錄數量限制
        
    Returns:
        list: 占卜歷史記錄
    """
    try:
        # 驗證用戶
        user = db.query(LineBotUser).filter(
            LineBotUser.line_user_id == user_id
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 獲取歷史記錄
        from app.models.divination import TimeDivinationHistory
        
        history_records = db.query(TimeDivinationHistory).filter(
            TimeDivinationHistory.user_id == user.id
        ).order_by(
            TimeDivinationHistory.current_time.desc()
        ).limit(limit).all()
        
        # 格式化結果
        history_list = []
        for record in history_records:
            history_list.append({
                "id": record.id,
                "target_time": record.target_time.isoformat(),
                "current_time": record.current_time.isoformat(),
                "gender": record.gender,
                "purpose": record.purpose,
                "taichi_palace": record.taichi_palace,
                "minute_dizhi": record.minute_dizhi,
                "sihua_count": len(json.loads(record.sihua_results or "[]"))
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "history": history_list,
            "total": len(history_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取占卜歷史錯誤: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"獲取歷史記錄失敗: {str(e)}"
        )

# 導出路由器
__all__ = ["router"] 