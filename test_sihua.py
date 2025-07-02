#!/usr/bin/env python3
"""
四化計算測試腳本
用於驗證四化星是否正確計算和分配
"""

import os
import sys
from datetime import datetime
from dateutil import parser

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.logic.star_calculator import StarCalculator
from app.logic.purple_star_chart import PurpleStarChart
from app.db.database import SessionLocal

def test_four_transformations():
    """測試四化計算"""
    print("=" * 50)
    print("四化計算測試")
    print("=" * 50)
    
    # 測試資料
    birth_time = parser.parse('1995-02-15T10:30:00+08:00')
    name = "測試用戶"
    gender = "M"
    
    print(f"測試資料：")
    print(f"姓名：{name}")
    print(f"性別：{gender}")
    print(f"生辰：{birth_time}")
    print()
    
    # 創建數據庫會話
    db = SessionLocal()
    
    try:
        # 創建紫微斗數命盤 - 修正參數順序
        chart = PurpleStarChart(
            year=birth_time.year,
            month=birth_time.month,
            day=birth_time.day,
            hour=birth_time.hour,
            minute=birth_time.minute,
            gender=gender,
            db=db
        )
        
        # 獲取命盤資料
        chart_data = chart.get_chart()
        
        print("=" * 30)
        print("生年天干四化對照")
        print("=" * 30)
        
        # 獲取生年天干
        birth_info = chart_data.get("birth_info", {})
        year_stem = birth_info.get("year_stem", "未知")
        print(f"生年天干：{year_stem}")
        
        # 獲取四化對照
        star_calculator = StarCalculator()
        if year_stem in star_calculator.FOUR_TRANSFORMATIONS:
            transformations = star_calculator.FOUR_TRANSFORMATIONS[year_stem]
            print(f"該年干的四化：")
            for trans_type, star_name in transformations.items():
                print(f"  {trans_type}：{star_name}")
        else:
            print(f"找不到年干 {year_stem} 的四化對照")
        
        print()
        print("=" * 30)
        print("命盤中的星曜分佈")
        print("=" * 30)
        
        palaces = chart_data.get("palaces", {})
        for palace_name, palace_info in palaces.items():
            stars = palace_info.get("stars", [])
            if stars:
                print(f"【{palace_name}】{palace_info.get('dizhi', '未知')}：{', '.join(stars)}")
        
        print()
        print("=" * 30)
        print("四化星搜尋結果")
        print("=" * 30)
        
        # 檢查每個四化星是否在命盤中
        if year_stem in star_calculator.FOUR_TRANSFORMATIONS:
            transformations = star_calculator.FOUR_TRANSFORMATIONS[year_stem]
            for trans_type, star_name in transformations.items():
                found = False
                found_in_palace = "未找到"
                
                for palace_name, palace_info in palaces.items():
                    stars = palace_info.get("stars", [])
                    for star in stars:
                        clean_star_name = star.split("（")[0] if "（" in star else star
                        clean_star_name = clean_star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "").strip()
                        
                        if clean_star_name == star_name:
                            found = True
                            found_in_palace = palace_name
                            break
                    if found:
                        break
                
                status = "✅ 找到" if found else "❌ 未找到"
                print(f"{star_name}化{trans_type}：{status} (在 {found_in_palace})")
        
        print()
        print("=" * 30)
        print("應用四化後的命盤")
        print("=" * 30)
        
        # 重新獲取應用四化後的命盤
        chart_data_with_sihua = chart.get_chart()
        palaces_with_sihua = chart_data_with_sihua.get("palaces", {})
        
        sihua_count = 0
        for palace_name, palace_info in palaces_with_sihua.items():
            stars = palace_info.get("stars", [])
            sihua_stars = [star for star in stars if any(marker in star for marker in ["化祿", "化權", "化科", "化忌"])]
            if sihua_stars:
                print(f"【{palace_name}】：{', '.join(sihua_stars)}")
                sihua_count += len(sihua_stars)
        
        print()
        print(f"總共找到 {sihua_count} 個四化星")
        if sihua_count == 4:
            print("✅ 四化星數量正確")
        else:
            print("❌ 四化星數量不正確，應該是 4 個")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_four_transformations() 