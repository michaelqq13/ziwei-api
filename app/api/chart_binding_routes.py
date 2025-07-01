from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.db.database import get_db
from app.logic.user_binding import UserBindingManager
from app.logic.purple_star_chart import PurpleStarChart
from app.models.birth_info import BirthInfo
from app.models.schemas import BirthInfoSchema
from app.db.repository import CalendarRepository
from app.utils.permission_middleware import RequireFree, check_user_permissions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chart-binding", tags=["命盤綁定"])

class ChartBindingRequest(BaseModel):
    birth_data: BirthInfoSchema
    save_to_line: bool = False

class ChartBindingResponse(BaseModel):
    success: bool
    chart_data: Optional[Dict[str, Any]] = None
    binding_info: Optional[Dict[str, Any]] = None
    message: str

class SaveToLineRequest(BaseModel):
    birth_data: BirthInfoSchema

class SaveToLineResponse(BaseModel):
    success: bool
    message: str
    expires_in_seconds: int = 0
    instructions: str

@router.post("/calculate-and-save", response_model=ChartBindingResponse)
async def calculate_chart_and_save(
    request: ChartBindingRequest,
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """計算命盤並可選擇保存到Line帳號"""
    try:
        # 計算命盤
        birth_info = BirthInfo(**request.birth_data.dict())
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        chart_result = chart.get_chart()
        
        # 免費版限制：移除四化詳細解釋
        if "four_transformations" in chart_result:
            for transformation in chart_result["four_transformations"]:
                if "explanation" in transformation:
                    transformation["explanation"] = "詳細解釋需要付費會員"
                if "analysis" in transformation:
                    transformation["analysis"] = "詳細分析需要付費會員"
        
        chart_result["version"] = "free"
        chart_result["calculated_for_user"] = current_user_id
        
        response = ChartBindingResponse(
            success=True,
            chart_data=chart_result,
            message="命盤計算完成"
        )
        
        # 如果用戶選擇保存到Line
        if request.save_to_line:
            binding_success = UserBindingManager.create_pending_binding(
                request.birth_data.dict(), db
            )
            
            if binding_success:
                response.binding_info = {
                    "pending_binding_created": True,
                    "expires_in_seconds": 60,
                    "instructions": "請在1分鐘內打開Line Bot並輸入「綁定」來完成綁定"
                }
                response.message = "命盤計算完成，待綁定記錄已創建"
            else:
                response.binding_info = {
                    "pending_binding_created": False,
                    "error": "創建待綁定記錄失敗"
                }
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"計算命盤並保存失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"計算失敗: {str(e)}")

@router.post("/save-to-line", response_model=SaveToLineResponse)
async def save_chart_to_line(
    request: SaveToLineRequest,
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """保存命盤到Line帳號（分離的API）"""
    try:
        # 創建待綁定記錄
        success = UserBindingManager.create_pending_binding(
            request.birth_data.dict(), db
        )
        
        if success:
            return SaveToLineResponse(
                success=True,
                message="待綁定記錄已創建",
                expires_in_seconds=60,
                instructions="請在1分鐘內打開Line Bot並輸入「綁定」來完成綁定"
            )
        else:
            return SaveToLineResponse(
                success=False,
                message="創建待綁定記錄失敗",
                instructions="請稍後再試或聯繫客服"
            )
            
    except Exception as e:
        logger.error(f"保存到Line失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="保存失敗")

@router.get("/binding-status")
async def get_binding_status(
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """獲取當前用戶的綁定狀態"""
    try:
        # 檢查用戶權限
        user_permissions = check_user_permissions(current_user_id, db)
        
        # 檢查是否已綁定
        is_bound = UserBindingManager.is_user_bound(current_user_id, db)
        
        if is_bound:
            # 獲取綁定資訊
            birth_info = UserBindingManager.get_user_birth_info(current_user_id, db)
            
            return {
                "success": True,
                "is_bound": True,
                "user_permissions": user_permissions,
                "birth_info": birth_info,
                "message": "帳號已綁定命盤"
            }
        else:
            return {
                "success": True,
                "is_bound": False,
                "user_permissions": user_permissions,
                "message": "帳號尚未綁定命盤"
            }
            
    except Exception as e:
        logger.error(f"獲取綁定狀態失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取狀態失敗")

@router.get("/bound-chart")
async def get_bound_chart(
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """獲取已綁定的命盤（快速查詢）"""
    try:
        # 檢查是否已綁定
        if not UserBindingManager.is_user_bound(current_user_id, db):
            raise HTTPException(status_code=404, detail="帳號尚未綁定命盤")
        
        # 獲取綁定的生辰資料
        birth_data = UserBindingManager.get_user_birth_info(current_user_id, db)
        if not birth_data:
            raise HTTPException(status_code=404, detail="找不到綁定的命盤資料")
        
        # 計算命盤
        birth_info = BirthInfo(**birth_data)
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        chart_result = chart.get_chart()
        
        # 檢查用戶權限決定返回內容
        user_permissions = check_user_permissions(current_user_id, db)
        
        if not user_permissions.get("is_premium", False):
            # 免費版限制
            if "four_transformations" in chart_result:
                for transformation in chart_result["four_transformations"]:
                    if "explanation" in transformation:
                        transformation["explanation"] = "詳細解釋需要付費會員"
                    if "analysis" in transformation:
                        transformation["analysis"] = "詳細分析需要付費會員"
            chart_result["version"] = "free"
        else:
            chart_result["version"] = "premium"
        
        chart_result["bound_user_id"] = current_user_id
        chart_result["is_bound_chart"] = True
        
        return {
            "success": True,
            "chart_data": chart_result,
            "user_permissions": user_permissions,
            "message": "已綁定命盤查詢成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取綁定命盤失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="查詢失敗")

@router.delete("/unbind")
async def unbind_chart(
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """解除命盤綁定（需要管理員權限或特殊情況）"""
    try:
        # 檢查用戶權限
        user_permissions = check_user_permissions(current_user_id, db)
        
        # 只有管理員可以解除綁定
        if not user_permissions.get("is_admin", False):
            raise HTTPException(
                status_code=403, 
                detail={
                    "error": "權限不足",
                    "message": "解除綁定需要管理員權限，請聯繫客服",
                    "contact_info": "如需修改命盤資料，請聯繫客服"
                }
            )
        
        # 執行解除綁定
        success = UserBindingManager.unbind_user(current_user_id, db)
        
        if success:
            return {
                "success": True,
                "message": "命盤綁定已解除"
            }
        else:
            return {
                "success": False,
                "message": "解除綁定失敗"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解除綁定失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="解除綁定失敗")

@router.get("/upgrade-prompt")
async def get_upgrade_prompt(
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """獲取升級提示信息"""
    try:
        user_permissions = check_user_permissions(current_user_id, db)
        
        if user_permissions.get("is_premium", False):
            return {
                "success": True,
                "is_premium": True,
                "message": "您已是付費會員，享有完整功能"
            }
        
        return {
            "success": True,
            "is_premium": False,
            "upgrade_benefits": {
                "current_limitations": [
                    "四化解釋顯示「需要付費會員」",
                    "無法使用流年/流月/流日功能",
                    "每日API調用限制100次",
                    "僅支援1個設備"
                ],
                "premium_features": [
                    "完整四化詳細解釋",
                    "流年/流月/流日運勢分析",
                    "Line Bot快速查詢綁定命盤",
                    "無限制占卜功能",
                    "每日API調用1000次",
                    "支援2個設備同時使用"
                ],
                "pricing": [
                    {"plan": "monthly", "price": 199, "description": "月費方案"},
                    {"plan": "quarterly", "price": 499, "description": "季費方案，省98元"},
                    {"plan": "yearly", "price": 1599, "description": "年費方案，省789元"}
                ]
            },
            "call_to_action": "立即升級享受完整功能"
        }
        
    except Exception as e:
        logger.error(f"獲取升級提示失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="獲取升級信息失敗") 