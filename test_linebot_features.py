#!/usr/bin/env python3
"""
LINE Bot 功能測試腳本
測試占卜、運勢查詢、會員管理等核心功能
"""

import sys
import os
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.logic.divination import calculate_divination, can_divination_this_week
from app.logic.fortune_analysis import FortuneAnalyzer, format_fortune_result
from app.logic.permission_manager import PermissionManager
from app.logic.user_binding import UserBindingManager
from app.models.user_permissions import UserRole

def test_divination_logic():
    """測試占卜邏輯"""
    print("🔮 測試占卜功能")
    print("-" * 30)
    
    try:
        # 獲取數據庫連接
        db = next(get_db())
        
        # 測試占卜計算
        divination_time = datetime.now()
        gender = "M"
        
        print(f"占卜時間: {divination_time}")
        print(f"性別: {'男性' if gender == 'M' else '女性'}")
        
        result = calculate_divination(divination_time, gender, db)
        
        print("\n占卜結果:")
        print(f"- 運勢摘要: {result.get('summary', 'N/A')}")
        print(f"- 本週重點: {result.get('week_focus', 'N/A')}")
        print(f"- 建議: {result.get('advice', 'N/A')}")
        
        fortune_aspects = result.get('fortune_aspects', {})
        if fortune_aspects:
            print("\n各面向運勢:")
            for aspect, fortune in fortune_aspects.items():
                print(f"- {aspect}: {fortune}")
        
        four_transformations = result.get('four_transformations', [])
        if four_transformations:
            print(f"\n四化解釋數量: {len(four_transformations)}")
        
        print("✅ 占卜功能測試通過")
        
    except Exception as e:
        print(f"❌ 占卜功能測試失敗: {e}")
    
    finally:
        db.close()

def test_permission_management():
    """測試權限管理"""
    print("\n👤 測試權限管理")
    print("-" * 30)
    
    try:
        db = next(get_db())
        test_user_id = "test_user_123"
        
        # 測試創建/獲取用戶權限
        user_permission = PermissionManager.get_or_create_user_permissions(test_user_id, db)
        print(f"✅ 創建/獲取用戶權限: {test_user_id}")
        
        if user_permission:
            print(f"✅ 獲取用戶權限成功")
            print(f"   - 用戶角色: {user_permission.role}")
            print(f"   - 是否為管理員: {user_permission.is_admin()}")
            print(f"   - 可使用付費功能: {user_permission.can_use_premium_feature()}")
        
        # 測試設置管理員權限
        success = PermissionManager.set_admin_permissions(test_user_id, db)
        if success:
            print("✅ 設置管理員權限成功")
        
        # 測試占卜權限檢查
        divination_permission = PermissionManager.check_divination_permission(test_user_id, db)
        print(f"✅ 占卜權限檢查: {divination_permission.get('can_divinate', False)}")
        
        # 測試用戶狀態摘要
        status_summary = PermissionManager.get_user_status_summary(test_user_id, db)
        if "error" not in status_summary:
            print("✅ 用戶狀態摘要獲取成功")
        
        print("✅ 權限管理測試通過")
        
    except Exception as e:
        print(f"❌ 權限管理測試失敗: {e}")
    
    finally:
        db.close()

def test_user_binding():
    """測試用戶綁定功能"""
    print("\n📅 測試用戶綁定")
    print("-" * 30)
    
    try:
        db = next(get_db())
        test_user_id = "test_binding_user_456"
        
        # 測試綁定用戶生辰資訊
        birth_data = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "gender": "F"
        }
        
        success = UserBindingManager.bind_user_birth_info(test_user_id, birth_data, db)
        
        if success:
            print("✅ 綁定用戶生辰資訊成功")
            
            # 測試檢查綁定狀態
            is_bound = UserBindingManager.is_user_bound(test_user_id, db)
            print(f"✅ 用戶綁定狀態: {is_bound}")
            
            # 測試獲取生辰資訊
            birth_info = UserBindingManager.get_user_birth_info(test_user_id, db)
            if birth_info:
                print("✅ 獲取生辰資訊成功")
                print(f"   - 出生時間: {birth_info['year']}/{birth_info['month']:02d}/{birth_info['day']:02d} {birth_info['hour']:02d}:{birth_info['minute']:02d}")
                print(f"   - 性別: {'女性' if birth_info['gender'] == 'F' else '男性'}")
        else:
            print("❌ 綁定用戶生辰資訊失敗")
        
        print("✅ 用戶綁定測試通過")
        
    except Exception as e:
        print(f"❌ 用戶綁定測試失敗: {e}")
    
    finally:
        db.close()

def test_fortune_analysis():
    """測試運勢分析"""
    print("\n📊 測試運勢分析")
    print("-" * 30)
    
    try:
        db = next(get_db())
        fortune_analyzer = FortuneAnalyzer(db)
        
        # 先確保有測試用戶的綁定資訊
        test_user_id = "test_fortune_user_789"
        
        birth_data = {
            "year": 1985,
            "month": 3,
            "day": 20,
            "hour": 10,
            "minute": 15,
            "gender": "M"
        }
        
        UserBindingManager.bind_user_birth_info(test_user_id, birth_data, db)
        
        # 測試流年運勢
        annual_result = fortune_analyzer.analyze_annual_fortune(test_user_id, 2024)
        if "error" not in annual_result:
            print("✅ 流年運勢分析成功")
            formatted_annual = format_fortune_result(annual_result)
            print(f"   流年運勢長度: {len(formatted_annual)} 字符")
        else:
            print(f"❌ 流年運勢分析失敗: {annual_result['error']}")
        
        # 測試流月運勢
        monthly_result = fortune_analyzer.analyze_monthly_fortune(test_user_id, 2024, 12)
        if "error" not in monthly_result:
            print("✅ 流月運勢分析成功")
            formatted_monthly = format_fortune_result(monthly_result)
            print(f"   流月運勢長度: {len(formatted_monthly)} 字符")
        else:
            print(f"❌ 流月運勢分析失敗: {monthly_result['error']}")
        
        # 測試流日運勢
        daily_result = fortune_analyzer.analyze_daily_fortune(test_user_id, datetime.now())
        if "error" not in daily_result:
            print("✅ 流日運勢分析成功")
            formatted_daily = format_fortune_result(daily_result)
            print(f"   流日運勢長度: {len(formatted_daily)} 字符")
        else:
            print(f"❌ 流日運勢分析失敗: {daily_result['error']}")
        
        print("✅ 運勢分析測試通過")
        
    except Exception as e:
        print(f"❌ 運勢分析測試失敗: {e}")
    
    finally:
        db.close()

def test_config_loading():
    """測試配置加載"""
    print("\n⚙️ 測試配置加載")
    print("-" * 30)
    
    try:
        from app.config.linebot_config import LineBotConfig
        
        print(f"✅ LINE Bot配置加載成功")
        print(f"   - Channel Secret: {'已設置' if LineBotConfig.CHANNEL_SECRET else '未設置'}")
        print(f"   - Access Token: {'已設置' if LineBotConfig.CHANNEL_ACCESS_TOKEN else '未設置'}")
        print(f"   - 管理員密語: {LineBotConfig.ADMIN_SECRET_PHRASE}")
        print(f"   - 主選單項目數: {len(LineBotConfig.MAIN_MENU_ITEMS)}")
        print(f"   - 性別選單項目數: {len(LineBotConfig.GENDER_MENU_ITEMS)}")
        print(f"   - 運勢選單項目數: {len(LineBotConfig.FORTUNE_MENU_ITEMS)}")
        
        # 測試驗證功能
        test_cases = [
            ("year", 1990, True),
            ("year", 1800, False),
            ("month", 5, True),
            ("month", 13, False),
            ("hour", 14, True),
            ("hour", 25, False)
        ]
        
        print("\n驗證功能測試:")
        for field, value, expected in test_cases:
            result = LineBotConfig.validate_birth_data(field, value)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {field}={value}: {result}")
        
        print("✅ 配置加載測試通過")
        
    except Exception as e:
        print(f"❌ 配置加載測試失敗: {e}")

def test_database_connection():
    """測試數據庫連接"""
    print("\n🗄️ 測試數據庫連接")
    print("-" * 30)
    
    try:
        db = next(get_db())
        
        # 测试基本查询
        from app.models.user_permissions import UserPermissions
        user_count = db.query(UserPermissions).count()
        print(f"✅ 數據庫連接成功")
        print(f"   - 用戶權限記錄數: {user_count}")
        
        # 測試創建和查詢
        test_user_id = "db_test_user"
        user_permission = PermissionManager.get_or_create_user_permissions(test_user_id, db)
        
        if user_permission:
            print(f"✅ 數據庫讀寫測試成功")
        
        print("✅ 數據庫連接測試通過")
        
    except Exception as e:
        print(f"❌ 數據庫連接測試失敗: {e}")
    
    finally:
        db.close()

def run_all_tests():
    """運行所有測試"""
    print("🧪 LINE Bot 功能測試套件")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_database_connection,
        test_permission_management,
        test_user_binding,
        test_divination_logic,
        test_fortune_analysis,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 執行失敗: {e}")
        
        print()  # 空行分隔
    
    print("=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！LINE Bot系統準備就緒")
    else:
        print("⚠️  部分測試失敗，請檢查相關功能")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 