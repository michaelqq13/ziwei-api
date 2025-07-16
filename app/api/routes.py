from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.logic.purple_star_chart import PurpleStarChart
from app.models.birth_info import BirthInfo
from app.models.schemas import BirthInfoSchema, PurpleStarChartSchema, ChartRequestWithCustomStem
from app.db.database import get_db
from app.db.repository import CalendarRepository
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chart", response_model=PurpleStarChartSchema)
def get_purple_star_chart(birth_data: BirthInfoSchema, db: Session = Depends(get_db)):
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        return chart.get_chart()
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/major-limits")
def get_chart_with_major_limits(
    birth_data: BirthInfoSchema, 
    current_age: Optional[int] = Query(None, description="當前年齡，用於確定當前大限"),
    db: Session = Depends(get_db)
):
    """獲取包含大限資訊的紫微斗數命盤"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        return chart.get_chart(include_major_limits=True, current_age=current_age)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/minor-limits")
def get_chart_with_minor_limits(
    birth_data: BirthInfoSchema, 
    target_age: Optional[int] = Query(None, description="目標年齡，用於確定特定年齡的小限"),
    db: Session = Depends(get_db)
):
    """獲取包含小限資訊的紫微斗數命盤"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        return chart.get_chart(include_minor_limits=True, target_age=target_age)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/full-limits")
def get_chart_with_full_limits(
    birth_data: BirthInfoSchema,
    current_age: Optional[int] = Query(None, description="當前年齡，用於確定當前大限"),
    target_age: Optional[int] = Query(None, description="目標年齡，用於確定特定年齡的小限"),
    db: Session = Depends(get_db)
):
    """獲取包含大限和小限資訊的完整紫微斗數命盤"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        return chart.get_chart(
            include_major_limits=True, 
            current_age=current_age,
            include_minor_limits=True, 
            target_age=target_age
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/annual-fortune")
def get_chart_with_annual_fortune(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    db: Session = Depends(get_db)
):
    """獲取流年資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        annual_fortune = chart.calculate_annual_fortune(target_year)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "annual_fortune": annual_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/monthly-fortune")
def get_chart_with_monthly_fortune(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12），如不指定則使用當前月份"),
    db: Session = Depends(get_db)
):
    """獲取流月資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        monthly_fortune = chart.calculate_monthly_fortune(target_year, target_month)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "monthly_fortune": monthly_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/daily-fortune")
def get_chart_with_daily_fortune(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12），如不指定則使用當前月份"),
    target_day: Optional[int] = Query(None, description="目標日期（農曆日1-30），如不指定則使用當前日期"),
    db: Session = Depends(get_db)
):
    """獲取流日資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        daily_fortune = chart.calculate_daily_fortune(target_year, target_month, target_day)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "daily_fortune": daily_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.get("/calendar/current-lunar")
def get_current_lunar_data(db: Session = Depends(get_db)):
    """獲取當前時間的農曆數據"""
    try:
        from datetime import datetime, timezone, timedelta
        
        # 台北時區
        TAIPEI_TZ = timezone(timedelta(hours=8))
        
        # 獲取當前台北時間
        now = datetime.now(TAIPEI_TZ)
        
        # 創建當前時間的BirthInfo
        current_birth_info = BirthInfo(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            gender="male",  # 預設值，不影響農曆計算
            longitude=121.5654,  # 台北經度
            latitude=25.0330     # 台北緯度
        )
        
        # 使用6tail服務獲取農曆資料
        from app.services.sixtail_service import sixtail_service
        lunar_data = sixtail_service.get_complete_info(
            current_birth_info.year,
            current_birth_info.month,
            current_birth_info.day,
            current_birth_info.hour,
            current_birth_info.minute
        )
        
        return {
            "success": True,
            "gregorian_date": f"{now.year}-{now.month:02d}-{now.day:02d}",
            "gregorian_time": f"{now.hour:02d}:{now.minute:02d}",
            "lunar_data": lunar_data
        }
        
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/four-transformations-explanations")
def get_four_transformations_explanations(
    birth_data: BirthInfoSchema,
    db: Session = Depends(get_db)
):
    """獲取四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        explanations = chart.get_four_transformations_explanations()
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/four-transformations-explanations-custom-stem")
def get_four_transformations_explanations_custom_stem(
    request: dict,
    db: Session = Depends(get_db)
):
    """使用自定義天干獲取四化解釋"""
    try:
        birth_data = request.get("birth_data")
        custom_stem = request.get("custom_stem")
        
        if not birth_data or not custom_stem:
            raise HTTPException(status_code=400, detail="birth_data and custom_stem are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        explanations = chart.get_four_transformations_explanations_by_stem(custom_stem)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "custom_stem": custom_stem,
            "explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/four-transformations-explanations-transformed")
def get_four_transformations_explanations_transformed(
    request: dict,
    db: Session = Depends(get_db)
):
    """獲取套用自定義天干四化後的解釋"""
    try:
        birth_data = request.get("birth_data")
        custom_stem = request.get("custom_stem")
        
        if not birth_data or not custom_stem:
            raise HTTPException(status_code=400, detail="birth_data and custom_stem are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 套用自定義天干的四化
        chart.apply_custom_stem_transformations(custom_stem)
        
        # 獲取解釋
        explanations = chart.get_four_transformations_explanations_by_stem(custom_stem)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "custom_stem": custom_stem,
            "chart": chart.get_chart(),
            "explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/annual-fortune-four-transformations")
def get_annual_fortune_four_transformations(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    db: Session = Depends(get_db)
):
    """獲取流年四化資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 計算流年
        annual_fortune = chart.calculate_annual_fortune(target_year)
        
        # 獲取流年天干
        annual_stem = annual_fortune.get("annual_stem")
        
        # 獲取流年四化解釋
        explanations = chart.get_four_transformations_explanations_by_stem(annual_stem)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "annual_fortune": annual_fortune,
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/monthly-fortune-four-transformations")
def get_monthly_fortune_four_transformations(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12），如不指定則使用當前月份"),
    db: Session = Depends(get_db)
):
    """獲取流月四化資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 計算流月
        monthly_fortune = chart.calculate_monthly_fortune(target_year, target_month)
        
        # 獲取流月天干
        monthly_stem = monthly_fortune.get("monthly_stem")
        
        # 獲取流月四化解釋
        explanations = chart.get_four_transformations_explanations_by_stem(monthly_stem)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "monthly_fortune": monthly_fortune,
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/daily-fortune-four-transformations")
def get_daily_fortune_four_transformations(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12），如不指定則使用當前月份"),
    target_day: Optional[int] = Query(None, description="目標日期（農曆日1-30），如不指定則使用當前日期"),
    db: Session = Depends(get_db)
):
    """獲取流日四化資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 計算流日
        daily_fortune = chart.calculate_daily_fortune(target_year, target_month, target_day)
        
        # 獲取流日天干
        daily_stem = daily_fortune.get("daily_stem")
        
        # 獲取流日四化解釋
        explanations = chart.get_four_transformations_explanations_by_stem(daily_stem)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "daily_fortune": daily_fortune,
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/major-limits-four-transformations")
def get_major_limits_four_transformations(
    birth_data: BirthInfoSchema,
    current_age: Optional[int] = Query(None, description="當前年齡，用於確定當前大限"),
    db: Session = Depends(get_db)
):
    """獲取大限四化資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 計算大限
        major_limits = chart.calculate_major_limits(current_age)
        
        # 獲取當前大限天干
        current_major_limit = None
        for limit in major_limits:
            if limit.get("is_current"):
                current_major_limit = limit
                break
        
        if current_major_limit:
            major_limit_stem = current_major_limit.get("stem")
            # 獲取大限四化解釋
            explanations = chart.get_four_transformations_explanations_by_stem(major_limit_stem)
        else:
            explanations = []
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "major_limits": major_limits,
            "current_major_limit": current_major_limit,
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/minor-limits-four-transformations")
def get_minor_limits_four_transformations(
    birth_data: BirthInfoSchema,
    target_age: Optional[int] = Query(None, description="目標年齡，用於確定特定年齡的小限"),
    db: Session = Depends(get_db)
):
    """獲取小限四化資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 計算小限
        minor_limits = chart.calculate_minor_limits(target_age)
        
        # 獲取目標年齡的小限天干
        target_minor_limit = None
        for limit in minor_limits:
            if limit.get("age") == target_age:
                target_minor_limit = limit
                break
        
        if target_minor_limit:
            minor_limit_stem = target_minor_limit.get("stem")
            # 獲取小限四化解釋
            explanations = chart.get_four_transformations_explanations_by_stem(minor_limit_stem)
        else:
            explanations = []
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "minor_limits": minor_limits,
            "target_minor_limit": target_minor_limit,
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/evil-stars-minute-branch")
def get_chart_with_evil_stars_minute_branch(
    request: dict,
    db: Session = Depends(get_db)
):
    """獲取包含分鐘地支凶星的命盤"""
    try:
        birth_data = request.get("birth_data")
        minute_branch = request.get("minute_branch")
        
        if not birth_data or not minute_branch:
            raise HTTPException(status_code=400, detail="birth_data and minute_branch are required")
        
        birth_info = BirthInfo(**birth_data)
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 計算凶星位置（基於分鐘地支）
        evil_stars = chart.star_calculator.calculate_evil_stars_minute_branch(minute_branch)
        
        # 將凶星加入對應宮位
        for star_name, palace_branch in evil_stars.items():
            # 找到對應的宮位
            target_palace = None
            for palace in chart.palaces.values():
                if palace.branch == palace_branch:
                    target_palace = palace
                    break
            
            if target_palace:
                if star_name not in target_palace.stars:
                    target_palace.stars.append(star_name)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "minute_branch": minute_branch,
            "evil_stars": evil_stars,
            "chart": chart.get_chart()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")

@router.post("/chart/with-custom-stem")
async def get_chart_with_custom_stem(request: ChartRequestWithCustomStem, db: Session = Depends(get_db)):
    """獲取套用自定義天干四化的命盤"""
    try:
        birth_info = BirthInfo(**request.birth_data.dict())
        
        chart = PurpleStarChart(birth_info=birth_info, db=db)
        
        # 套用自定義天干的四化
        chart.apply_custom_stem_transformations(request.custom_stem)
        
        return {
            "success": True,
            "birth_info": request.birth_data.dict(),
            "custom_stem": request.custom_stem,
            "chart": chart.get_chart()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="請求的資源不存在")
    except Exception as e:
        logger.error(f"命盤計算失敗: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用")
