from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.logic.purple_star_chart import PurpleStarChart
from app.models.birth_info import BirthInfo
from app.models.schemas import BirthInfoSchema, PurpleStarChartSchema, ChartRequestWithCustomStem
from app.db.database import get_db
from app.db.repository import CalendarRepository
from typing import Optional

router = APIRouter()

@router.post("/chart", response_model=PurpleStarChartSchema)
def get_purple_star_chart(birth_data: BirthInfoSchema, db: Session = Depends(get_db)):
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()  # 啟用星曜計算
        
        return chart.get_chart()
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/major-limits")
def get_chart_with_major_limits(
    birth_data: BirthInfoSchema, 
    current_age: Optional[int] = Query(None, description="當前年齡，用於確定當前大限"),
    db: Session = Depends(get_db)
):
    """獲取包含大限資訊的紫微斗數命盤"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        return chart.get_chart(include_major_limits=True, current_age=current_age)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/minor-limits")
def get_chart_with_minor_limits(
    birth_data: BirthInfoSchema, 
    target_age: Optional[int] = Query(None, description="目標年齡，用於確定特定年齡的小限"),
    db: Session = Depends(get_db)
):
    """獲取包含小限資訊的紫微斗數命盤"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        return chart.get_chart(include_minor_limits=True, target_age=target_age)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

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
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        return chart.get_chart(
            include_major_limits=True, 
            current_age=current_age,
            include_minor_limits=True, 
            target_age=target_age
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/annual-fortune")
def get_chart_with_annual_fortune(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    db: Session = Depends(get_db)
):
    """獲取流年資訊"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        annual_fortune = chart.calculate_annual_fortune(target_year)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "annual_fortune": annual_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

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
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        monthly_fortune = chart.calculate_monthly_fortune(target_year, target_month)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "monthly_fortune": monthly_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

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
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        daily_fortune = chart.calculate_daily_fortune(target_year, target_month, target_day)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "daily_fortune": daily_fortune
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/calendar/current-lunar")
def get_current_lunar_data(db: Session = Depends(get_db)):
    """獲取當前時間的農曆數據"""
    try:
        from datetime import datetime
        
        # 獲取當前時間
        now = datetime.now()
        
        # 創建當前時間的BirthInfo
        current_birth_info = BirthInfo(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            gender="男",  # 性別不影響農曆轉換
            longitude=121.5654,  # 默認經度（台北）
            latitude=25.0330     # 默認緯度（台北）
        )
        
        calendar_repo = CalendarRepository(db)
        calendar_data = calendar_repo.get_calendar_data(current_birth_info)
        
        if not calendar_data:
            raise HTTPException(status_code=404, detail="找不到當前時間的農曆資料")
        
        return {
            "success": True,
            "gregorian": {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute
            },
            "lunar": {
                "year": calendar_data.lunar_year_in_chinese,
                "month": calendar_data.lunar_month_in_chinese,
                "day": calendar_data.lunar_day_in_chinese,
                "year_gan_zhi": calendar_data.year_gan_zhi,
                "month_gan_zhi": calendar_data.month_gan_zhi,
                "day_gan_zhi": calendar_data.day_gan_zhi,
                "hour_gan_zhi": calendar_data.hour_gan_zhi
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取當前農曆資料失敗: {str(e)}")

@router.post("/chart/four-transformations-explanations")
def get_four_transformations_explanations(
    birth_data: BirthInfoSchema,
    db: Session = Depends(get_db)
):
    """獲取四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        explanations = chart.get_four_transformations_explanations()
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/four-transformations-explanations-custom-stem")
def get_four_transformations_explanations_custom_stem(
    request: dict,
    db: Session = Depends(get_db)
):
    """獲取自定義天干的四化解釋"""
    try:
        birth_data = request.get("birth_data")
        custom_stem = request.get("custom_stem")  # 自定義天干
        
        if not custom_stem:
            raise HTTPException(status_code=400, detail="custom_stem is required")
        
        birth_info = BirthInfo(**birth_data)
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取自定義天干的四化解釋
        explanations = chart.get_four_transformations_explanations_by_stem(custom_stem)
        
        return {
            "success": True,
            "birth_info": birth_data,
            "custom_stem": custom_stem,
            "four_transformations_explanations": explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/four-transformations-explanations-transformed")
def get_four_transformations_explanations_transformed(
    request: dict,
    db: Session = Depends(get_db)
):
    """獲取轉換後的四化解釋（太極點或流運模式）"""
    try:
        birth_data = request.get("birth_data")
        palace_mappings = request.get("palace_mappings", {})  # 格式: {"原宮位": "轉換後宮位"}
        
        birth_info = BirthInfo(**birth_data)
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取原始四化解釋
        original_explanations = chart.get_four_transformations_explanations()
        
        # 根據宮位映射轉換解釋
        transformed_explanations = {}
        
        for key, explanation in original_explanations.items():
            original_palace = explanation["宮位"]
            
            # 如果有映射關係，使用轉換後的宮位獲取新的解釋內容
            if original_palace in palace_mappings:
                transformed_palace = palace_mappings[original_palace]
                
                # 獲取轉換後宮位的解釋內容
                new_explanation = chart.star_calculator.get_explanation_for_palace(
                    explanation["星曜"],
                    explanation["四化"],
                    transformed_palace,
                    {'year_stem': chart.calendar_data.year_gan_zhi[0]}
                )
                
                if new_explanation:
                    transformed_explanations[key] = new_explanation
                else:
                    # 如果找不到對應解釋，保持原有但更新宮位名稱
                    transformed_explanations[key] = {
                        **explanation,
                        "宮位": transformed_palace
                    }
            else:
                # 沒有映射關係，保持原樣
                transformed_explanations[key] = explanation
        
        return {
            "success": True,
            "birth_info": birth_data,
            "four_transformations_explanations": transformed_explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/annual-fortune-four-transformations")
def get_annual_fortune_four_transformations(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    db: Session = Depends(get_db)
):
    """獲取流年四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取流年資訊
        annual_fortune = chart.calculate_annual_fortune(target_year)
        
        # 獲取本命盤四化解釋
        original_explanations = chart.get_four_transformations_explanations()
        
        # 根據流年宮位對應關係轉換四化解釋
        annual_explanations = {}
        annual_palaces = annual_fortune.get("流年宮位", {})
        
        for key, explanation in original_explanations.items():
            original_palace = explanation["宮位"]
            
            # 找到原宮位對應的流年宮位
            corresponding_annual_palace = None
            # 處理宮位名稱，直接使用原始名稱
            original_palace_normalized = original_palace
            
            for annual_name, annual_info in annual_palaces.items():
                if annual_info:
                    natal_palace = annual_info.get("本命宮位")
                    # 處理宮位名稱格式匹配
                    # 流年宮位對應表中的本命宮位名稱格式：命宮、父母、福德...
                    # 本命四化解釋中的宮位名稱格式：兄弟、夫妻、田宅...
                    
                    # 標準化宮位名稱，確保都有"宮"字後綴
                    if natal_palace and not natal_palace.endswith("宮"):
                        natal_palace = natal_palace + "宮"
                    
                    if original_palace_normalized and not original_palace_normalized.endswith("宮"):
                        original_palace_normalized = original_palace_normalized + "宮"
                    
                    if natal_palace == original_palace_normalized:
                        corresponding_annual_palace = annual_name
                        break
            
            if corresponding_annual_palace:
                # 獲取流年宮位的四化解釋
                new_explanation = chart.star_calculator.get_explanation_for_palace(
                    explanation["星曜"],
                    explanation["四化"],
                    corresponding_annual_palace.replace("流年", ""),  # 移除"流年"前綴用於查找解釋
                    {'year_stem': chart.calendar_data.year_gan_zhi[0]}
                )
                
                if new_explanation:
                    annual_explanations[key] = {
                        **new_explanation,
                        "宮位": corresponding_annual_palace,
                        "流年年份": annual_fortune.get("目標年份"),
                        "流年地支": annual_fortune.get("年份地支")
                    }
                else:
                    # 保持原有解釋但更新宮位名稱
                    annual_explanations[key] = {
                        **explanation,
                        "宮位": corresponding_annual_palace,
                        "流年年份": annual_fortune.get("目標年份"),
                        "流年地支": annual_fortune.get("年份地支")
                    }
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "annual_fortune": annual_fortune,
            "four_transformations_explanations": annual_explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/monthly-fortune-four-transformations")
def get_monthly_fortune_four_transformations(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12），如不指定則使用當前月份"),
    db: Session = Depends(get_db)
):
    """獲取流月四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取流月資訊
        monthly_fortune = chart.calculate_monthly_fortune(target_year, target_month)
        
        # 獲取本命盤四化解釋
        original_explanations = chart.get_four_transformations_explanations()
        
        # 根據流月宮位對應關係轉換四化解釋
        monthly_explanations = {}
        monthly_palaces = monthly_fortune.get("流月宮位", {})
        
        for key, explanation in original_explanations.items():
            original_palace = explanation["宮位"]
            
            # 找到原宮位對應的流月宮位
            corresponding_monthly_palace = None
            # 處理宮位名稱，確保格式一致
            original_palace_normalized = original_palace
            if not original_palace.endswith("宮"):
                original_palace_normalized = original_palace + "宮"
                
            for monthly_name, monthly_info in monthly_palaces.items():
                if monthly_info:
                    natal_palace = monthly_info.get("本命宮位")
                    # 同樣處理本命宮位名稱格式
                    if natal_palace and not natal_palace.endswith("宮"):
                        natal_palace = natal_palace + "宮"
                    
                    if natal_palace == original_palace_normalized:
                        corresponding_monthly_palace = monthly_name
                        break
            
            if corresponding_monthly_palace:
                # 獲取流月宮位的四化解釋 - 移除"流月"前綴來獲取基本宮位名稱
                basic_palace_name = corresponding_monthly_palace.replace("流月", "")
                new_explanation = chart.star_calculator.get_explanation_for_palace(
                    explanation["星曜"],
                    explanation["四化"],
                    basic_palace_name,
                    {'year_stem': chart.calendar_data.year_gan_zhi[0]}
                )
                
                if new_explanation:
                    monthly_explanations[key] = {
                        **new_explanation,
                        "宮位": corresponding_monthly_palace,
                        "流年年份": monthly_fortune.get("目標年份"),
                        "流月月份": monthly_fortune.get("目標月份")
                    }
                else:
                    # 保持原有解釋但更新宮位名稱和內容
                    monthly_explanations[key] = {
                        **explanation,
                        "宮位": corresponding_monthly_palace,
                        "流年年份": monthly_fortune.get("目標年份"),
                        "流月月份": monthly_fortune.get("目標月份")
                    }
            else:
                # 如果找不到對應的流月宮位，保持原有解釋
                monthly_explanations[key] = explanation
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "monthly_fortune": monthly_fortune,
            "four_transformations_explanations": monthly_explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/daily-fortune-four-transformations")
def get_daily_fortune_four_transformations(
    birth_data: BirthInfoSchema,
    target_year: Optional[int] = Query(None, description="目標年份（西元年），如不指定則使用當前年份"),
    target_month: Optional[int] = Query(None, description="目標月份（農曆月1-12），如不指定則使用當前月份"),
    target_day: Optional[int] = Query(None, description="目標日期（農曆日1-30），如不指定則使用當前日期"),
    db: Session = Depends(get_db)
):
    """獲取流日四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取流日資訊
        daily_fortune = chart.calculate_daily_fortune(target_year, target_month, target_day)
        
        # 獲取本命盤四化解釋
        original_explanations = chart.get_four_transformations_explanations()
        
        # 根據流日宮位對應關係轉換四化解釋
        daily_explanations = {}
        daily_palaces = daily_fortune.get("流日宮位", {})
        
        for key, explanation in original_explanations.items():
            original_palace = explanation["宮位"]
            
            # 找到原宮位對應的流日宮位
            corresponding_daily_palace = None
            # 處理宮位名稱，直接使用原始名稱
            original_palace_normalized = original_palace
                
            for daily_name, daily_info in daily_palaces.items():
                if daily_info:
                    natal_palace = daily_info.get("本命宮位")
                    # 處理宮位名稱格式匹配
                    # 流日宮位對應表中的本命宮位名稱格式：命宮、父母、福德...
                    # 本命四化解釋中的宮位名稱格式：兄弟、夫妻、田宅...
                    
                    # 標準化宮位名稱，確保都有"宮"字後綴
                    if natal_palace and not natal_palace.endswith("宮"):
                        natal_palace = natal_palace + "宮"
                    
                    if original_palace_normalized and not original_palace_normalized.endswith("宮"):
                        original_palace_normalized = original_palace_normalized + "宮"
                    
                    if natal_palace == original_palace_normalized:
                        corresponding_daily_palace = daily_name
                        break
            
            if corresponding_daily_palace:
                # 獲取流日宮位的四化解釋 - 移除"流日"前綴來獲取基本宮位名稱
                basic_palace_name = corresponding_daily_palace.replace("流日", "")
                new_explanation = chart.star_calculator.get_explanation_for_palace(
                    explanation["星曜"],
                    explanation["四化"],
                    basic_palace_name,
                    {'year_stem': chart.calendar_data.year_gan_zhi[0]}
                )
                
                if new_explanation:
                    daily_explanations[key] = {
                        **new_explanation,
                        "宮位": corresponding_daily_palace,
                        "流年年份": daily_fortune.get("目標年份"),
                        "流月月份": daily_fortune.get("目標月份"),
                        "流日日期": daily_fortune.get("目標日期")
                    }
                else:
                    # 保持原有解釋但更新宮位名稱和內容
                    daily_explanations[key] = {
                        **explanation,
                        "宮位": corresponding_daily_palace,
                        "流年年份": daily_fortune.get("目標年份"),
                        "流月月份": daily_fortune.get("目標月份"),
                        "流日日期": daily_fortune.get("目標日期")
                    }
            else:
                # 如果找不到對應的流日宮位，保持原有解釋
                daily_explanations[key] = explanation
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "daily_fortune": daily_fortune,
            "four_transformations_explanations": daily_explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/major-limits-four-transformations")
def get_major_limits_four_transformations(
    birth_data: BirthInfoSchema,
    current_age: Optional[int] = Query(None, description="當前年齡，用於確定當前大限"),
    db: Session = Depends(get_db)
):
    """獲取大限四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取大限資訊
        major_limits_result = chart.get_chart(include_major_limits=True, current_age=current_age)
        major_limits = major_limits_result.get("major_limits")
        
        # 獲取本命盤四化解釋
        original_explanations = chart.get_four_transformations_explanations()
        
        # 根據當前大限宮位轉換四化解釋
        major_limit_explanations = {}
        current_major_limit = major_limits.get("當前大限") if major_limits else None
        
        if current_major_limit:
            current_palace = current_major_limit.get("宮位名稱")
            current_branch = current_major_limit.get("地支")
            
            # 建立本命宮位到大限宮位的對應關係
            palace_mapping = {}
            all_major_limits = major_limits.get("所有大限", [])
            
            # 找到當前大限在十二宮中的位置（正確順序：命宮 → 父母 → 福德 → 田宅 → 官祿 → 交友 → 遷移 → 疾厄 → 財帛 → 子女 → 夫妻 → 兄弟）
            palace_names = ["命宮", "父母", "福德", "田宅", "官祿", "交友", "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"]
            current_limit_index = None
            
            for i, palace_name in enumerate(palace_names):
                if palace_name == current_palace:
                    current_limit_index = i
                    break
            

            
            if current_limit_index is not None:
                # 建立宮位對應關係：本命宮位 -> 大限宮位
                # 正確邏輯：根據地支位置對應，而不是宫位名稱索引
                current_major_limit_branch = current_major_limit.get("地支")
                earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
                
                # 找到當前大限地支的索引
                current_branch_index = earthly_branches.index(current_major_limit_branch)
                
                # 建立本命宮位到大限宮位的地支對應關係
                # 正確邏輯：本命宮位的地支 對應到 大限體系中相同地支的宮位名稱
                for palace_name, palace_info in chart.palaces.items():
                    # 獲取本命宮位的地支
                    natal_branch = palace_info.branch
                    
                    # 找到大限中該地支對應的宮位名稱
                    for target_palace_name, target_palace_info in chart.palaces.items():
                        if target_palace_info.branch == natal_branch:
                            # 確定該地支在大限體系中的十二宮名稱
                            # 大限命宮的地支 = current_major_limit_branch
                            # 計算該地支相對於大限命宮的偏移
                            natal_branch_index = earthly_branches.index(natal_branch)
                            offset = (natal_branch_index - current_branch_index + 12) % 12
                            
                            # 根據偏移確定大限宮位名稱
                            limit_palace_names = ["命宮", "父母", "福德", "田宅", "官祿", "交友", "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"]
                            target_limit_palace = limit_palace_names[offset]
                            
                            palace_mapping[palace_name] = f"大限{target_limit_palace}"
                            break
                

            
            for key, explanation in original_explanations.items():
                original_palace = explanation["宮位"]
                
                # 處理宮位名稱，直接使用原始名稱
                original_palace_normalized = original_palace
                
                # 找到對應的大限宮位
                corresponding_major_limit_palace = palace_mapping.get(original_palace_normalized)

                
                if corresponding_major_limit_palace:
                    # 獲取大限宮位的四化解釋
                    basic_palace_name = corresponding_major_limit_palace.replace("大限", "")
                    new_explanation = chart.star_calculator.get_explanation_for_palace(
                        explanation["星曜"],
                        explanation["四化"],
                        basic_palace_name,
                        {'year_stem': chart.calendar_data.year_gan_zhi[0]}
                    )
                    
                    if new_explanation:
                        major_limit_explanations[key] = {
                            **new_explanation,
                            "宮位": corresponding_major_limit_palace,
                            "大限宮位": current_palace,
                            "大限年齡範圍": current_major_limit.get("年齡範圍"),
                            "大限重點": f"本命{original_palace}四化對應到{corresponding_major_limit_palace}",
                            "palace_mapping": corresponding_major_limit_palace
                        }
                    else:
                        # 保持原有解釋但更新宮位名稱
                        major_limit_explanations[key] = {
                            **explanation,
                            "宮位": corresponding_major_limit_palace,
                            "大限宮位": current_palace,
                            "大限年齡範圍": current_major_limit.get("年齡範圍"),
                            "大限重點": f"本命{original_palace}四化對應到{corresponding_major_limit_palace}",
                            "palace_mapping": corresponding_major_limit_palace
                        }
                else:
                    # 如果找不到對應的大限宮位，保持原有解釋
                    major_limit_explanations[key] = {
                        **explanation,
                        "大限宮位": current_palace,
                        "大限年齡範圍": current_major_limit.get("年齡範圍"),
                        "大限重點": f"此四化在{original_palace}，對當前大限({current_palace})有間接影響"
                    }
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "major_limits": major_limits,
            "four_transformations_explanations": major_limit_explanations,

        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/minor-limits-four-transformations")
def get_minor_limits_four_transformations(
    birth_data: BirthInfoSchema,
    target_age: Optional[int] = Query(None, description="目標年齡，用於確定特定年齡的小限"),
    db: Session = Depends(get_db)
):
    """獲取小限四化解釋"""
    try:
        birth_info = BirthInfo(**birth_data.dict())
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 獲取小限資訊
        minor_limits_result = chart.get_chart(include_minor_limits=True, target_age=target_age)
        minor_limits = minor_limits_result.get("minor_limits")
        
        # 獲取本命盤四化解釋
        original_explanations = chart.get_four_transformations_explanations()
        
        # 根據當前小限宮位轉換四化解釋
        minor_limit_explanations = {}
        current_minor_limit = minor_limits.get("小限資訊") if minor_limits else None
        
        if current_minor_limit:
            current_palace = current_minor_limit.get("宮位名稱")
            target_age_value = current_minor_limit.get("年齡")
            
            # 建立本命宮位到小限宮位的對應關係
            palace_mapping = {}
            
            # 找到當前小限宮位在十二宮中的位置（正確順序：命宮 → 父母 → 福德 → 田宅 → 官祿 → 交友 → 遷移 → 疾厄 → 財帛 → 子女 → 夫妻 → 兄弟）
            palace_names = ["命宮", "父母", "福德", "田宅", "官祿", "交友", "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"]
            current_limit_index = None
            
            for i, palace_name in enumerate(palace_names):
                if palace_name == current_palace:
                    current_limit_index = i
                    break
            
            if current_limit_index is not None:
                # 建立宮位對應關係：本命宮位 -> 小限宮位
                # 正確邏輯：根據地支位置對應，而不是宫位名稱索引
                current_minor_limit_branch = current_minor_limit.get("地支")
                earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
                
                # 找到當前小限地支的索引
                current_branch_index = earthly_branches.index(current_minor_limit_branch)
                
                # 建立本命宮位到小限宮位的地支對應關係
                # 正確邏輯：本命宮位的地支 對應到 小限體系中相同地支的宮位名稱
                for palace_name, palace_info in chart.palaces.items():
                    # 獲取本命宮位的地支
                    natal_branch = palace_info.branch
                    
                    # 找到小限中該地支對應的宮位名稱
                    for target_palace_name, target_palace_info in chart.palaces.items():
                        if target_palace_info.branch == natal_branch:
                            # 確定該地支在小限體系中的十二宮名稱
                            # 小限命宮的地支 = current_minor_limit_branch
                            # 計算該地支相對於小限命宮的偏移
                            natal_branch_index = earthly_branches.index(natal_branch)
                            offset = (natal_branch_index - current_branch_index + 12) % 12
                            
                            # 根據偏移確定小限宮位名稱
                            limit_palace_names = ["命宮", "父母", "福德", "田宅", "官祿", "交友", "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"]
                            target_limit_palace = limit_palace_names[offset]
                            
                            palace_mapping[palace_name] = f"小限{target_limit_palace}"
                            break
            
            for key, explanation in original_explanations.items():
                original_palace = explanation["宮位"]
                
                # 處理宮位名稱，直接使用原始名稱
                original_palace_normalized = original_palace
                
                # 找到對應的小限宮位
                corresponding_minor_limit_palace = palace_mapping.get(original_palace_normalized)
                
                if corresponding_minor_limit_palace:
                    # 獲取小限宮位的四化解釋
                    basic_palace_name = corresponding_minor_limit_palace.replace("小限", "")
                    new_explanation = chart.star_calculator.get_explanation_for_palace(
                        explanation["星曜"],
                        explanation["四化"],
                        basic_palace_name,
                        {'year_stem': chart.calendar_data.year_gan_zhi[0]}
                    )
                    
                    if new_explanation:
                        minor_limit_explanations[key] = {
                            **new_explanation,
                            "宮位": corresponding_minor_limit_palace,
                            "小限宮位": current_palace,
                            "小限年齡": target_age_value,
                            "小限重點": f"本命{original_palace}四化對應到{corresponding_minor_limit_palace}",
                            "palace_mapping": corresponding_minor_limit_palace
                        }
                    else:
                        # 保持原有解釋但更新宮位名稱
                        minor_limit_explanations[key] = {
                            **explanation,
                            "宮位": corresponding_minor_limit_palace,
                            "小限宮位": current_palace,
                            "小限年齡": target_age_value,
                            "小限重點": f"本命{original_palace}四化對應到{corresponding_minor_limit_palace}",
                            "palace_mapping": corresponding_minor_limit_palace
                        }
                else:
                    # 如果找不到對應的小限宮位，保持原有解釋
                    minor_limit_explanations[key] = {
                        **explanation,
                        "小限宮位": current_palace,
                        "小限年齡": target_age_value,
                        "小限重點": f"此四化在{original_palace}，對當前小限({current_palace})有間接影響"
                    }
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "minor_limits": minor_limits,
            "four_transformations_explanations": minor_limit_explanations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/evil-stars-minute-branch")
def get_chart_with_evil_stars_minute_branch(
    request: dict,
    db: Session = Depends(get_db)
):
    """獲取使用分鐘地支計算凶星的命盤"""
    try:
        birth_data = request.get("birth_data")
        minute_branch = request.get("minute_branch")
        
        if not birth_data or not minute_branch:
            raise HTTPException(status_code=400, detail="Missing birth_data or minute_branch")
        
        birth_info = BirthInfo(**birth_data)
        
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 準備傳遞給StarCalculator的birth_info
        year_stem = chart.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = chart.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = chart.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        from app.utils.chinese_calendar import ChineseCalendar
        lunar_day = ChineseCalendar.parse_chinese_day(chart.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(chart.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(chart.birth_info.hour)
        }
        
        # 使用分鐘地支重新計算凶星位置
        chart.star_calculator.recalculate_evil_stars_with_minute_branch(
            birth_info_for_calculator,
            chart.palaces,
            minute_branch
        )
        
        return chart.get_chart()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/chart/with-custom-stem")
async def get_chart_with_custom_stem(request: ChartRequestWithCustomStem, db: Session = Depends(get_db)):
    """獲取帶有自定義天干四化的命盤"""
    try:
        birth_data = request.birth_data
        custom_stem = request.custom_stem
        
        birth_info = BirthInfo(**birth_data.dict())
        calendar_repo = CalendarRepository(db)
        
        chart = PurpleStarChart(birth_info, calendar_repo)
        chart.initialize()
        chart.calculate_stars()
        
        # 應用自定義天干四化
        chart.apply_custom_stem_transformations(custom_stem)
        
        return {
            "success": True,
            "birth_info": birth_data.dict(),
            "custom_stem": custom_stem,
            "chart_data": chart.get_chart()
        }
    except Exception as e:
        import traceback
        print(f"Error in get_chart_with_custom_stem: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
