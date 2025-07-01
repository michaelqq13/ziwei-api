from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, DATABASE_URL
from app.models.calendar import CalendarData
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_test_data():
    """初始化測試數據"""
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
                logger.info("數據庫為空，開始添加測試數據...")
                
                # 添加測試數據（2025年6月30日）
                test_data = CalendarData(
                    gregorian_datetime="2025-06-30 22:51:00",
                    gregorian_year=2025,
                    gregorian_month=6,
                    gregorian_day=30,
                    gregorian_hour=22,
                    lunar_year_in_chinese="乙巳",
                    lunar_month_in_chinese="五月",
                    lunar_day_in_chinese="廿四",
                    is_leap_month_in_chinese=False,
                    year_gan_zhi="乙巳",
                    month_gan_zhi="丙午",
                    day_gan_zhi="丁未",
                    hour_gan_zhi="辛亥",
                    minute_gan_zhi="辛亥"
                )
                
                db.add(test_data)
                db.commit()
                logger.info("測試數據添加完成")
            else:
                logger.info("數據庫已有數據，跳過初始化")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"初始化測試數據失敗：{str(e)}")
        raise

if __name__ == "__main__":
    logger.info("開始初始化測試數據...")
    init_test_data()
    logger.info("測試數據初始化完成！") 