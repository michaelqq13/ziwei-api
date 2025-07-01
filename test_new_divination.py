#!/usr/bin/env python3
"""
測試重構後的占卜功能
"""

import requests
import json
import time

def test_divination_api():
    """測試占卜API功能"""
    base_url = "http://localhost:8000"
    test_user_id = "test_user_rebuild_123"
    
    print("🔮 測試重構後的占卜功能\n")
    
    try:
        # 1. 測試占卜狀態檢查
        print("1️⃣ 測試占卜狀態檢查...")
        response = requests.post(f"{base_url}/api/divination/check/{test_user_id}")
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            check_result = response.json()
            print(f"檢查結果: {json.dumps(check_result, indent=2, ensure_ascii=False)}")
            
            if check_result.get("can_divinate"):
                # 2. 測試執行占卜
                print("\n2️⃣ 測試執行占卜...")
                response = requests.post(f"{base_url}/api/divination/perform/{test_user_id}?gender=M")
                print(f"狀態碼: {response.status_code}")
                
                if response.status_code == 200:
                    divination_result = response.json()
                    print(f"占卜結果: {json.dumps(divination_result, indent=2, ensure_ascii=False)}")
                    
                    # 3. 再次檢查狀態（應該顯示本週已占卜）
                    print("\n3️⃣ 再次檢查占卜狀態...")
                    response = requests.post(f"{base_url}/api/divination/check/{test_user_id}")
                    if response.status_code == 200:
                        check_result2 = response.json()
                        print(f"第二次檢查結果: {json.dumps(check_result2, indent=2, ensure_ascii=False)}")
                        
                        if not check_result2.get("can_divinate"):
                            print("✅ 週限制功能正常運作")
                        else:
                            print("❌ 週限制功能異常")
                    
                    # 4. 測試占卜歷史
                    print("\n4️⃣ 測試占卜歷史...")
                    response = requests.get(f"{base_url}/api/divination/history/{test_user_id}")
                    if response.status_code == 200:
                        history_result = response.json()
                        print(f"歷史記錄: {json.dumps(history_result, indent=2, ensure_ascii=False)}")
                        print("✅ 歷史記錄功能正常")
                    else:
                        print(f"❌ 歷史記錄測試失敗: {response.status_code}")
                        
                else:
                    print(f"❌ 執行占卜失敗: {response.status_code}")
                    print(f"錯誤訊息: {response.text}")
            else:
                print("ℹ️ 用戶本週已經占卜過，測試週限制功能")
                
        else:
            print(f"❌ 占卜狀態檢查失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到API服務，請確認服務是否運行在 http://localhost:8000")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

def test_direct_divination_logic():
    """直接測試占卜邏輯"""
    print("\n🧪 直接測試占卜邏輯模組\n")
    
    try:
        from app.logic.divination import calculate_divination
        from datetime import datetime
        
        result = calculate_divination(datetime.now(), 'F')
        print("占卜邏輯測試結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("✅ 占卜邏輯模組正常運作")
        
    except Exception as e:
        print(f"❌ 占卜邏輯測試失敗: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🌟 紫微斗數占卜功能重構測試")
    print("=" * 50)
    
    # 測試直接邏輯
    test_direct_divination_logic()
    
    # 等待一下確保服務啟動
    print("\n⏳ 等待API服務啟動...")
    time.sleep(3)
    
    # 測試API
    test_divination_api()
    
    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    print("=" * 50) 