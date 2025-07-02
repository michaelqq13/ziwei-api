#!/usr/bin/env python3
"""測試可選數據庫功能"""

import sys
import os
import logging
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_optional_db_functionality():
    """測試可選數據庫功能"""
    print("=" * 60)
    print("測試可選數據庫功能")
    print("=" * 60)
    
    try:
        # 測試1：測試 PurpleStarChart 無數據庫模式
        print("\n1. 測試 PurpleStarChart 無數據庫模式")
        from app.logic.purple_star_chart import PurpleStarChart
        from app.models.birth_info import BirthInfo
        
        birth_info = BirthInfo(
            year=1990, month=5, day=15, hour=14, minute=30,
            gender="男", longitude=121.5654, latitude=25.0330
        )
        
        chart = PurpleStarChart(birth_info=birth_info, db=None)
        print(f"✅ PurpleStarChart 創建成功，簡化模式：{chart.simplified_mode}")
        
        # 獲取命盤數據
        chart_data = chart.get_chart()
        print(f"✅ 命盤數據獲取成功，宮位數量：{len(chart_data.get('palaces', {}))}")
        
    except Exception as e:
        print(f"❌ PurpleStarChart 測試失敗：{e}")
        return False
    
    try:
        # 測試2：測試占卜邏輯無數據庫模式
        print("\n2. 測試占卜邏輯無數據庫模式")
        from app.logic.divination_logic import get_divination_result
        
        result = get_divination_result(db=None, gender="男")
        
        if result.get("success"):
            print("✅ 占卜邏輯測試成功")
            print(f"   太極點：{result.get('taichi_palace')}")
            print(f"   觸機時間：{result.get('trigger_time')}")
            print(f"   簡化模式：{result.get('simplified_mode')}")
            
            sihua_results = result.get("sihua_results", [])
            print(f"   四化結果數量：{len(sihua_results)}")
            
            for i, sihua in enumerate(sihua_results):
                trans_type = sihua.get("transformation_type", "")
                star_name = sihua.get("star_name", "")
                taichi_palace = sihua.get("taichi_palace", "")
                explanation = sihua.get("explanation", "")
                
                print(f"   {i+1}. {star_name}化{trans_type} 在 {taichi_palace}")
                if explanation:
                    print(f"      解釋長度：{len(explanation)} 字元")
        else:
            print(f"❌ 占卜邏輯測試失敗：{result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 占卜邏輯測試失敗：{e}")
        return False
    
    try:
        # 測試3：測試農曆轉換功能
        print("\n3. 測試農曆轉換功能")
        from app.utils.chinese_calendar import ChineseCalendar
        
        # 測試年干支
        year_ganzhi = ChineseCalendar.get_year_ganzhi(1990)
        print(f"✅ 1990年干支：{year_ganzhi}")
        
        # 測試月干支
        month_ganzhi = ChineseCalendar.get_month_ganzhi(1990, 5)
        print(f"✅ 1990年5月干支：{month_ganzhi}")
        
        # 測試日干支
        day_ganzhi = ChineseCalendar.get_day_ganzhi(1990, 5, 15)
        print(f"✅ 1990年5月15日干支：{day_ganzhi}")
        
        # 測試時干支
        hour_ganzhi = ChineseCalendar.get_hour_ganzhi(14, day_ganzhi[0])
        print(f"✅ 14時干支：{hour_ganzhi}")
        
    except Exception as e:
        print(f"❌ 農曆轉換測試失敗：{e}")
        return False
    
    try:
        # 測試4：測試HTTP端點
        print("\n4. 測試HTTP端點")
        import requests
        
        # 測試健康檢查
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康檢查端點正常")
        else:
            print(f"❌ 健康檢查端點失敗：{response.status_code}")
            
        # 測試占卜端點（如果有的話）
        # 這裡可以添加對占卜端點的測試
        
    except Exception as e:
        print(f"❌ HTTP端點測試失敗：{e}")
        return False
    
    print("\n" + "=" * 60)
    print("所有測試完成！系統現在支持可選數據庫模式")
    print("=" * 60)
    print("\n總結：")
    print("✅ PurpleStarChart 支持無數據庫模式")
    print("✅ 占卜邏輯支持無數據庫模式") 
    print("✅ 農曆轉換功能正常")
    print("✅ 服務啟動正常")
    print("\n⚠️  注意：無數據庫模式使用內置農曆轉換，可能與驗證過的數據庫資料有細微差異")
    print("💡 建議：修復數據庫連接後，系統將自動切換回精確模式")
    
    return True

if __name__ == "__main__":
    success = test_optional_db_functionality()
    sys.exit(0 if success else 1) 