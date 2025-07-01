"""
FastAPI 主應用程序
"""
import os
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

app = FastAPI(
    title="Purple Star Astrology API",
    description="An API for calculating Purple Star Astrology charts.",
    version="1.0.0"
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
