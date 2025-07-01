"""
FastAPI 主應用程序
"""
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.api import divination_routes
from app.api import binding_routes
from app.api import permission_routes
from app.api import protected_routes
from app.api import payment_routes
from app.api import chart_binding_routes
from app.api import webhook  # Added LINE Bot webhook
from app.logic.divination_logic import divination_logic
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_database_migrations():
    """在應用啟動時運行數據庫遷移"""
    try:
        logger.info("開始執行數據庫遷移...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            logger.info("數據庫遷移成功完成")
            logger.info(f"遷移輸出: {result.stdout}")
        else:
            logger.error(f"數據庫遷移失敗: {result.stderr}")
            logger.error(f"遷移輸出: {result.stdout}")
            # 不拋出異常，讓應用繼續啟動
            
    except Exception as e:
        logger.error(f"執行數據庫遷移時發生錯誤: {str(e)}")
        # 不拋出異常，讓應用繼續啟動

def init_test_data():
    """初始化測試數據"""
    try:
        from app.db.init_test_data import init_test_data as run_init_test_data
        logger.info("開始初始化測試數據...")
        run_init_test_data()
        logger.info("測試數據初始化完成")
    except Exception as e:
        logger.error(f"初始化測試數據時發生錯誤: {str(e)}")
        # 不拋出異常，讓應用繼續啟動

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    logger.info("應用啟動中...")
    run_database_migrations()
    init_test_data()
    logger.info("應用啟動完成")
    
    yield
    
    # 關閉時執行
    logger.info("應用正在關閉...")

app = FastAPI(
    title="Purple Star Astrology API",
    description="An API for calculating Purple Star Astrology charts.",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法
    allow_headers=["*"],  # 允許所有請求頭
)

# API路由
app.include_router(routes.router, prefix="/api")
app.include_router(divination_routes.router)
app.include_router(binding_routes.router, prefix="/api/binding")
app.include_router(permission_routes.router, prefix="/api/permissions")
app.include_router(protected_routes.router, prefix="/api")
app.include_router(payment_routes.router, prefix="/api/payment")
app.include_router(chart_binding_routes.router, prefix="/api")
app.include_router(webhook.router)  # LINE Bot webhook at root path

@app.get("/")
def read_root():
    return {"message": "Welcome to the Purple Star Astrology API"}

@app.get("/test-divination")
async def test_divination(db: Session = Depends(get_db)):
    """測試特定時間的占卜結果"""
    try:
        logger.info("開始執行占卜測試")
        test_time = datetime(2025, 6, 30, 22, 51)
        gender = "M"
        
        logger.info(f"測試參數 - 時間：{test_time}, 性別：{gender}")
        
        result = divination_logic.perform_divination(gender, test_time, db)
        logger.info(f"占卜結果：{result}")
        
        if result["success"]:
            # 驗證結果
            basic_chart = result.get("basic_chart", {})
            ming_palace = next((palace for palace_name, palace in basic_chart.items() if palace_name == "命宮"), None)
            
            verification = {
                "命宮地支": ming_palace["dizhi"] if ming_palace else None,
                "分鐘地支": result.get("minute_dizhi"),
                "太極點命宮": result.get("taichi_palace"),
                "宮干": result.get("palace_tiangan")
            }
            
            expected = {
                "命宮地支": "申",
                "分鐘地支": "亥",
                "太極點命宮": "亥宮",
                "宮干": "丁"
            }
            
            matches = {
                key: {
                    "actual": value,
                    "expected": expected[key],
                    "matches": value == expected[key]
                }
                for key, value in verification.items()
            }
            
            return {
                "success": True,
                "message": "測試成功",
                "result": result,
                "verification": matches
            }
        else:
            logger.error(f"占卜失敗：{result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"測試過程發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
