"""
數據庫連接配置
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 設置日誌
logger = logging.getLogger(__name__)

# 動態獲取數據庫 URL
def get_database_url():
    """動態獲取數據庫 URL"""
    url = os.getenv("DATABASE_URL")
    if not url:
        logger.warning("未找到 DATABASE_URL 環境變數，使用默認本地連接")
        return "postgresql://postgres:postgres@localhost:5432/ziwei"
    
    logger.info(f"找到 DATABASE_URL: {url[:50]}...")  # 只顯示前50個字符以保護敏感信息
    
    # 如果是 Railway 提供的 DATABASE_URL，需要替換掉 "postgres://" 為 "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        logger.info("已將 postgres:// 替換為 postgresql://")
    
    return url

# 獲取數據庫 URL
DATABASE_URL = get_database_url()

# 創建數據庫引擎
logger.info("正在創建數據庫引擎...")
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    echo=os.getenv("ECHO_SQL", "false").lower() == "true"
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建基礎模型類
Base = declarative_base()

# 依賴注入函數
def get_db():
    """獲取數據庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 