#!/usr/bin/env python3
"""
Railway 部署農曆數據初始化腳本
專門用於在 Railway 上初始化農曆數據
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """獲取數據庫連接 URL"""
    url = os.getenv("DATABASE_URL")
    if not url:
        logger.error("未找到 DATABASE_URL 環境變數")
        return None
    
    # 如果是 Railway 提供的 DATABASE_URL，需要替換掉 "postgres://" 為 "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        logger.info("已將 postgres:// 替換為 postgresql://")
    
    return url

def init_railway_calendar_data():
    """初始化 Railway 上的農曆數據"""
    try:
        # 獲取數據庫連接
        database_url = get_database_url()
        if not database_url:
            logger.error("無法獲取數據庫連接")
            return False
            
        logger.info(f"連接到數據庫: {database_url[:50]}...")
        
        # 創建數據庫引擎
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # 導入必要的模型
        from app.models.calendar_data import CalendarData, Base
        
        # 創建表格（如果不存在）
        Base.metadata.create_all(engine)
        logger.info("數據庫表格創建完成")
        
        # 創建會話
        db = SessionLocal()
        
        try:
            # 檢查現有數據
            existing_count = db.query(CalendarData).count()
            logger.info(f"數據庫中現有 {existing_count} 條農曆數據")
            
            # 檢查是否有當前日期的數據
            today = datetime.now()
            current_date_records = db.query(CalendarData).filter(
                CalendarData.gregorian_year == today.year,
                CalendarData.gregorian_month == today.month,
                CalendarData.gregorian_day == today.day
            ).count()
            
            logger.info(f"今日 ({today.year}-{today.month}-{today.day}) 的記錄數: {current_date_records}")
            
            # 如果沒有足夠的數據，添加基本測試數據
            if existing_count < 1000:  # 如果數據不足1000條
                logger.info("數據不足，開始添加基本農曆數據...")
                
                # 添加當前日期前後7天的數據
                base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                calendar_data_list = []
                
                for day_offset in range(-7, 8):  # 前後7天
                    target_date = base_date + timedelta(days=day_offset)
                    
                    # 每天添加幾個關鍵時辰的數據
                    for hour in [0, 6, 12, 18]:  # 子時、卯時、午時、酉時
                        calendar_data = CalendarData(
                            gregorian_datetime=target_date.replace(hour=hour),
                            gregorian_year=target_date.year,
                            gregorian_month=target_date.month,
                            gregorian_day=target_date.day,
                            gregorian_hour=hour,
                            lunar_year_in_chinese="二〇二五",
                            lunar_month_in_chinese="六月",
                            lunar_day_in_chinese=f"初{abs(day_offset) + 1}",
                            is_leap_month_in_chinese=False,
                            year_gan_zhi="乙巳",
                            month_gan_zhi="壬午",
                            day_gan_zhi="癸酉",
                            hour_gan_zhi="甲子",
                            solar_term_today=None,
                            solar_term_in_hour="夏至"
                        )
                        calendar_data_list.append(calendar_data)
                
                # 批量添加數據
                db.add_all(calendar_data_list)
                db.commit()
                
                final_count = db.query(CalendarData).count()
                logger.info(f"農曆數據添加完成，總共 {final_count} 條記錄")
                
            else:
                logger.info("農曆數據充足，無需添加")
            
            # 驗證關鍵日期的數據
            test_dates = [
                datetime(2025, 7, 1),
                datetime(2025, 7, 2),
                datetime(2025, 7, 3),
                datetime(2025, 7, 4),
                datetime(2025, 7, 5)
            ]
            
            for test_date in test_dates:
                count = db.query(CalendarData).filter(
                    CalendarData.gregorian_year == test_date.year,
                    CalendarData.gregorian_month == test_date.month,
                    CalendarData.gregorian_day == test_date.day
                ).count()
                logger.info(f"日期 {test_date.year}-{test_date.month}-{test_date.day} 的記錄數: {count}")
            
            return True
            
        except Exception as e:
            logger.error(f"數據庫操作失敗: {e}")
            db.rollback()
            return False
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"初始化農曆數據失敗: {e}")
        return False

if __name__ == "__main__":
    logger.info("開始初始化 Railway 農曆數據...")
    
    success = init_railway_calendar_data()
    
    if success:
        logger.info("✅ Railway 農曆數據初始化成功")
        sys.exit(0)
    else:
        logger.error("❌ Railway 農曆數據初始化失敗")
        sys.exit(1) 