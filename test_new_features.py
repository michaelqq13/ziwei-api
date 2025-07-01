#!/usr/bin/env python3
"""
測試新功能：權限系統、綁定功能、占卜功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import get_db, engine
from app.logic.permission_manager import PermissionManager
from app.logic.user_binding import UserBindingManager
from app.logic.divination import can_divination_this_week, calculate_divination, save_divination_record
from app.models.user_permissions import UserPermissions, UserRole
from app.models.user_birth_info import UserBirthInfo
from app.models.pending_binding import PendingBinding

def test_permission_system():
    """測試權限系統"""
    print("🔐 測試權限系統...")
    
    db = next(get_db())
    test_user_id = "test_user_permissions"
    
    try:
        # 測試創建用戶權限
        permissions = PermissionManager.get_or_create_user_permissions(test_user_id, db)
        print(f"✅ 創建用戶權限成功: {permissions.user_id}, 角色: {permissions.role}")
        
        # 測試權限檢查
        is_premium = PermissionManager.check_premium_access(test_user_id, db)
        is_admin = PermissionManager.check_admin_access(test_user_id, db)
        print(f"✅ 權限檢查: 付費={is_premium}, 管理員={is_admin}")
        
        # 測試API頻率限制
        rate_limit = PermissionManager.check_api_rate_limit(test_user_id, db)
        print(f"✅ API頻率限制: {rate_limit}")
        
        # 測試升級為付費會員
        upgrade_success = PermissionManager.upgrade_to_premium(test_user_id, 30, db)
        print(f"✅ 升級付費會員: {upgrade_success}")
        
        # 再次檢查權限
        is_premium_after = PermissionManager.check_premium_access(test_user_id, db)
        print(f"✅ 升級後權限檢查: 付費={is_premium_after}")
        
    except Exception as e:
        print(f"❌ 權限系統測試失敗: {e}")
    finally:
        # 清理測試數據
        db.query(UserPermissions).filter(UserPermissions.user_id == test_user_id).delete()
        db.commit()
        db.close()

def test_binding_system():
    """測試綁定系統"""
    print("\n📱 測試綁定系統...")
    
    db = next(get_db())
    test_user_id = "test_user_binding"
    test_birth_data = {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "gender": "male",
        "location": "台北市"
    }
    
    try:
        # 測試創建待綁定記錄
        pending_success = UserBindingManager.create_pending_binding(test_birth_data, db)
        print(f"✅ 創建待綁定記錄: {pending_success}")
        
        # 測試綁定用戶
        if pending_success:
            binding_result = UserBindingManager.process_binding_request(test_user_id, db)
            print(f"✅ 綁定用戶: {binding_result.get('success', False)}")
            
            if binding_result.get('success'):
                # 檢查綁定狀態
                is_bound = UserBindingManager.is_user_bound(test_user_id, db)
                print(f"✅ 綁定狀態檢查: {is_bound}")
                
                # 獲取綁定資訊
                birth_info = UserBindingManager.get_user_birth_info(test_user_id, db)
                print(f"✅ 獲取綁定資訊: {birth_info is not None}")
            else:
                print(f"❌ 綁定失敗: {binding_result.get('message', '未知錯誤')}")
        
    except Exception as e:
        print(f"❌ 綁定系統測試失敗: {e}")
    finally:
        # 清理測試數據
        db.query(UserBirthInfo).filter(UserBirthInfo.user_id == test_user_id).delete()
        db.query(PendingBinding).delete()
        db.commit()
        db.close()

def test_divination_system():
    """測試占卜系統"""
    print("\n🔮 測試占卜系統...")
    
    db = next(get_db())
    test_user_id = "test_user_divination"
    
    try:
        # 檢查占卜權限
        can_divinate = can_divination_this_week(test_user_id, db)
        print(f"✅ 占卜權限檢查: {can_divinate}")
        
        if can_divinate:
            # 執行占卜
            from datetime import datetime
            divination_time = datetime.now()
            divination_result = calculate_divination(divination_time, "male", db=db)
            print(f"✅ 計算占卜: {divination_result is not None}")
            
            if divination_result:
                print(f"   占卜結果摘要: {divination_result.get('summary', '')[:50]}...")
                
                # 保存占卜記錄
                save_divination_record(test_user_id, divination_time, "male", divination_result, db)
                print(f"✅ 保存占卜記錄成功")
            
            # 再次檢查是否還能占卜
            can_divinate_again = can_divination_this_week(test_user_id, db)
            print(f"✅ 占卜後權限檢查: {can_divinate_again}")
        
    except Exception as e:
        print(f"❌ 占卜系統測試失敗: {e}")
    finally:
        # 清理測試數據
        from app.models.divination import DivinationRecord
        db.query(DivinationRecord).filter(DivinationRecord.user_id == test_user_id).delete()
        db.commit()
        db.close()

def test_api_endpoints():
    """測試API端點"""
    print("\n🌐 測試API端點...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # 測試用戶狀態API
        response = client.get("/api/protected/user/status", headers={"X-User-ID": "test_api_user"})
        print(f"✅ 用戶狀態API: {response.status_code}")
        
        # 測試升級信息API
        response = client.get("/api/protected/upgrade-info", headers={"X-User-ID": "test_api_user"})
        print(f"✅ 升級信息API: {response.status_code}")
        
        # 測試綁定狀態API
        response = client.get("/api/chart-binding/binding-status", headers={"X-User-ID": "test_api_user"})
        print(f"✅ 綁定狀態API: {response.status_code}")
        
    except ImportError:
        print("⚠️  FastAPI TestClient 不可用，跳過API測試")
    except Exception as e:
        print(f"❌ API端點測試失敗: {e}")

def main():
    """主測試函數"""
    print("🚀 開始測試新功能...")
    print("=" * 50)
    
    # 確保數據庫表存在
    from app.db.database import Base
    Base.metadata.create_all(bind=engine)
    
    # 運行各項測試
    test_permission_system()
    test_binding_system()
    test_divination_system()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 功能測試完成！")

if __name__ == "__main__":
    main() 