#!/usr/bin/env python3
"""
管理員設定腳本
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
    
    try:
        success = PermissionManager.set_admin_permissions(user_id, db)
        
        if success:
            print(f"✅ 成功設定 {user_id} 為管理員")
            print()
            print("管理員權限包含：")
            print("• 無限制使用所有功能")
            print("• 無API調用限制")
            print("• 無設備數量限制")
            print("• 無占卜週限制")
            print("• 可以管理其他用戶權限")
        else:
            print("❌ 設定管理員權限失敗")
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        db.close()

def list_admins():
    """列出所有管理員"""
    print("=== 管理員列表 ===")
    
    db = SessionLocal()
    
    try:
        from app.models.user_permissions import UserPermissions, UserRole
        
        admins = db.query(UserPermissions).filter(
            UserPermissions.role == UserRole.ADMIN
        ).all()
        
        if admins:
            print(f"找到 {len(admins)} 個管理員：")
            print()
            for admin in admins:
                print(f"• User ID: {admin.user_id}")
                print(f"  創建時間: {admin.created_at}")
                print(f"  最後更新: {admin.updated_at}")
                print()
        else:
            print("目前沒有管理員")
            
    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
    finally:
        db.close()

def main():
    """主函數"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_admins()
            return
        elif sys.argv[1] == "add":
            if len(sys.argv) > 2:
                user_id = sys.argv[2]
                db = SessionLocal()
                try:
                    success = PermissionManager.set_admin_permissions(user_id, db)
                    if success:
                        print(f"✅ 成功設定 {user_id} 為管理員")
                    else:
                        print("❌ 設定失敗")
                except Exception as e:
                    print(f"❌ 發生錯誤: {e}")
                finally:
                    db.close()
                return
    
    # 互動模式
    while True:
        print()
        print("=== 管理員管理工具 ===")
        print("1. 設定新管理員")
        print("2. 查看管理員列表")
        print("3. 退出")
        print()
        
        choice = input("請選擇操作 (1-3): ").strip()
        
        if choice == "1":
            setup_admin()
        elif choice == "2":
            list_admins()
        elif choice == "3":
            print("再見！")
            break
        else:
            print("❌ 無效選擇，請重新輸入")

if __name__ == "__main__":
    main() 