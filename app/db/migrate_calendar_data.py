import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.calendar import Base, CalendarData
import os
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_calendar_data():
    # 建立 PostgreSQL 資料庫連接
    DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/ziwei'
    engine = create_engine(DATABASE_URL)
    
    # 創建資料表
    Base.metadata.create_all(engine)
    
    # 建立 session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 檢查現有數據
        existing_count = session.query(CalendarData).count()
        logger.info(f"現有記錄數: {existing_count}")
        
        # 如果已有大量數據，詢問是否要重新導入
        if existing_count > 1000:
            response = input(f"數據庫中已有 {existing_count} 筆記錄，是否要清空重新導入？(y/N): ")
            if response.lower() == 'y':
                logger.info("正在清空現有數據...")
                session.query(CalendarData).delete()
                session.commit()
                logger.info("現有數據已清空")
            else:
                logger.info("保留現有數據，結束導入")
                return
        
        # 讀取 CSV 檔案
        csv_path = '/Users/chenhsuanming/purple_star_calendar/calendar_data_1900-2100.csv'
        logger.info(f"開始讀取 CSV 檔案: {csv_path}")
        
        # 使用 chunking 來處理大文件
        chunk_size = 10000
        chunk_count = 0
        total_inserted = 0
        
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            chunk_count += 1
            logger.info(f"處理第 {chunk_count} 個批次，記錄數: {len(chunk)}")
            
            # 準備批量插入的數據
            calendar_objects = []
            
            for _, row in chunk.iterrows():
                try:
                    calendar_data = CalendarData(
                        gregorian_datetime=pd.to_datetime(row['gregorian_datetime']),
                        gregorian_year=int(row['gregorian_year']),
                        gregorian_month=int(row['gregorian_month']),
                        gregorian_day=int(row['gregorian_day']),
                        gregorian_hour=int(row['gregorian_hour']),
                        lunar_year_in_chinese=str(row['lunar_year_in_chinese']),
                        lunar_month_in_chinese=str(row['lunar_month_in_chinese']),
                        lunar_day_in_chinese=str(row['lunar_day_in_chinese']),
                        is_leap_month_in_chinese=row['is_leap_month_in_chinese'] == '是',
                        year_gan_zhi=str(row['year_gan_zhi']),
                        month_gan_zhi=str(row['month_gan_zhi']),
                        day_gan_zhi=str(row['day_gan_zhi']),
                        hour_gan_zhi=str(row['hour_gan_zhi']),
                        solar_term_today=str(row['solar_term_today']) if pd.notna(row['solar_term_today']) else None,
                        solar_term_in_hour=str(row['solar_term_in_hour']) if pd.notna(row['solar_term_in_hour']) else None
                    )
                    calendar_objects.append(calendar_data)
                except Exception as e:
                    logger.error(f"處理行數據時發生錯誤: {e}")
                    continue
            
            # 批量插入
            try:
                session.add_all(calendar_objects)
                session.commit()
                total_inserted += len(calendar_objects)
                logger.info(f"第 {chunk_count} 個批次插入成功，已插入總數: {total_inserted}")
            except Exception as e:
                logger.error(f"批量插入失敗: {e}")
                session.rollback()
                continue
        
        logger.info(f"數據導入完成！總共插入 {total_inserted} 筆記錄")
        
    except Exception as e:
        logger.error(f"數據導入過程發生錯誤: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    migrate_calendar_data() 