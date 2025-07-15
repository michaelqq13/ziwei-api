#!/usr/bin/env python3
"""
簡化版管理員設定腳本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.logic.permission_manager import PermissionManager

def setup_admin():
    """設定管理員權限"""
    print("=== 管理員權限設定 ===")
    print()
    
    # 獲取用戶輸入
    user_id = input("請輸入要設定為管理員的Line User ID: ").strip()
    
    if not user_id:
        print("❌ User ID不能為空")
        return
    
    confirm = input(f"確認要將 {user_id} 設定為管理員嗎？(y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    # 執行設定
    db = SessionLocal()
    permission_manager = PermissionManager()
    
    try:
        # 獲取或創建用戶
        user = permission_manager.get_or_create_user(db, user_id)
        print(f"✅ 用戶確認: {user.line_user_id}")
        
        # 設置管理員權限
        success = permission_manager.set_admin_permissions(user_id, db)
        
        if success:
            print(f"✅ 成功設定 {user_id} 為管理員")
            print()
            print("🎉 管理員權限包含：")
            print("• 無限制占卜功能")
            print("• 指定時間占卜")
            print("• 系統管理功能")
            print("• 用戶數據查看")
            print("• 選單管理功能")
            
            # 驗證設定結果
            db.refresh(user)
            if user.is_admin():
                print(f"\n🔍 驗證成功：{user_id} 現在是管理員")
            else:
                print(f"\n⚠️ 驗證失敗：權限設定可能未生效")
                
        else:
            print("❌ 設定管理員權限失敗")
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin() 