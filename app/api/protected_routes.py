from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.logic.purple_star_chart import PurpleStarChart
from app.models.birth_info import BirthInfo
from app.models.schemas import BirthInfoSchema, PurpleStarChartSchema, ChartRequestWithCustomStem
from app.db.database import get_db
from app.db.repository import CalendarRepository
from app.utils.permission_middleware import (
    RequireFree, 
    RequirePremium, 
    RequireAdmin,
    PermissionLevel, 
    check_user_permissions,
    create_premium_required_response
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/protected", tags=["受保護的功能"])

# ============ 免費功能 ============

@router.post("/chart/basic", response_model=PurpleStarChartSchema)
async def get_basic_chart(
    birth_data: BirthInfoSchema,
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """基本排盤功能（免費）- 顯示星曜名稱但不含四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        result = chart.get_chart()
        
        # 免費版：移除四化詳細解釋，只保留基本信息
        if "four_transformations" in result:
            # 保留四化星曜名稱，但移除詳細解釋
            for transformation in result["four_transformations"]:
                if "explanation" in transformation:
                    transformation["explanation"] = "詳細解釋需要付費會員"
                if "analysis" in transformation:
                    transformation["analysis"] = "詳細分析需要付費會員"
        
        result["version"] = "free"
        result["user_id"] = current_user_id
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"基本排盤失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="排盤服務暫時不可用")

@router.get("/user/status")
async def get_user_status(
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """獲取用戶狀態（免費）"""
    try:
        user_permissions = check_user_permissions(current_user_id, db)
        return {
            "success": True,
            "user_status": user_permissions,
            "available_features": {
                "free": ["基本排盤", "星曜名稱顯示", "每週一次占卜"],
                "premium": ["四化詳細解釋", "流年/流月/流日功能", "Line綁定快速查詢", "無限制占卜"] if not user_permissions.get("is_premium") else []
            }
        }
    except Exception as e:
        logger.error(f"獲取用戶狀態失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

# ============ 付費功能 ============

@router.post("/chart/premium")
async def get_premium_chart(
    birth_data: BirthInfoSchema,
    db: Session = Depends(get_db),
    current_user_id: str = RequirePremium
):
    """完整排盤功能（付費）- 包含四化詳細解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        result = chart.get_chart()
        result["version"] = "premium"
        result["user_id"] = current_user_id
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"排盤計算失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="排盤服務暫時不可用")

@router.post("/chart/four-transformations")
async def get_four_transformations_premium(
    birth_data: BirthInfoSchema,
    db: Session = Depends(get_db),
    current_user_id: str = RequirePremium
):
    """四化詳細解釋（付費功能）"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        four_transformations = chart.get_four_transformations_explanations()
        
        return {
            "success": True,
            "user_id": current_user_id,
            "birth_info": birth_data.dict(),
            "four_transformations": four_transformations,
            "version": "premium"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"四化解釋計算失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/annual-fortune")
async def get_annual_fortune_premium(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    db: Session = Depends(get_db),
    current_user_id: str = RequirePremium
):
    """流年運勢（付費功能）"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        annual_fortune = chart.calculate_annual_fortune(target_year)
        
        return {
            "success": True,
            "user_id": current_user_id,
            "birth_info": birth_data.dict(),
            "annual_fortune": annual_fortune,
            "version": "premium"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"流年運勢計算失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/monthly-fortune")
async def get_monthly_fortune_premium(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年）"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12）"),
    db: Session = Depends(get_db),
    current_user_id: str = RequirePremium
):
    """流月運勢（付費功能）"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        monthly_fortune = chart.calculate_monthly_fortune(target_year, target_month)
        
        return {
            "success": True,
            "user_id": current_user_id,
            "birth_info": birth_data.dict(),
            "monthly_fortune": monthly_fortune,
            "version": "premium"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"流月運勢計算失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/daily-fortune")
async def get_daily_fortune_premium(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年）"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12）"),
    target_day: Optional[int] = Query(None, description="目標日期（農曆日1-30）"),
    db: Session = Depends(get_db),
    current_user_id: str = RequirePremium
):
    """流日運勢（付費功能）"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        daily_fortune = chart.calculate_daily_fortune(target_year, target_month, target_day)
        
        return {
            "success": True,
            "user_id": current_user_id,
            "birth_info": birth_data.dict(),
            "daily_fortune": daily_fortune,
            "version": "premium"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"流日運勢計算失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

# ============ 管理員功能 ============

@router.get("/admin/users")
async def get_all_users(
    skip: int = Query(0, description="跳過記錄數"),
    limit: int = Query(100, description="返回記錄數"),
    db: Session = Depends(get_db),
    current_user_id: str = RequireAdmin
):
    """獲取所有用戶列表（管理員功能）"""
    try:
        from app.models.user_permissions import UserPermissions
        
        users = db.query(UserPermissions).offset(skip).limit(limit).all()
        
        return {
            "success": True,
            "admin_user_id": current_user_id,
            "users": [
                {
                    "user_id": user.user_id,
                    "role": user.role,
                    "subscription_status": user.subscription_status,
                    "subscription_end": user.subscription_end,
                    "daily_api_calls": user.daily_api_calls,
                    "created_at": user.created_at
                }
                for user in users
            ],
            "total_count": db.query(UserPermissions).count()
        }
        
    except Exception as e:
        logger.error(f"獲取用戶列表失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

# ============ 功能升級提示 ============

@router.get("/upgrade-info")
async def get_upgrade_info(
    db: Session = Depends(get_db),
    current_user_id: str = RequireFree
):
    """獲取升級信息（所有用戶可訪問）"""
    try:
        user_permissions = check_user_permissions(current_user_id, db) if current_user_id else {}
        
        return {
            "success": True,
            "current_user": user_permissions,
            "features_comparison": {
                "free": {
                    "features": [
                        "基本排盤功能",
                        "星曜名稱顯示",
                        "每週一次占卜",
                        "基本宮位信息"
                    ],
                    "limitations": [
                        "無四化詳細解釋",
                        "無流年/流月/流日功能",
                        "每日API調用100次限制",
                        "僅支援1個設備"
                    ]
                },
                "premium": {
                    "features": [
                        "完整四化詳細解釋",
                        "流年運勢分析",
                        "流月運勢分析", 
                        "流日運勢分析",
                        "Line Bot快速查詢",
                        "無限制占卜",
                        "優先客服支援"
                    ],
                    "benefits": [
                        "每日API調用1000次",
                        "支援2個設備同時使用",
                        "完整功能無限制使用"
                    ]
                }
            },
            "pricing": {
                "monthly": {"price": 199, "description": "月費方案", "savings": 0},
                "quarterly": {"price": 499, "description": "季費方案", "savings": 98},
                "yearly": {"price": 1599, "description": "年費方案", "savings": 789}
            }
        }
        
    except Exception as e:
        logger.error(f"獲取升級信息失敗 {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/taichi", response_model=PurpleStarChartSchema)
def get_purple_star_chart_taichi(request: dict, db: Session = Depends(get_db)):
    """獲取太極點命盤"""
    try:
        birth_data = request.get("birth_data")
        taichi_branch = request.get("taichi_branch")
        
        if not birth_data or not taichi_branch:
            raise HTTPException(status_code=400, detail="birth_data and taichi_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        chart.apply_taichi(taichi_branch)
        
        return chart.get_chart()
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"太極點命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/taichi-sihua-explanations")
def get_taichi_sihua_explanations(request: dict, db: Session = Depends(get_db)):
    """獲取太極點四化解釋"""
    try:
        birth_data = request.get("birth_data")
        taichi_branch = request.get("taichi_branch")
        
        if not birth_data or not taichi_branch:
            raise HTTPException(status_code=400, detail="birth_data and taichi_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        chart.apply_taichi(taichi_branch)
        
        # 獲取太極點天干
        taichi_stem = chart.palaces[f"太極{taichi_branch}"].stem
        
        # 獲取太極點四化解釋
        explanations = chart.get_taichi_sihua_explanations(taichi_stem)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "taichi_branch": taichi_branch,
            "taichi_stem": taichi_stem,
            "explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"太極點四化解釋失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/taichi-with-sihua")
def get_taichi_chart_with_sihua(request: dict, db: Session = Depends(get_db)):
    """獲取太極點命盤及四化解釋"""
    try:
        birth_data = request.get("birth_data")
        taichi_branch = request.get("taichi_branch")
        
        if not birth_data or not taichi_branch:
            raise HTTPException(status_code=400, detail="birth_data and taichi_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        chart.apply_taichi(taichi_branch)
        
        # 獲取太極點天干
        taichi_stem = chart.palaces[f"太極{taichi_branch}"].stem
        
        # 獲取太極點四化解釋
        explanations = chart.get_taichi_sihua_explanations(taichi_stem)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "taichi_branch": taichi_branch,
            "taichi_stem": taichi_stem,
            "chart": chart.get_chart(),
            "explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"太極點命盤及四化解釋失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/taichi-annual-fortune")
def get_taichi_annual_fortune(request: dict, db: Session = Depends(get_db)):
    """獲取太極點流年資訊"""
    try:
        birth_data = request.get("birth_data")
        taichi_branch = request.get("taichi_branch")
        target_year = request.get("target_year")
        
        if not birth_data or not taichi_branch:
            raise HTTPException(status_code=400, detail="birth_data and taichi_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        chart.apply_taichi(taichi_branch)
        
        # 計算流年
        annual_fortune = chart.calculate_annual_fortune(target_year)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "taichi_branch": taichi_branch,
            "annual_fortune": annual_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"太極點流年計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/taichi-monthly-fortune")
def get_taichi_monthly_fortune(request: dict, db: Session = Depends(get_db)):
    """獲取太極點流月資訊"""
    try:
        birth_data = request.get("birth_data")
        taichi_branch = request.get("taichi_branch")
        target_year = request.get("target_year")
        target_month = request.get("target_month")
        
        if not birth_data or not taichi_branch:
            raise HTTPException(status_code=400, detail="birth_data and taichi_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        chart.apply_taichi(taichi_branch)
        
        # 計算流月
        monthly_fortune = chart.calculate_monthly_fortune(target_year, target_month)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "taichi_branch": taichi_branch,
            "monthly_fortune": monthly_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"太極點流月計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/taichi-daily-fortune")
def get_taichi_daily_fortune(request: dict, db: Session = Depends(get_db)):
    """獲取太極點流日資訊"""
    try:
        birth_data = request.get("birth_data")
        taichi_branch = request.get("taichi_branch")
        target_year = request.get("target_year")
        target_month = request.get("target_month")
        target_day = request.get("target_day")
        
        if not birth_data or not taichi_branch:
            raise HTTPException(status_code=400, detail="birth_data and taichi_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        chart.apply_taichi(taichi_branch)
        
        # 計算流日
        daily_fortune = chart.calculate_daily_fortune(target_year, target_month, target_day)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "taichi_branch": taichi_branch,
            "daily_fortune": daily_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"太極點流日計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用") 