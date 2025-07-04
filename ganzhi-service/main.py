#!/usr/bin/env python3
"""
干支計算微服務 - 檔案模式專用
提供獨立的干支查詢服務，使用預先準備的完整干支資料檔案
"""
import logging
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from ganzhi_calculator import GanzhiCalculator

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="干支計算微服務",
    description="專門用於干支計算的獨立微服務，使用檔案資料模式",
    version="2.0.0"
)

# 初始化計算器
try:
    calculator = GanzhiCalculator()
    logger.info("干支計算器初始化成功")
except Exception as e:
    logger.error(f"初始化干支計算器失敗: {e}")
    calculator = None

@app.get("/")
async def root():
    """根路徑 - 服務狀態"""
    return {
        "service": "干支計算微服務",
        "version": "2.0.0",
        "mode": "檔案模式",
        "status": "running",
        "calculator_ready": calculator is not None
    }

@app.get("/ganzhi")
async def get_ganzhi(
    ts: int = Query(..., description="Unix 時間戳"),
    timezone_offset: int = Query(8, description="時區偏移（小時），預設為 UTC+8")
):
    """
    計算指定時間的干支信息
    
    Args:
        ts: Unix 時間戳
        timezone_offset: 時區偏移（小時），預設為 UTC+8
        
    Returns:
        包含年月日時干支和農曆信息的 JSON
    """
    if calculator is None:
        logger.error("計算器未初始化")
        raise HTTPException(status_code=503, detail="服務尚未準備就緒，計算器未初始化")
    
    try:
        logger.info(f"收到干支查詢請求: timestamp={ts}, timezone_offset={timezone_offset}")
        
        # 驗證時間戳
        if ts <= 0:
            raise HTTPException(status_code=400, detail="無效的時間戳")
        
        # 計算干支
        result = calculator.calculate_ganzhi(ts, timezone_offset)
        
        if result.get("data_source") == "error":
            error_msg = result.get("error", "未知錯誤")
            logger.error(f"干支計算失敗: {error_msg}")
            raise HTTPException(status_code=404, detail=f"計算失敗: {error_msg}")
        
        logger.info(f"干支計算成功: {result}")
        return JSONResponse(content=result)
        
    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        error_msg = f"處理干支查詢請求時發生錯誤: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/info")
async def get_service_info():
    """
    獲取服務信息和狀態
    
    Returns:
        服務狀態和資料統計信息
    """
    if calculator is None:
        return JSONResponse(content={
            "status": "error",
            "error": "計算器未初始化"
        })
    
    try:
        info = calculator.get_service_info()
        logger.info(f"服務狀態查詢: {info}")
        return JSONResponse(content=info)
        
    except Exception as e:
        error_msg = f"獲取服務信息時發生錯誤: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return JSONResponse(content={
            "status": "error",
            "error": error_msg
        })

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    if calculator is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "計算器未初始化"
            }
        )
    
    try:
        info = calculator.get_service_info()
        
        # 檢查服務是否健康
        is_healthy = (
            info.get("file_connected", False) and 
            info.get("records_count", 0) > 0
        )
        
        if is_healthy:
            return JSONResponse(content={
                "status": "healthy",
                "message": "服務運行正常",
                "records_count": info.get("records_count")
            })
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy", 
                    "message": "資料檔案未正確載入",
                    "info": info
                }
            )
            
    except Exception as e:
        error_msg = f"健康檢查失敗: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": error_msg
            }
        )

@app.get("/test")
async def test_endpoint():
    """測試端點 - 用於驗證特定測試案例"""
    if calculator is None:
        raise HTTPException(status_code=503, detail="服務尚未準備就緒")
    
    try:
        # 測試 2025/7/3 22:07 的案例
        test_timestamp = 1751551620
        result = calculator.calculate_ganzhi(test_timestamp, 8)
        
        return {
            "test_case": "2025/7/3 22:07",
            "timestamp": test_timestamp,
            "result": result,
            "expected": {
                "year_ganzhi": "乙巳",
                "month_ganzhi": "壬午",
                "day_ganzhi": "癸酉",
                "hour_ganzhi": "癸亥",
                "lunar_month": "六月",
                "lunar_day": "初九"
            },
            "matches_expected": (
                result.get("year_ganzhi") == "乙巳" and
                result.get("month_ganzhi") == "壬午" and
                result.get("day_ganzhi") == "癸酉" and
                result.get("hour_ganzhi") == "癸亥" and
                result.get("lunar_month") == "六月" and
                result.get("lunar_day") == "初九"
            )
        }
        
    except Exception as e:
        error_msg = f"測試失敗: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    
    logger.info("啟動干支計算微服務 - 檔案模式")
    logger.info("=" * 50)
    
    # 顯示服務信息
    if calculator:
        info = calculator.get_service_info()
        logger.info(f"服務狀態: {info}")
    else:
        logger.error("計算器初始化失敗")
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 