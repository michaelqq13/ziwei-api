#!/usr/bin/env python3
"""
Rich Menu 生成模式管理腳本
讓用戶可以輕鬆切換圖片資源型和程式生成型，並重新生成選單
"""
import os
import sys
from pathlib import Path
import argparse

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.rich_menu_manager import RichMenuManager
from app.utils.image_based_rich_menu_generator import ImageBasedRichMenuGenerator

def show_current_status():
    """顯示當前狀態"""
    print("📊 當前 Rich Menu 狀態")
    print("-" * 40)
    
    # 檢查圖片資源目錄
    image_generator = ImageBasedRichMenuGenerator()
    config_path = os.path.join(image_generator.image_base_path, "button_image_config.json")
    
    if os.path.exists(config_path):
        print(f"✅ 圖片資源配置：{config_path}")
        
        # 檢查圖片文件
        button_images = image_generator.button_image_mapping.get("button_images", {})
        available_images = 0
        for button_name, config in button_images.items():
            image_file = config.get("image_file", "")
            image_path = os.path.join(image_generator.image_base_path, image_file)
            if os.path.exists(image_path):
                available_images += 1
        
        print(f"📁 可用圖片：{available_images}/{len(button_images)}")
    else:
        print("❌ 圖片資源配置不存在")
    
    # 檢查現有 Rich Menu
    try:
        manager = RichMenuManager()
        menus = manager.get_rich_menu_list()
        if menus:
            print(f"📋 現有選單數量：{len(menus)}")
            for menu in menus:
                print(f"   - {menu.get('name', 'Unknown')}: {menu.get('richMenuId', 'Unknown')}")
        else:
            print("📋 沒有現有選單")
    except Exception as e:
        print(f"❌ 無法檢查現有選單：{e}")

def generate_menu_with_mode(mode: str, user_level: str = "member", force: bool = False):
    """使用指定模式生成選單"""
    use_image_based = (mode == "image")
    
    print(f"\n🎨 使用 {'圖片資源型' if use_image_based else '程式生成型'} 生成 {user_level} 選單...")
    
    try:
        manager = RichMenuManager(use_image_based=use_image_based)
        
        if user_level == "admin":
            menu_id = manager.setup_admin_rich_menu(force_recreate=force)
        else:
            menu_id = manager.setup_complete_rich_menu(force_recreate=force)
        
        if menu_id:
            print(f"✅ 選單生成成功！ID: {menu_id}")
            return menu_id
        else:
            print("❌ 選單生成失敗")
            return None
            
    except Exception as e:
        print(f"❌ 生成選單時發生錯誤：{e}")
        return None

def compare_modes():
    """比較兩種生成模式"""
    print("\n🔍 比較兩種生成模式")
    print("=" * 50)
    
    # 生成圖片資源型選單
    print("\n1️⃣ 測試圖片資源型生成器...")
    try:
        from app.utils.image_based_rich_menu_generator import generate_image_based_rich_menu
        image_path, button_areas = generate_image_based_rich_menu("member", "rich_menu_images/test_image_based.png")
        print(f"✅ 圖片資源型：{image_path}")
        print(f"   按鈕數量：{len(button_areas)}")
    except Exception as e:
        print(f"❌ 圖片資源型生成失敗：{e}")
    
    # 生成程式生成型選單
    print("\n2️⃣ 測試程式生成型生成器...")
    try:
        from app.utils.rich_menu_image_generator import generate_starry_rich_menu
        image_path, button_areas = generate_starry_rich_menu("rich_menu_images/test_programmatic.png")
        print(f"✅ 程式生成型：{image_path}")
        print(f"   按鈕數量：{len(button_areas)}")
    except Exception as e:
        print(f"❌ 程式生成型生成失敗：{e}")

def setup_image_resources():
    """設定圖片資源"""
    print("\n🖼️ 設定圖片資源")
    print("-" * 30)
    
    # 初始化圖片資源生成器
    generator = ImageBasedRichMenuGenerator()
    
    print(f"✅ 圖片資源目錄：{generator.image_base_path}")
    
    # 檢查配置文件
    config_path = os.path.join(generator.image_base_path, "button_image_config.json")
    if os.path.exists(config_path):
        print(f"✅ 配置文件：{config_path}")
    else:
        print(f"❌ 配置文件不存在：{config_path}")
    
    # 檢查說明文件
    readme_path = os.path.join(generator.image_base_path, "README.md")
    if os.path.exists(readme_path):
        print(f"✅ 說明文件：{readme_path}")
    else:
        print(f"❌ 說明文件不存在：{readme_path}")
    
    print("\n📋 按鈕圖片狀態：")
    button_images = generator.button_image_mapping.get("button_images", {})
    for button_name, config in button_images.items():
        image_file = config.get("image_file", "")
        image_path = os.path.join(generator.image_base_path, image_file)
        exists = "✅" if os.path.exists(image_path) else "❌"
        print(f"  {exists} {button_name}: {image_file}")
        if not os.path.exists(image_path):
            print(f"      → 請將圖片放置在：{image_path}")

def cleanup_old_menus():
    """清理舊選單"""
    print("\n🧹 清理舊選單")
    print("-" * 20)
    
    try:
        manager = RichMenuManager()
        
        # 獲取現有選單
        menus = manager.get_rich_menu_list()
        if not menus:
            print("📋 沒有需要清理的選單")
            return
        
        print(f"📋 找到 {len(menus)} 個選單")
        
        # 獲取當前預設選單
        default_menu_id = manager.get_default_rich_menu_id()
        
        # 清理舊選單
        cleaned_count = manager.cleanup_old_rich_menus(default_menu_id)
        print(f"✅ 已清理 {cleaned_count} 個舊選單")
        
    except Exception as e:
        print(f"❌ 清理選單時發生錯誤：{e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Rich Menu 生成模式管理")
    parser.add_argument("--mode", choices=["image", "programmatic"], 
                       help="生成模式：image（圖片資源型）或 programmatic（程式生成型）")
    parser.add_argument("--level", choices=["member", "admin"], default="member",
                       help="用戶等級：member（會員）或 admin（管理員）")
    parser.add_argument("--force", action="store_true", 
                       help="強制重新生成選單")
    parser.add_argument("--compare", action="store_true",
                       help="比較兩種生成模式")
    parser.add_argument("--setup", action="store_true",
                       help="設定圖片資源")
    parser.add_argument("--cleanup", action="store_true",
                       help="清理舊選單")
    parser.add_argument("--status", action="store_true",
                       help="顯示當前狀態")
    
    args = parser.parse_args()
    
    print("🌟 Rich Menu 生成模式管理工具")
    print("=" * 50)
    
    # 顯示當前狀態
    if args.status or len(sys.argv) == 1:
        show_current_status()
    
    # 設定圖片資源
    if args.setup:
        setup_image_resources()
    
    # 比較模式
    if args.compare:
        compare_modes()
    
    # 清理舊選單
    if args.cleanup:
        cleanup_old_menus()
    
    # 生成選單
    if args.mode:
        menu_id = generate_menu_with_mode(args.mode, args.level, args.force)
        if menu_id:
            print(f"\n✅ 選單已設定為預設選單：{menu_id}")
    
    # 顯示使用提示
    if len(sys.argv) == 1:
        print("\n📖 使用說明：")
        print("python scripts/manage_rich_menu_mode.py --mode image --level member    # 使用圖片資源型生成會員選單")
        print("python scripts/manage_rich_menu_mode.py --mode programmatic --level admin  # 使用程式生成型生成管理員選單")
        print("python scripts/manage_rich_menu_mode.py --compare                      # 比較兩種模式")
        print("python scripts/manage_rich_menu_mode.py --setup                        # 設定圖片資源")
        print("python scripts/manage_rich_menu_mode.py --cleanup                      # 清理舊選單")
        print("python scripts/manage_rich_menu_mode.py --status                       # 顯示狀態")

if __name__ == "__main__":
    main() 