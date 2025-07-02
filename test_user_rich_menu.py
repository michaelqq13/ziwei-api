#!/usr/bin/env python3
"""
測試為特定用戶設置Rich Menu
"""

import sys
import os
sys.path.append('.')

from app.utils.rich_menu_manager import rich_menu_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_user_rich_menu(user_id=None):
    """為用戶設置Rich Menu"""
    try:
        # 1. 確保有預設Rich Menu
        logger.info("檢查預設Rich Menu...")
        menu_id = rich_menu_manager.get_default_rich_menu_id()
        
        if not menu_id:
            logger.info("沒有預設Rich Menu，正在創建...")
            menu_id = rich_menu_manager.setup_complete_rich_menu(force_recreate=True)
            
        if not menu_id:
            logger.error("無法創建Rich Menu")
            return False
            
        logger.info(f"找到Rich Menu ID: {menu_id}")
        
        # 2. 如果提供了用戶ID，為該用戶設置Rich Menu
        if user_id:
            logger.info(f"為用戶 {user_id} 設置Rich Menu...")
            success = rich_menu_manager.set_user_rich_menu(user_id, menu_id)
            if success:
                logger.info(f"✅ 成功為用戶 {user_id} 設置Rich Menu")
            else:
                logger.error(f"❌ 為用戶 {user_id} 設置Rich Menu失敗")
            return success
        else:
            logger.info("✅ 預設Rich Menu已設置完成")
            return True
            
    except Exception as e:
        logger.error(f"設置Rich Menu時發生錯誤: {e}")
        return False

def get_rich_menu_status():
    """獲取Rich Menu狀態"""
    try:
        # 獲取預設Rich Menu
        default_menu = rich_menu_manager.get_default_rich_menu_id()
        logger.info(f"預設Rich Menu ID: {default_menu}")
        
        # 獲取所有Rich Menu
        all_menus = rich_menu_manager.get_rich_menu_list()
        logger.info(f"總共有 {len(all_menus) if all_menus else 0} 個Rich Menu")
        
        if all_menus:
            for menu in all_menus:
                logger.info(f"- {menu.get('richMenuId')}: {menu.get('name', 'Unknown')}")
                
        return {
            "default_menu": default_menu,
            "total_menus": len(all_menus) if all_menus else 0,
            "menus": all_menus or []
        }
        
    except Exception as e:
        logger.error(f"獲取Rich Menu狀態時發生錯誤: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            print("=== Rich Menu 狀態 ===")
            get_rich_menu_status()
            
        elif command == "setup":
            print("=== 設置預設 Rich Menu ===")
            set_user_rich_menu()
            
        elif command == "set_user" and len(sys.argv) > 2:
            user_id = sys.argv[2]
            print(f"=== 為用戶 {user_id} 設置 Rich Menu ===")
            set_user_rich_menu(user_id)
            
        else:
            print("用法:")
            print("  python test_user_rich_menu.py status")
            print("  python test_user_rich_menu.py setup")
            print("  python test_user_rich_menu.py set_user <USER_ID>")
    else:
        print("=== Rich Menu 測試腳本 ===")
        print("1. 檢查狀態...")
        get_rich_menu_status()
        print("\n2. 設置預設Rich Menu...")
        set_user_rich_menu() 