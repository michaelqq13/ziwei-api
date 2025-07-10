#!/usr/bin/env python3
"""
Rich Menu 更新腳本
用於管理和更新 LINE Bot 的 Rich Menu
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.rich_menu_manager import RichMenuManager
from app.utils.driver_view_rich_menu_handler import driver_view_handler
from app.utils.dynamic_rich_menu import dynamic_rich_menu_manager
from app.db.database import get_db
from app.models.linebot_models import LineBotUser
from app.logic.permission_manager import permission_manager
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_default_rich_menu():
    """更新預設 Rich Menu 為 '基本功能' 分頁"""
    print("=== 更新預設 Rich Menu (設為'基本功能') ===")
    
    manager = RichMenuManager()
    
    # 使用 driver_view_handler 創建 "basic" 分頁的 Rich Menu
    basic_menu_id = driver_view_handler.create_tab_rich_menu("basic")
    
    if basic_menu_id:
        print(f"✅ 成功創建新的 '基本功能' Rich Menu: {basic_menu_id}")
        
        # 設為預設
        if manager.set_default_rich_menu(basic_menu_id):
            print(f"✅ 成功設為預設 Rich Menu")
            return basic_menu_id
        else:
            print("❌ 設為預設失敗")
            return None
    else:
        print("❌ 創建新的 '基本功能' Rich Menu 失敗")
        return None

def update_user_rich_menus():
    """更新所有用戶的 Rich Menu"""
    print("\n=== 更新用戶 Rich Menu ===")
    
    try:
        db = next(get_db())
        users = db.query(LineBotUser).all()
        
        if not users:
            print("數據庫中沒有用戶")
            return
        
        print(f"找到 {len(users)} 個用戶")
        
        success_count = 0
        fail_count = 0
        
        for user in users:
            user_id = user.line_user_id
            
            # 檢查用戶 ID 格式（真實的 LINE 用戶 ID 應該以 U 開頭）
            if not user_id.startswith('U') or len(user_id) != 33:
                print(f"⚠️  跳過測試用戶: {user_id} (非真實 LINE 用戶 ID)")
                continue
            
            try:
                # 獲取用戶權限
                user_stats = permission_manager.get_user_stats(db, user)
                is_admin = user_stats["user_info"]["is_admin"]
                
                # 更新 Rich Menu
                from app.utils.rich_menu_manager import update_user_rich_menu
                success = update_user_rich_menu(user_id, is_admin=is_admin)
                
                if success:
                    print(f"✅ 用戶 {user.display_name or user_id} 更新成功")
                    success_count += 1
                else:
                    print(f"❌ 用戶 {user.display_name or user_id} 更新失敗")
                    fail_count += 1
                    
            except Exception as e:
                print(f"❌ 用戶 {user.display_name or user_id} 更新錯誤: {e}")
                fail_count += 1
        
        print(f"\n更新完成：成功 {success_count} 個，失敗 {fail_count} 個")
        db.close()
        
    except Exception as e:
        print(f"更新用戶 Rich Menu 時發生錯誤: {e}")

def cleanup_legacy_menus():
    """清理傳統選單，保留駕駛視窗選單"""
    print("=== 清理傳統選單 ===")
    
    manager = RichMenuManager()
    
    # 獲取所有選單
    all_menus = manager.get_rich_menu_list()
    if not all_menus:
        print("沒有找到任何選單")
        return
    
    # 分類選單
    driver_view_menus = []
    legacy_menus = []
    
    for menu in all_menus:
        menu_id = menu.get("richMenuId")
        menu_name = menu.get("name", "")
        
        # 駕駛視窗選單（保留）
        if ("DriverView" in menu_name or 
            "driver_view" in menu_name.lower() or
            "駕駛視窗" in menu_name):
            driver_view_menus.append(menu)
        # 傳統選單（刪除）
        else:
            legacy_menus.append(menu)
    
    print(f"找到 {len(driver_view_menus)} 個駕駛視窗選單（保留）")
    print(f"找到 {len(legacy_menus)} 個傳統選單（將刪除）")
    
    # 刪除傳統選單
    deleted_count = 0
    for menu in legacy_menus:
        menu_id = menu.get("richMenuId")
        menu_name = menu.get("name", "")
        
        if manager.delete_rich_menu(menu_id):
            print(f"✅ 已刪除傳統選單: {menu_name} ({menu_id})")
            deleted_count += 1
        else:
            print(f"❌ 刪除失敗: {menu_name} ({menu_id})")
    
    print(f"\n清理完成！刪除了 {deleted_count} 個傳統選單")
    
    # 顯示剩餘選單
    if driver_view_menus:
        print("\n保留的駕駛視窗選單:")
        for menu in driver_view_menus:
            menu_id = menu.get("richMenuId")
            menu_name = menu.get("name", "")
            print(f"  - {menu_name} ({menu_id})")

def smart_cleanup():
    """智能清理：只保留最新的駕駛視窗選單"""
    print("=== 智能清理選單 ===")
    
    manager = RichMenuManager()
    
    # 獲取所有選單
    all_menus = manager.get_rich_menu_list()
    if not all_menus:
        print("沒有找到任何選單")
        return
    
    # 按分頁類型分組
    menu_groups = {}
    legacy_menus = []
    
    for menu in all_menus:
        menu_id = menu.get("richMenuId")
        menu_name = menu.get("name", "")
        
        # 駕駛視窗選單
        if ("DriverView" in menu_name or 
            "driver_view" in menu_name.lower() or
            "駕駛視窗" in menu_name):
            
            # 提取分頁信息
            if "DriverView_" in menu_name:
                parts = menu_name.split("_")
                if len(parts) >= 2:
                    tab = parts[1]
                    key = f"driver_view_{tab}"
                    
                    if key not in menu_groups:
                        menu_groups[key] = []
                    menu_groups[key].append(menu)
            else:
                # 無法分類的駕駛視窗選單，暫時保留
                key = "uncategorized_driver_view"
                if key not in menu_groups:
                    menu_groups[key] = []
                menu_groups[key].append(menu)
        else:
            # 傳統選單（全部刪除）
            legacy_menus.append(menu)
    
    print(f"找到 {len(menu_groups)} 個駕駛視窗選單組")
    print(f"找到 {len(legacy_menus)} 個傳統選單（將全部刪除）")
    
    # 刪除傳統選單
    deleted_count = 0
    for menu in legacy_menus:
        menu_id = menu.get("richMenuId")
        menu_name = menu.get("name", "")
        
        if manager.delete_rich_menu(menu_id):
            print(f"✅ 已刪除傳統選單: {menu_name}")
            deleted_count += 1
        else:
            print(f"❌ 刪除失敗: {menu_name}")
    
    # 每組只保留最新的一個
    for key, menus in menu_groups.items():
        if len(menus) > 1:
            print(f"\n處理組 {key}，有 {len(menus)} 個重複選單")
            
            # 保留最新的（假設 ID 較新的是最新的）
            menus.sort(key=lambda x: x.get("richMenuId", ""), reverse=True)
            keep_menu = menus[0]
            delete_menus = menus[1:]
            
            print(f"保留: {keep_menu.get('name', '')} ({keep_menu.get('richMenuId', '')})")
            
            for menu in delete_menus:
                menu_id = menu.get("richMenuId")
                menu_name = menu.get("name", "")
                
                if manager.delete_rich_menu(menu_id):
                    print(f"✅ 已刪除重複選單: {menu_name}")
                    deleted_count += 1
                else:
                    print(f"❌ 刪除失敗: {menu_name}")
    
    print(f"\n智能清理完成！總共刪除了 {deleted_count} 個選單")

def show_rich_menu_status():
    """顯示 Rich Menu 狀態"""
    print("\n=== Rich Menu 狀態 ===")
    
    manager = RichMenuManager()
    
    # 獲取預設 Rich Menu
    default_id = manager.get_default_rich_menu_id()
    print(f"預設 Rich Menu: {default_id}")
    
    # 獲取所有 Rich Menu
    all_menus = manager.get_rich_menu_list()
    if all_menus:
        print(f"\n所有 Rich Menu ({len(all_menus)} 個):")
        for i, menu in enumerate(all_menus, 1):
            menu_id = menu['richMenuId']
            menu_name = menu['name']
            chat_bar_text = menu['chatBarText']
            is_default = "✅" if menu_id == default_id else "  "
            
            print(f"{is_default} {i}. {menu_name}")
            print(f"     ID: {menu_id}")
            print(f"     聊天欄文字: {chat_bar_text}")
            print()
    else:
        print("沒有找到任何 Rich Menu")

def main():
    """主函數"""
    if len(sys.argv) != 2:
        print("使用方法: python update_rich_menu.py <command>")
        print("可用命令:")
        print("  status - 顯示 Rich Menu 狀態")
        print("  update - 更新預設 Rich Menu")
        print("  users - 更新所有用戶的 Rich Menu")
        print("  cleanup - 清理傳統選單（保留分頁式選單）")
        print("  smart - 智能清理（只保留最新的分頁式選單）")
        print("  all - 執行完整更新")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_rich_menu_status()
    elif command == "update":
        update_default_rich_menu()
    elif command == "users":
        update_user_rich_menus()
    elif command == "cleanup":
        cleanup_legacy_menus()
    elif command == "smart":
        smart_cleanup()
    elif command == "all":
        update_default_rich_menu()
        update_user_rich_menus()
        cleanup_legacy_menus()
        show_rich_menu_status()
    else:
        print(f"未知命令: {command}")
        print("請使用 'status', 'update', 'users', 'cleanup', 'smart', 或 'all'")

if __name__ == "__main__":
    main() 