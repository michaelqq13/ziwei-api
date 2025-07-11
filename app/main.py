"""
FastAPI 主應用程序
"""
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api import routes
from app.api import divination_routes
from app.api import time_divination_routes
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
from app.utils.security_middleware import security_check_middleware

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 速率限制器
limiter = Limiter(key_func=get_remote_address)

def run_database_migrations():
    """在應用啟動時運行數據庫遷移"""
    try:
        # 先測試數據庫連接
        from app.db.database import engine
        with engine.connect() as connection:
            logger.info("數據庫連接成功，開始執行遷移...")
        
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
            
    except Exception as e:
        logger.warning(f"數據庫不可用，跳過遷移: {str(e)}")
        logger.info("應用將在無數據庫模式下運行")

def init_test_data():
    """初始化測試數據"""
    try:
        # 先檢查數據庫連接
        from app.db.database import engine
        with engine.connect() as connection:
            logger.info("數據庫連接成功，開始初始化測試數據...")
        
        from app.db.init_test_data import init_test_data as run_init_test_data
        run_init_test_data()
        logger.info("測試數據初始化完成")
    except Exception as e:
        logger.warning(f"數據庫不可用或測試數據初始化失敗，跳過: {str(e)}")
        logger.info("應用將在無數據庫模式下運行")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    logger.info("應用啟動中...")
    run_database_migrations()
    init_test_data()
    # setup_rich_menu() 已被移除，因為新的 Handler 會在初始化時自動同步
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

# 添加靜態文件支持
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ziwei-frontend", "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"靜態文件服務已啟用，目錄: {static_dir}")
else:
    logger.warning(f"靜態文件目錄不存在: {static_dir}")

# 安全中間件設定
# 1. 信任的主機限制
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=ALLOWED_HOSTS + ["*"]  # 生產環境應移除 "*"
)

# 2. CORS 設定 - 限制來源
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 限制特定來源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 限制方法
    allow_headers=["*"],
    max_age=3600,  # 預檢請求快取時間
)

# 3. 速率限制中間件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 4. 請求大小限制中間件
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    """限制請求大小"""
    MAX_SIZE = 1024 * 1024 * 2  # 2MB 限制
    
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > MAX_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"請求大小超過限制 ({MAX_SIZE / 1024 / 1024}MB)"
                )
    
    response = await call_next(request)
    return response

# 5. 安全標頭中間件
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """添加安全標頭"""
    response = await call_next(request)
    
    # 安全標頭
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# 6. 安全檢查中間件
app.middleware("http")(security_check_middleware)

# API路由
app.include_router(routes.router, prefix="/api")
app.include_router(divination_routes.router)
app.include_router(time_divination_routes.router)
app.include_router(binding_routes.router, prefix="/api/binding")
app.include_router(permission_routes.router)
app.include_router(protected_routes.router, prefix="/api")
app.include_router(payment_routes.router, prefix="/api/payment")
app.include_router(chart_binding_routes.router, prefix="/api")
app.include_router(webhook.router)  # LINE Bot webhook at root path

@app.get("/")
@limiter.limit("10/minute")  # 首頁限制
def read_root(request: Request):
    return {"message": "Welcome to the Purple Star Astrology API"}

@app.get("/service")
@limiter.limit("10/minute")
async def service_page(request: Request):
    """星語引路人服務頁面"""
    from fastapi.responses import FileResponse
    service_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ziwei-frontend", "public", "service.html")
    if os.path.exists(service_file):
        return FileResponse(service_file, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="服務頁面未找到")

@app.get("/test-divination")
@limiter.limit("5/minute")  # 測試端點嚴格限制
async def test_divination(
    request: Request,
    db: Session = Depends(get_db),
    admin_key: str = None  # 添加管理員密鑰參數
):
    """測試特定時間的占卜結果（僅限管理員）"""
    try:
        # 安全檢查：需要管理員密鑰
        if admin_key != os.getenv("ADMIN_TEST_KEY", "your-admin-test-key"):
            raise HTTPException(status_code=403, detail="需要管理員權限")
        
        logger.info("開始執行占卜測試（管理員模式）")
        # 使用當前時間進行測試，而不是硬編碼的時間
        test_time = datetime.now()
        gender = "M"
        
        logger.info(f"測試參數 - 時間：{test_time}, 性別：{gender}")
        
        result = divination_logic.perform_divination(gender, test_time, db)
        logger.info("占卜測試完成")
        
        if result["success"]:
            # 驗證結果（只返回基本驗證資訊，不返回完整結果）
            basic_chart = result.get("basic_chart", {})
            ming_palace = next((palace for palace_name, palace in basic_chart.items() if palace_name == "命宮"), None)
            
            verification = {
                "測試成功": True,
                "分鐘地支": result.get("minute_dizhi"),
                "太極點命宮": result.get("taichi_palace"),
                "宮干": result.get("palace_tiangan"),
                "四化數量": len(result.get("sihua_results", []))
            }
            
            return {
                "success": True,
                "message": "測試成功",
                "verification": verification,
                "test_time": test_time.isoformat(),
                "note": "完整結果不在此顯示以保護演算法"
            }
        else:
            logger.error(f"占卜失敗：{result.get('error')}")
            raise HTTPException(status_code=500, detail="占卜測試失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"測試過程發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail="測試系統錯誤")
