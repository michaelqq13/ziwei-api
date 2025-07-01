import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.calendar import Base, CalendarData
import os

def migrate_calendar_data():
    # 建立資料庫連接
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///calendar.db')
    engine = create_engine(DATABASE_URL)
    
    # 創建資料表
    Base.metadata.create_all(engine)
    
    # 建立 session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 讀取 CSV 檔案
    csv_path = '/Users/chenhsuanming/purple_star_calendar/calendar_data_1900-2100.csv'
    df = pd.read_csv(csv_path)
    
    # 轉換資料並寫入資料庫
    for _, row in df.iterrows():
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
            solar_term_today=row['solar_term_today'],
            solar_term_in_hour=row['solar_term_in_hour']
        )
        session.add(calendar_data)
    
    # 提交變更
    session.commit()
    session.close()

if __name__ == '__main__':
    migrate_calendar_data() 