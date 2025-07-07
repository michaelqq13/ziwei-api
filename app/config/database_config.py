"""
數據庫配置
"""
import os
from typing import Optional

class DatabaseConfig:
    """數據庫配置類"""
    
    # 獲取數據庫 URL
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # 如果沒有設置 DATABASE_URL，使用默認的本地 SQLite
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///./ziwei.db"
    
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
    
    @classmethod
    def get_database_url(cls):
        """動態獲取數據庫 URL（用於調試）"""
        url = os.getenv("DATABASE_URL")
        if not url:
            return "sqlite:///./ziwei.db"
        
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        return url 