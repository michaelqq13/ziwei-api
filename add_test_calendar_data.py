#!/usr/bin/env python3
"""
添加測試農曆數據腳本
用於快速添加當前日期附近的農曆數據，以便測試占卜功能
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.calendar import Base, CalendarData
from app.config.database_config import DatabaseConfig
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_test_calendar_data():
    """添加測試農曆數據"""
    try:
        # 獲取數據庫連接
        database_url = DatabaseConfig.get_database_url()
        engine = create_engine(database_url)
        
        # 創建表（如果不存在）
        Base.metadata.create_all(engine)
        
        # 創建會話
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 檢查是否已有數據
            existing_count = db.query(CalendarData).count()
            logger.info(f"數據庫中現有 {existing_count} 條農曆數據")
            
            # 添加當前日期及前後幾天的測試數據
            test_dates = []
            base_date = datetime.now()
            
            # 添加前後7天的數據
            for i in range(-7, 8):
                test_date = base_date + timedelta(days=i)
                test_dates.append(test_date)
            
            # 為每個日期添加24小時的數據
            calendar_data_list = []
            for test_date in test_dates:
                for hour in range(24):
                    # 檢查是否已存在該時間的數據
                    existing = db.query(CalendarData).filter(
                        CalendarData.gregorian_year == test_date.year,
                        CalendarData.gregorian_month == test_date.month,
                        CalendarData.gregorian_day == test_date.day,
                        CalendarData.gregorian_hour == hour
                    ).first()
                    
                    if not existing:
                        # 創建測試數據（這裡使用簡化的農曆數據）
                        calendar_data = CalendarData(
                            gregorian_datetime=datetime(test_date.year, test_date.month, test_date.day, hour, 0, 0),
                            gregorian_year=test_date.year,
                            gregorian_month=test_date.month,
                            gregorian_day=test_date.day,
                            gregorian_hour=hour,
                            lunar_year_in_chinese="乙巳年",
                            lunar_month_in_chinese="五月",
                            lunar_day_in_chinese="初七",
                            is_leap_month_in_chinese=False,
                            year_gan_zhi="乙巳",
                            month_gan_zhi="壬午",
                            day_gan_zhi="辛未",
                            hour_gan_zhi=get_hour_gan_zhi(hour),
                            solar_term_today=None,
                            solar_term_in_hour="夏至"
                        )
                        calendar_data_list.append(calendar_data)
            
            if calendar_data_list:
                # 批量添加數據
                db.add_all(calendar_data_list)
                db.commit()
                logger.info(f"成功添加 {len(calendar_data_list)} 條測試農曆數據")
            else:
                logger.info("所有測試日期的數據都已存在，無需添加")
                
            # 檢查最終數據量
            final_count = db.query(CalendarData).count()
            logger.info(f"數據庫中現有 {final_count} 條農曆數據")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"添加測試農曆數據失敗：{e}")
        raise

def get_hour_gan_zhi(hour):
    """獲取時辰干支（簡化版）"""
    # 簡化的時辰干支對照表
    hour_branches = {
        23: "子", 0: "子", 1: "丑", 2: "丑", 3: "寅", 4: "寅",
        5: "卯", 6: "卯", 7: "辰", 8: "辰", 9: "巳", 10: "巳",
        11: "午", 12: "午", 13: "未", 14: "未", 15: "申", 16: "申",
        17: "酉", 18: "酉", 19: "戌", 20: "戌", 21: "亥", 22: "亥"
    }
    
    branch = hour_branches.get(hour, "子")
    # 簡化：都使用甲干
    return f"甲{branch}"

if __name__ == "__main__":
    logger.info("開始添加測試農曆數據...")
    add_test_calendar_data()
    logger.info("測試農曆數據添加完成！") 