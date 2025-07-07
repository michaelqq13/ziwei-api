#!/usr/bin/env python3
"""
Rich Menu 管理腳本
用於管理和維護 LINE Bot 的 Rich Menu
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.rich_menu_manager import rich_menu_manager
from app.utils.rich_menu_image_generator import generate_admin_starry_rich_menu, generate_starry_rich_menu
from app.db.database import get_db
from app.logic.permission_manager import permission_manager
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_rich_menus():
    """列出所有 Rich Menu"""
    print("📋 Rich Menu 列表:")
    menus = rich_menu_manager.get_rich_menu_list()
    
    if menus:
        for i, menu in enumerate(menus, 1):
            name = menu.get('name', '未知')
            menu_id = menu.get('richMenuId', '未知')
            size = menu.get('size', {})
            width = size.get('width', 0)
            height = size.get('height', 0)
            chat_bar_text = menu.get('chatBarText', '未設定')
            
            print(f"  {i}. {name}")
            print(f"     ID: {menu_id}")
            print(f"     尺寸: {width}x{height}")
            print(f"     聊天欄文字: {chat_bar_text}")
            print()
    else:
        print("  沒有找到任何 Rich Menu")

def get_current_default():
    """獲取當前預設 Rich Menu"""
    default_id = rich_menu_manager.get_default_rich_menu_id()
    if default_id:
        print(f"📌 當前預設 Rich Menu ID: {default_id}")
    else:
        print("❌ 沒有設定預設 Rich Menu")

def setup_menus():
    """設定所有 Rich Menu"""
    print("🔧 設定 Rich Menu...")
    
    # 設定一般用戶 Rich Menu
    print("\n1. 設定一般用戶 Rich Menu...")
    normal_menu_id = rich_menu_manager.ensure_default_rich_menu()
    if normal_menu_id:
        print(f"✅ 一般用戶 Rich Menu 設定成功: {normal_menu_id}")
    else:
        print("❌ 一般用戶 Rich Menu 設定失敗")
    
    # 設定管理員 Rich Menu
    print("\n2. 設定管理員 Rich Menu...")
    admin_menu_id = rich_menu_manager.setup_admin_rich_menu()
    if admin_menu_id:
        print(f"✅ 管理員 Rich Menu 設定成功: {admin_menu_id}")
    else:
        print("❌ 管理員 Rich Menu 設定失敗")
    
    print("\n🎉 Rich Menu 設定完成！")

def update_user_menu(line_user_id: str, is_admin: bool = False):
    """更新特定用戶的 Rich Menu"""
    print(f"🔄 更新用戶 {line_user_id} 的 Rich Menu...")
    
    success = rich_menu_manager.set_user_menu_by_role(line_user_id, is_admin)
    if success:
        menu_type = "管理員" if is_admin else "一般用戶"
        print(f"✅ 成功設定 {menu_type} Rich Menu")
    else:
        print("❌ 設定 Rich Menu 失敗")

def cleanup_old_menus():
    """清理舊的 Rich Menu"""
    print("🧹 清理舊的 Rich Menu...")
    
    # 獲取當前預設 Rich Menu
    default_id = rich_menu_manager.get_default_rich_menu_id()
    
    # 獲取管理員 Rich Menu
    admin_menu_id = rich_menu_manager.get_or_create_admin_menu_id()
    
    # 保留的 Rich Menu ID 列表
    keep_ids = []
    if default_id:
        keep_ids.append(default_id)
    if admin_menu_id:
        keep_ids.append(admin_menu_id)
    
    # 刪除其他 Rich Menu
    menus = rich_menu_manager.get_rich_menu_list()
    if menus:
        deleted_count = 0
        for menu in menus:
            menu_id = menu.get('richMenuId')
            if menu_id not in keep_ids:
                if rich_menu_manager.delete_rich_menu(menu_id):
                    deleted_count += 1
                    print(f"🗑️ 已刪除 Rich Menu: {menu_id}")
        
        print(f"✅ 清理完成，共刪除 {deleted_count} 個舊的 Rich Menu")
    else:
        print("❌ 無法獲取 Rich Menu 列表")

def regenerate_images():
    """重新生成 Rich Menu 圖片"""
    print("🎨 重新生成 Rich Menu 圖片...")
    
    try:
        # 生成一般用戶圖片
        normal_image, _ = generate_starry_rich_menu()
        print(f"✅ 一般用戶圖片生成成功: {normal_image}")
        
        # 生成管理員圖片
        admin_image, _ = generate_admin_starry_rich_menu()
        print(f"✅ 管理員圖片生成成功: {admin_image}")
        
        print("🎉 圖片生成完成！")
        
    except Exception as e:
        print(f"❌ 圖片生成失敗: {e}")

def show_menu_differences():
    """顯示一般用戶和管理員 Rich Menu 的差異"""
    print("🔍 Rich Menu 差異分析:")
    
    try:
        # 生成配置
        normal_image, normal_areas = generate_starry_rich_menu()
        admin_image, admin_areas = generate_admin_starry_rich_menu()
        
        # 提取按鈕文字
        normal_buttons = [area.get('action', {}).get('text', '') for area in normal_areas]
        admin_buttons = [area.get('action', {}).get('text', '') for area in admin_areas]
        
        print(f"\n📊 按鈕數量:")
        print(f"  一般用戶: {len(normal_buttons)} 個")
        print(f"  管理員: {len(admin_buttons)} 個")
        
        print(f"\n🔹 一般用戶按鈕:")
        for i, button in enumerate(normal_buttons, 1):
            print(f"  {i}. {button}")
        
        print(f"\n🔸 管理員按鈕:")
        for i, button in enumerate(admin_buttons, 1):
            print(f"  {i}. {button}")
        
        # 找出差異
        normal_set = set(normal_buttons)
        admin_set = set(admin_buttons)
        
        admin_only = admin_set - normal_set
        if admin_only:
            print(f"\n⭐ 管理員專用按鈕:")
            for button in admin_only:
                print(f"  - {button}")
        
    except Exception as e:
        print(f"❌ 分析差異時發生錯誤: {e}")

def main():
    """主功能選單"""
    print("🌟 Rich Menu 管理工具 ✨")
    print("=" * 50)
    
    while True:
        print("\n📋 請選擇操作:")
        print("1. 列出所有 Rich Menu")
        print("2. 查看當前預設 Rich Menu")
        print("3. 設定所有 Rich Menu")
        print("4. 更新用戶 Rich Menu")
        print("5. 清理舊的 Rich Menu")
        print("6. 重新生成圖片")
        print("7. 顯示 Rich Menu 差異")
        print("0. 退出")
        
        choice = input("\n請輸入選項 (0-7): ").strip()
        
        if choice == "1":
            list_rich_menus()
        elif choice == "2":
            get_current_default()
        elif choice == "3":
            setup_menus()
        elif choice == "4":
            user_id = input("請輸入 LINE 用戶 ID: ").strip()
            is_admin_str = input("是否為管理員? (y/n): ").strip().lower()
            is_admin = is_admin_str in ['y', 'yes', '是']
            update_user_menu(user_id, is_admin)
        elif choice == "5":
            confirm = input("確定要清理舊的 Rich Menu 嗎? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                cleanup_old_menus()
        elif choice == "6":
            regenerate_images()
        elif choice == "7":
            show_menu_differences()
        elif choice == "0":
            print("👋 再見！")
            break
        else:
            print("❌ 無效的選項，請重新選擇")

if __name__ == "__main__":
    main() 