#!/usr/bin/env python3
"""
Railway 農曆數據初始化腳本
為 Railway 數據庫添加測試用的農曆數據
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到 Python 路徑
sys.path.append('/app')

from app.models.calendar import CalendarData
from app.config.database_config import DatabaseConfig

def get_database_url():
    """獲取數據庫連接URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL 環境變量未設置")
    
    # 修正 postgres:// 為 postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return database_url

def init_railway_calendar_data():
    """初始化 Railway 農曆數據"""
    try:
        # 連接數據庫
        database_url = get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("開始初始化 Railway 農曆數據...")
        
        # 檢查現有記錄數量
        existing_count = db.query(CalendarData).count()
        print(f"現有記錄數量: {existing_count}")
        
        # 定義要添加的日期範圍（2025年7月1日到7月31日）
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 31)
        
        # 天干地支循環
        heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 2025年乙巳年的基礎設定
        year_gan_zhi = "乙巳"
        
        # 計算從年初到7月1日的天數，用於計算日干支
        year_start = datetime(2025, 1, 1)
        days_from_year_start = (start_date - year_start).days
        
        # 2025年1月1日的日干支假設為甲子（可以根據實際情況調整）
        base_day_gan_index = 0  # 甲
        base_day_zhi_index = 0  # 子
        
        current_date = start_date
        added_count = 0
        
        while current_date <= end_date:
            # 計算當前日期的農曆信息
            lunar_month = 5  # 假設7月對應農曆5月
            lunar_day = current_date.day
            
            # 計算日干支
            day_offset = (current_date - start_date).days + days_from_year_start
            day_gan_index = (base_day_gan_index + day_offset) % 10
            day_zhi_index = (base_day_zhi_index + day_offset) % 12
            day_gan_zhi = heavenly_stems[day_gan_index] + earthly_branches[day_zhi_index]
            
            # 計算月干支（簡化版本）
            month_gan_index = (day_gan_index + current_date.month - 1) % 10
            month_zhi_index = (current_date.month - 1) % 12
            month_gan_zhi = heavenly_stems[month_gan_index] + earthly_branches[month_zhi_index]
            
            # 為每一天的每個小時創建記錄
            for hour in range(24):
                # 檢查是否已存在該記錄
                existing = db.query(CalendarData).filter(
                    CalendarData.gregorian_year == current_date.year,
                    CalendarData.gregorian_month == current_date.month,
                    CalendarData.gregorian_day == current_date.day,
                    CalendarData.gregorian_hour == hour
                ).first()
                
                if existing:
                    continue
                
                # 計算時干支
                hour_zhi_index = (hour // 2) % 12
                hour_gan_index = (day_gan_index * 2 + hour_zhi_index) % 10
                hour_gan_zhi = heavenly_stems[hour_gan_index] + earthly_branches[hour_zhi_index]
                
                # 創建新的農曆數據記錄
                calendar_data = CalendarData(
                    gregorian_year=current_date.year,
                    gregorian_month=current_date.month,
                    gregorian_day=current_date.day,
                    gregorian_hour=hour,
                    gregorian_minute=0,
                    lunar_year_in_chinese=f"乙巳年",
                    lunar_month_in_chinese=f"五月",
                    lunar_day_in_chinese=f"{lunar_day}日" if lunar_day <= 30 else f"{lunar_day-30}日",
                    year_gan_zhi=year_gan_zhi,
                    month_gan_zhi=month_gan_zhi,
                    day_gan_zhi=day_gan_zhi,
                    hour_gan_zhi=hour_gan_zhi,
                    solar_term="",
                    is_leap_month=False,
                    julian_day=0,
                    week_day=current_date.weekday(),
                    constellation="",
                    lunar_year_animal="蛇",
                    lunar_month_animal="",
                    lunar_day_animal="",
                    lunar_hour_animal="",
                    gan_zhi_60_day=0,
                    gan_zhi_60_year=0,
                    lunar_season="夏",
                    lunar_season_name="",
                    solar_term_name="",
                    solar_term_date="",
                    lunar_calendar_name="",
                    lunar_calendar_year=2025,
                    lunar_calendar_month=5,
                    lunar_calendar_day=lunar_day if lunar_day <= 30 else lunar_day-30,
                    lunar_calendar_hour=hour,
                    lunar_calendar_minute=0,
                    lunar_calendar_second=0,
                    lunar_calendar_millisecond=0
                )
                
                db.add(calendar_data)
                added_count += 1
                
                # 每100筆記錄提交一次
                if added_count % 100 == 0:
                    db.commit()
                    print(f"已添加 {added_count} 筆記錄...")
            
            current_date += timedelta(days=1)
        
        # 最終提交
        db.commit()
        
        # 檢查最終記錄數量
        final_count = db.query(CalendarData).count()
        print(f"初始化完成！")
        print(f"添加了 {added_count} 筆新記錄")
        print(f"數據庫總記錄數: {final_count}")
        
        # 驗證特定日期的記錄
        test_record = db.query(CalendarData).filter(
            CalendarData.gregorian_year == 2025,
            CalendarData.gregorian_month == 7,
            CalendarData.gregorian_day == 3,
            CalendarData.gregorian_hour == 13
        ).first()
        
        if test_record:
            print(f"✅ 驗證成功: 2025-7-3 13:00 的記錄存在")
            print(f"   日干支: {test_record.day_gan_zhi}")
            print(f"   時干支: {test_record.hour_gan_zhi}")
        else:
            print("❌ 驗證失敗: 找不到 2025-7-3 13:00 的記錄")
        
        db.close()
        
    except Exception as e:
        print(f"初始化失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_railway_calendar_data() 