from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database_config import DatabaseConfig
from app.models.calendar import Base, CalendarData
from datetime import datetime
import logging
import pandas as pd
import os

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_test_data(limit_rows=None):
    """初始化完整的時間數據
    
    Args:
        limit_rows: 限制導入的行數，用於測試（None = 導入全部）
    """
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
            existing_count = db.query(CalendarData).count()
            
            # 如果沒有數據或數據量很少，則導入完整數據
            if existing_count < 100:  # 少於100條記錄表示需要導入完整數據
                logger.info(f"數據庫中只有 {existing_count} 條記錄，開始導入完整的時間數據...")
                
                # 嘗試從完整的 CSV 文件導入數據
                csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'calendar_data_current.csv')
                
                if os.path.exists(csv_path):
                    logger.info(f"找到當前年份的 CSV 文件: {csv_path}")
                    logger.info("開始導入當前年份的時間數據...")
                    
                    # 讀取 CSV 文件並導入數據
                    df = pd.read_csv(csv_path)
                    if limit_rows:
                        df = df.head(limit_rows)
                        logger.info(f"限制導入前 {limit_rows} 行數據進行測試")
                    
                    logger.info(f"CSV 文件共有 {len(df)} 條記錄，開始批量導入...")
                    
                    # 批量導入數據（每次1000條）
                    batch_size = 1000
                    for i in range(0, len(df), batch_size):
                        batch_df = df.iloc[i:i+batch_size]
                        calendar_data_list = []
                        
                        for _, row in batch_df.iterrows():
                            calendar_data = CalendarData(
                                gregorian_datetime=pd.to_datetime(row['gregorian_datetime']),
                                gregorian_year=row['gregorian_year'],
                                gregorian_month=row['gregorian_month'],
                                gregorian_day=row['gregorian_day'],
                                gregorian_hour=row['gregorian_hour'],
                                lunar_year_in_chinese=row['lunar_year_in_chinese'],
                                lunar_month_in_chinese=row['lunar_month_in_chinese'],
                                lunar_day_in_chinese=row['lunar_day_in_chinese'],
                                is_leap_month_in_chinese=row['is_leap_month_in_chinese'] == '是',
                                year_gan_zhi=row['year_gan_zhi'],
                                month_gan_zhi=row['month_gan_zhi'],
                                day_gan_zhi=row['day_gan_zhi'],
                                hour_gan_zhi=row['hour_gan_zhi'],
                                solar_term_today=row['solar_term_today'] if pd.notna(row['solar_term_today']) else None,
                                solar_term_in_hour=row['solar_term_in_hour'] if pd.notna(row['solar_term_in_hour']) else None
                            )
                            calendar_data_list.append(calendar_data)
                        
                        # 批量添加
                        db.add_all(calendar_data_list)
                        db.commit()
                        
                        if limit_rows:
                            logger.info(f"測試模式：已導入 {min(i + batch_size, len(df))} / {len(df)} 條記錄")
                        else:
                            logger.info(f"已導入 {min(i + batch_size, len(df))} / {len(df)} 條記錄")
                    
                    final_count = db.query(CalendarData).count()
                    logger.info(f"當前年份數據導入完成，共導入 {final_count} 條記錄")
                else:
                    logger.warning(f"找不到當前年份的 CSV 文件: {csv_path}")
                    logger.info("改為導入基本測試數據...")
                    
                    # 如果找不到完整文件，則添加基本測試數據（當前時間附近）
                    test_data_list = []
                    
                    # 2025年7月1日 - 當前日期
                    for hour in range(0, 24, 2):  # 每2小時一條記錄
                        calendar_data = CalendarData(
                            gregorian_datetime=datetime(2025, 7, 1, hour, 0, 0),
                            gregorian_year=2025,
                            gregorian_month=7,
                            gregorian_day=1,
                            gregorian_hour=hour,
                            lunar_year_in_chinese="乙巳",
                            lunar_month_in_chinese="六月",
                            lunar_day_in_chinese="初七",
                            is_leap_month_in_chinese=False,
                            year_gan_zhi="乙巳",
                            month_gan_zhi="壬午",
                            day_gan_zhi="辛未",
                            hour_gan_zhi="戊子",
                            solar_term_today=None,
                            solar_term_in_hour="夏至"
                        )
                        test_data_list.append(calendar_data)
                    
                    # 2025年7月2日
                    for hour in range(0, 24, 2):
                        calendar_data = CalendarData(
                            gregorian_datetime=datetime(2025, 7, 2, hour, 0, 0),
                            gregorian_year=2025,
                            gregorian_month=7,
                            gregorian_day=2,
                            gregorian_hour=hour,
                            lunar_year_in_chinese="乙巳",
                            lunar_month_in_chinese="六月",
                            lunar_day_in_chinese="初八",
                            is_leap_month_in_chinese=False,
                            year_gan_zhi="乙巳",
                            month_gan_zhi="壬午",
                            day_gan_zhi="壬申",
                            hour_gan_zhi="庚子",
                            solar_term_today=None,
                            solar_term_in_hour="夏至"
                        )
                        test_data_list.append(calendar_data)
                    
                    db.add_all(test_data_list)
                    db.commit()
                    logger.info(f"基本測試數據導入完成，共 {len(test_data_list)} 條記錄")
            else:
                logger.info(f"數據庫中已有 {existing_count} 條記錄，跳過數據導入")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"初始化數據失敗：{e}")
        raise e

if __name__ == "__main__":
    logger.info("開始初始化時間數據...")
    init_test_data()
    logger.info("時間數據初始化完成！") 