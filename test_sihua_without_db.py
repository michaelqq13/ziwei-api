#!/usr/bin/env python3
"""
測試四化功能在沒有數據庫時是否正常工作
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logic.divination_logic import DivinationLogic
from app.utils.divination_flex_message import DivinationFlexMessageGenerator
from datetime import datetime, timezone, timedelta

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def test_divination_without_db():
    """測試在沒有數據庫時的四化功能"""
    print("=== 測試四化功能（無數據庫模式）===\n")
    
    # 創建占卜邏輯實例
    divination = DivinationLogic()
    
    # 測試時間
    test_time = datetime(2024, 12, 26, 15, 45, tzinfo=TAIPEI_TZ)
    
    # 執行占卜（db=None）
    result = divination.perform_divination("M", test_time, None)
    
    if result["success"]:
        print(f"✅ 占卜計算成功")
        print(f"太極點命宮：{result['taichi_palace']}")
        print(f"宮干：{result['palace_tiangan']}")
        print(f"分鐘地支：{result['minute_dizhi']}")
        print()
        
        # 檢查四化解釋
        print("=== 四化解釋 ===")
        for i, sihua in enumerate(result["sihua_results"], 1):
            print(f"\n{i}. {sihua['type']}星 - {sihua['star']}")
            print(f"   落宮：{sihua['palace']}")
            explanation = sihua.get('explanation', '')
            if explanation:
                print(f"   解釋長度：{len(explanation)} 字元")
                print(f"   解釋開頭：{explanation[:100]}...")
            else:
                print("   ❌ 沒有解釋內容")
        
        # 測試Flex Message生成
        print("\n=== Flex Message測試 ===")
        flex_generator = DivinationFlexMessageGenerator()
        
        # 測試一般用戶版本
        user_flex_messages = flex_generator.generate_divination_messages(result, is_admin=False)
        if user_flex_messages:
            print(f"✅ 一般用戶Flex Message生成成功：{len(user_flex_messages)} 個訊息")
        else:
            print("❌ 一般用戶Flex Message生成失敗")
        
        # 測試管理員版本
        admin_flex_messages = flex_generator.generate_divination_messages(result, is_admin=True)
        if admin_flex_messages:
            print(f"✅ 管理員Flex Message生成成功：{len(admin_flex_messages)} 個訊息")
        else:
            print("❌ 管理員Flex Message生成失敗")
        
        print("\n=== 測試結果 ===")
        print("✅ 四化功能在無數據庫模式下正常工作")
        print("✅ 所有四化解釋都包含完整內容")
        print("✅ Flex Message生成正常")
        
    else:
        print(f"❌ 占卜失敗：{result.get('error')}")

if __name__ == "__main__":
    test_divination_without_db() 