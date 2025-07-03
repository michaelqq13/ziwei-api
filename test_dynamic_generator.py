#!/usr/bin/env python3
"""
測試動態農曆數據生成器
"""
import sys
import os
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.database_config import DatabaseConfig
from app.utils.lunar_data_generator import get_or_create_lunar_data
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_dynamic_generator():
    """測試動態農曆數據生成器"""
    try:
        # 連接數據庫
        database_url = DatabaseConfig.get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("=== 動態農曆數據生成器測試 ===")
        
        # 測試目標日期：2025年7月3日下午1點
        target_date = datetime(2025, 7, 3, 13, 0, 0)
        print(f"測試目標日期：{target_date}")
        
        # 嘗試獲取或創建農曆數據
        print("開始獲取或創建農曆數據...")
        
        lunar_data = get_or_create_lunar_data(db, target_date)
        
        if lunar_data:
            print("✅ 成功獲取農曆數據！")
            print(f"   日期：{lunar_data.gregorian_year}-{lunar_data.gregorian_month}-{lunar_data.gregorian_day} {lunar_data.gregorian_hour}:00")
            print(f"   農曆年：{lunar_data.lunar_year_in_chinese}")
            print(f"   農曆月：{lunar_data.lunar_month_in_chinese}")
            print(f"   農曆日：{lunar_data.lunar_day_in_chinese}")
            print(f"   年干支：{lunar_data.year_gan_zhi}")
            print(f"   月干支：{lunar_data.month_gan_zhi}")
            print(f"   日干支：{lunar_data.day_gan_zhi}")
            print(f"   時干支：{lunar_data.hour_gan_zhi}")
            print(f"   節氣：{lunar_data.solar_term_today}")
        else:
            print("❌ 獲取農曆數據失敗")
            return False
        
        # 測試另一個日期
        print("\n=== 測試另一個日期 ===")
        target_date2 = datetime(2025, 7, 5, 10, 0, 0)
        print(f"測試目標日期：{target_date2}")
        
        lunar_data2 = get_or_create_lunar_data(db, target_date2)
        
        if lunar_data2:
            print("✅ 第二個日期也成功獲取農曆數據！")
            print(f"   日期：{lunar_data2.gregorian_year}-{lunar_data2.gregorian_month}-{lunar_data2.gregorian_day} {lunar_data2.gregorian_hour}:00")
            print(f"   日干支：{lunar_data2.day_gan_zhi}")
            print(f"   時干支：{lunar_data2.hour_gan_zhi}")
        else:
            print("❌ 第二個日期獲取農曆數據失敗")
            return False
        
        db.close()
        
        print("\n🎉 動態農曆數據生成器測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dynamic_generator()
    sys.exit(0 if success else 1) 