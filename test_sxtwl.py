#!/usr/bin/env python3
"""
測試 sxtwl 庫的可用性
"""

print("開始測試 sxtwl 庫...")

try:
    import sxtwl
    print("✅ sxtwl 庫導入成功")
    
    # 測試基本功能
    day_obj = sxtwl.fromSolar(2025, 7, 28)
    print(f"✅ 基本功能測試成功，農曆年: {day_obj.getLunarYear()}")
    
    print("✅ sxtwl 庫完全可用")
    
except ImportError as e:
    print(f"❌ sxtwl 庫導入失敗: {e}")
    print("請運行: pip install sxtwl")
    
except Exception as e:
    print(f"❌ sxtwl 庫運行錯誤: {e}")
    
print("測試完成") 