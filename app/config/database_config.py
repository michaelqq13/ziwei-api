"""
數據庫配置
"""
import os
from typing import Optional

class DatabaseConfig:
    """數據庫配置類"""
    
    # 獲取數據庫 URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/ziwei"  # 默認使用 PostgreSQL
    )
    
    # 如果是 Railway 提供的 DATABASE_URL，需要替換掉 "postgres://" 為 "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # 數據庫連接池配置
    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    # 是否顯示 SQL 語句（調試用）
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true" 