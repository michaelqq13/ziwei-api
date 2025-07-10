#!/usr/bin/env python3
"""
駕駛視窗選單管理工具
解決舊選單緩存和衝突問題
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from app.utils.driver_view_rich_menu_handler import DriverViewRichMenuHandler
from app.utils.rich_menu_manager import RichMenuManager

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show_menu_status():
    """顯示選單狀態"""
    print("\n" + "="*60)
    print("🚗 駕駛視窗選單狀態")
    print("="*60)
    
    try:
        handler = DriverViewRichMenuHandler()
        manager = RichMenuManager()
        
        # 獲取所有選單
        all_menus = manager.get_rich_menu_list()
        if not all_menus:
            print("📋 沒有找到任何 Rich Menu")
            return
        
        # 分類選單
        driver_menus = []
        other_menus = []
        
        for menu in all_menus:
            menu_name = menu.get("name", "")
            if ("DriverView" in menu_name or 
                "driver_view" in menu_name.lower() or
                "駕駛視窗" in menu_name):
                driver_menus.append(menu)
            else:
                other_menus.append(menu)
        
        print(f"📊 總選單數: {len(all_menus)}")
        print(f"🚗 駕駛視窗選單: {len(driver_menus)}")
        print(f"📄 其他選單: {len(other_menus)}")
        
        # 顯示駕駛視窗選單詳情
        if driver_menus:
            print(f"\n📋 駕駛視窗選單列表:")
            current_version = handler.menu_version
            for i, menu in enumerate(driver_menus, 1):
                menu_id = menu.get("richMenuId")
                menu_name = menu.get("name", "")
                
                # 檢查版本
                is_current = current_version in menu_name
                version_status = "✅ 當前版本" if is_current else "⚠️ 舊版本"
                
                print(f"  {i}. {menu_name}")
                print(f"     ID: {menu_id}")
                print(f"     狀態: {version_status}")
                print()
        
        # 獲取緩存狀態
        cache_status = handler.get_cache_status()
        print(f"🗄️ 緩存狀態:")
        print(f"   版本: {cache_status.get('version', 'Unknown')}")
        print(f"   緩存選單數: {cache_status.get('cached_menus', 0)}")
        
        if cache_status.get('cache_details'):
            print(f"   緩存詳情:")
            for cache_key, details in cache_status['cache_details'].items():
                is_valid = "✅ 有效" if details['is_valid'] else "❌ 無效"
                print(f"     - {cache_key}: {details['menu_id']} ({is_valid})")
        
        # 獲取預設選單
        default_menu_id = manager.get_default_rich_menu_id()
        if default_menu_id:
            print(f"\n🌟 預設選單 ID: {default_menu_id}")
            # 查找對應的選單名稱
            for menu in all_menus:
                if menu.get("richMenuId") == default_menu_id:
                    menu_name = menu.get("name", "")
                    is_driver = ("DriverView" in menu_name or 
                               "driver_view" in menu_name.lower() or
                               "駕駛視窗" in menu_name)
                    menu_type = "🚗 駕駛視窗選單" if is_driver else "📄 一般選單"
                    print(f"    名稱: {menu_name} ({menu_type})")
                    break
        else:
            print(f"\n🌟 預設選單: 未設定")
            
    except Exception as e:
        print(f"❌ 獲取選單狀態失敗: {e}")

def cleanup_old_menus():
    """清理舊選單"""
    print("\n" + "="*60)
    print("🧹 清理舊駕駛視窗選單")
    print("="*60)
    
    try:
        handler = DriverViewRichMenuHandler()
        
        # 清理舊選單
        deleted_count = handler.cleanup_old_driver_menus(keep_current_version=True)
        
        if deleted_count > 0:
            print(f"✅ 清理完成！刪除了 {deleted_count} 個舊選單")
        else:
            print("📋 沒有需要清理的舊選單")
            
    except Exception as e:
        print(f"❌ 清理失敗: {e}")

def force_refresh_all():
    """強制刷新所有分頁選單"""
    print("\n" + "="*60)
    print("🔄 強制刷新所有分頁選單")
    print("="*60)
    
    try:
        handler = DriverViewRichMenuHandler()
        tabs = ["basic", "fortune", "advanced"]
        
        # 先清理所有舊選單
        print("🧹 清理所有舊選單...")
        handler.cleanup_old_driver_menus(keep_current_version=False)
        
        # 清空緩存
        handler.clear_cache()
        
        # 重新創建所有選單
        success_count = 0
        for tab in tabs:
            print(f"🔄 刷新 {tab} 分頁...")
            menu_id = handler.force_refresh_menu(tab)
            if menu_id:
                success_count += 1
                print(f"✅ {tab} 分頁刷新成功: {menu_id}")
            else:
                print(f"❌ {tab} 分頁刷新失敗")
        
        print(f"\n🎉 刷新完成！成功刷新 {success_count}/{len(tabs)} 個分頁")
        
        # 設定基本功能為預設選單
        if success_count > 0:
            manager = RichMenuManager()
            basic_menu_id = handler.rich_menu_cache.get("driver_view_basic")
            if basic_menu_id:
                if manager.set_default_rich_menu(basic_menu_id):
                    print(f"✅ 基本功能設為預設選單: {basic_menu_id}")
                else:
                    print(f"⚠️ 設定預設選單失敗")
        
    except Exception as e:
        print(f"❌ 強制刷新失敗: {e}")

def clear_cache():
    """清空緩存"""
    print("\n" + "="*60)
    print("🗑️ 清空選單緩存")
    print("="*60)
    
    try:
        handler = DriverViewRichMenuHandler()
        handler.clear_cache()
        print("✅ 緩存清空完成")
        
    except Exception as e:
        print(f"❌ 清空緩存失敗: {e}")

def validate_cache():
    """驗證緩存有效性"""
    print("\n" + "="*60)
    print("🔍 驗證緩存有效性")
    print("="*60)
    
    try:
        handler = DriverViewRichMenuHandler()
        cache_status = handler.get_cache_status()
        
        if not cache_status.get('cache_details'):
            print("📋 沒有緩存的選單")
            return
        
        print(f"檢查 {len(cache_status['cache_details'])} 個緩存選單:")
        
        invalid_count = 0
        for cache_key, details in cache_status['cache_details'].items():
            menu_id = details['menu_id']
            is_valid = details['is_valid']
            
            if is_valid:
                print(f"✅ {cache_key}: {menu_id} (有效)")
            else:
                print(f"❌ {cache_key}: {menu_id} (無效)")
                invalid_count += 1
        
        if invalid_count > 0:
            print(f"\n⚠️ 發現 {invalid_count} 個無效緩存")
            response = input("是否要清理無效緩存？(y/N): ")
            if response.lower() == 'y':
                # 清理無效緩存
                for cache_key, details in list(cache_status['cache_details'].items()):
                    if not details['is_valid']:
                        if cache_key in handler.rich_menu_cache:
                            del handler.rich_menu_cache[cache_key]
                            print(f"🗑️ 已清除無效緩存: {cache_key}")
                print("✅ 無效緩存清理完成")
        else:
            print("✅ 所有緩存都是有效的")
            
    except Exception as e:
        print(f"❌ 驗證緩存失敗: {e}")

def setup_fresh_menus():
    """建立全新的選單系統"""
    print("\n" + "="*60)
    print("🆕 建立全新選單系統")
    print("="*60)
    
    try:
        # 確認操作
        print("⚠️ 這將刪除所有現有的駕駛視窗選單並重新創建")
        response = input("確定要繼續嗎？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            return
        
        handler = DriverViewRichMenuHandler()
        manager = RichMenuManager()
        
        # 1. 刪除所有駕駛視窗選單
        print("🗑️ 刪除所有現有的駕駛視窗選單...")
        deleted_count = handler.cleanup_old_driver_menus(keep_current_version=False)
        print(f"✅ 刪除了 {deleted_count} 個舊選單")
        
        # 2. 清空緩存
        print("🧹 清空緩存...")
        handler.clear_cache()
        
        # 3. 重新創建所有分頁
        print("🔧 創建新的分頁選單...")
        tabs = ["basic", "fortune", "advanced"]
        created_menus = {}
        
        for tab in tabs:
            print(f"   創建 {tab} 分頁...")
            menu_id = handler.create_tab_rich_menu(tab)
            if menu_id:
                created_menus[tab] = menu_id
                handler.rich_menu_cache[f"driver_view_{tab}"] = menu_id
                print(f"   ✅ {tab}: {menu_id}")
            else:
                print(f"   ❌ {tab}: 創建失敗")
        
        # 4. 設定預設選單
        if "basic" in created_menus:
            print("🌟 設定基本功能為預設選單...")
            if manager.set_default_rich_menu(created_menus["basic"]):
                print(f"✅ 預設選單設定成功: {created_menus['basic']}")
            else:
                print("⚠️ 設定預設選單失敗")
        
        print(f"\n🎉 全新選單系統建立完成！")
        print(f"   成功創建 {len(created_menus)}/{len(tabs)} 個分頁選單")
        
    except Exception as e:
        print(f"❌ 建立全新選單系統失敗: {e}")

def main():
    """主函數"""
    if len(sys.argv) != 2:
        print("駕駛視窗選單管理工具")
        print("使用方法: python manage_driver_menu.py <command>")
        print("\n可用命令:")
        print("  status    - 顯示選單狀態")
        print("  cleanup   - 清理舊選單")
        print("  refresh   - 強制刷新所有分頁")
        print("  clear     - 清空緩存")
        print("  validate  - 驗證緩存有效性")
        print("  fresh     - 建立全新選單系統")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "status":
            show_menu_status()
        elif command == "cleanup":
            cleanup_old_menus()
        elif command == "refresh":
            force_refresh_all()
        elif command == "clear":
            clear_cache()
        elif command == "validate":
            validate_cache()
        elif command == "fresh":
            setup_fresh_menus()
        else:
            print(f"❌ 未知命令: {command}")
            print("可用命令: status, cleanup, refresh, clear, validate, fresh")
    
    except KeyboardInterrupt:
        print("\n❌ 操作被中斷")
    except Exception as e:
        print(f"❌ 執行命令時發生錯誤: {e}")

if __name__ == "__main__":
    main() 