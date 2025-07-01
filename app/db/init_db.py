from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, DATABASE_URL
from app.models.calendar import CalendarData
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """初始化數據庫"""
    try:
        # 創建數據庫引擎
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        
        # 創建所有表格
        Base.metadata.create_all(bind=engine)
        
        # 創建會話
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 檢查是否已有數據
            existing_data = db.query(CalendarData).first()
            if not existing_data:
                logger.info("數據庫為空，開始初始化基礎數據...")
                # 這裡可以添加一些基礎數據
                
            logger.info("數據庫初始化完成")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"數據庫初始化失敗：{str(e)}")
        raise

if __name__ == "__main__":
    logger.info("開始初始化數據庫...")
    init_db()
    logger.info("數據庫初始化完成！") 