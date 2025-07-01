from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database_config import DatabaseConfig
from app.models.calendar_data import Base, CalendarData
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_test_data():
    """初始化測試數據"""
    try:
        # 使用正確的數據庫配置
        database_url = DatabaseConfig.get_database_url()
        logger.info(f"使用數據庫URL: {database_url[:50]}...")
        
        # 創建數據庫引擎
        engine = create_engine(database_url)
        
        # 創建會話
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 檢查是否已有數據
            existing_data = db.query(CalendarData).first()
            if not existing_data:
                logger.info("數據庫為空，開始添加測試數據...")
                
                # 添加更多測試數據，涵蓋常用的日期
                test_data_list = [
                    # 2025年6月30日 - 原始測試數據
                    CalendarData(
                        gregorian_datetime=datetime(2025, 6, 30, 22, 51, 0),
                        gregorian_year=2025,
                        gregorian_month=6,
                        gregorian_day=30,
                        gregorian_hour=22,
                        lunar_year_in_chinese="乙巳",
                        lunar_month_in_chinese="五月",
                        lunar_day_in_chinese="廿四",
                        is_leap_month_in_chinese=False,
                        year_gan_zhi="乙巳",
                        month_gan_zhi="壬午",
                        day_gan_zhi="丁未",
                        hour_gan_zhi="辛亥",
                        minute_gan_zhi="辛亥"
                    ),
                    # 2024年12月20日 - 今天的日期
                    CalendarData(
                        gregorian_datetime=datetime(2024, 12, 20, 12, 0, 0),
                        gregorian_year=2024,
                        gregorian_month=12,
                        gregorian_day=20,
                        gregorian_hour=12,
                        lunar_year_in_chinese="甲辰",
                        lunar_month_in_chinese="十一月",
                        lunar_day_in_chinese="二十",
                        is_leap_month_in_chinese=False,
                        year_gan_zhi="甲辰",
                        month_gan_zhi="丙子",
                        day_gan_zhi="乙亥",
                        hour_gan_zhi="壬午",
                        minute_gan_zhi="壬午"
                    ),
                    # 2024年1月1日 - 新年
                    CalendarData(
                        gregorian_datetime=datetime(2024, 1, 1, 0, 0, 0),
                        gregorian_year=2024,
                        gregorian_month=1,
                        gregorian_day=1,
                        gregorian_hour=0,
                        lunar_year_in_chinese="癸卯",
                        lunar_month_in_chinese="十一月",
                        lunar_day_in_chinese="二十",
                        is_leap_month_in_chinese=False,
                        year_gan_zhi="癸卯",
                        month_gan_zhi="甲子",
                        day_gan_zhi="甲午",
                        hour_gan_zhi="甲子",
                        minute_gan_zhi="甲子"
                    )
                ]
                
                for test_data in test_data_list:
                    db.add(test_data)
                
                db.commit()
                logger.info(f"測試數據添加完成，共添加 {len(test_data_list)} 條記錄")
            else:
                logger.info("數據庫已有數據，跳過初始化")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"初始化測試數據失敗：{str(e)}")
        # 不拋出異常，讓應用繼續啟動

if __name__ == "__main__":
    logger.info("開始初始化測試數據...")
    init_test_data()
    logger.info("測試數據初始化完成！") 