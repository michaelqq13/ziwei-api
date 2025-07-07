#!/usr/bin/env python3
"""
分頁式 Rich Menu 管理工具
支援多種邊界樣式和完整的管理功能
"""

import argparse
import os
import webbrowser
from app.utils.tabbed_rich_menu_generator import (
    generate_tabbed_rich_menu, 
    get_available_border_styles,
    set_default_border_style
)

def show_status():
    """顯示系統狀態"""
    print("📊 分頁式 Rich Menu 系統狀態")
    print("=" * 40)
    
    # 檢查圖片目錄
    image_dir = "rich_menu_images"
    if os.path.exists(image_dir):
        files = [f for f in os.listdir(image_dir) if f.startswith("tabbed_menu_")]
        print(f"📁 圖片目錄: {image_dir}")
        print(f"📄 已生成選單: {len(files)} 個")
        
        if files:
            print("\n📋 現有選單文件:")
            for file in sorted(files):
                file_path = os.path.join(image_dir, file)
                size = os.path.getsize(file_path) / 1024
                print(f"   📱 {file} ({size:.1f} KB)")
    else:
        print("📁 圖片目錄不存在")
    
    # 顯示可用的邊界樣式
    border_styles = get_available_border_styles()
    print(f"\n🎨 可用邊界樣式: {', '.join(border_styles)}")
    
    print("\n✅ 系統狀態檢查完成")

def setup_menu(user_level, tab, border_style="soft_glow"):
    """設定分頁選單"""
    print(f"🛠️ 設定分頁選單")
    print(f"   用戶等級: {user_level}")
    print(f"   活躍分頁: {tab}")
    print(f"   邊界樣式: {border_style}")
    print("-" * 30)
    
    try:
        image_path, button_areas = generate_tabbed_rich_menu(tab, user_level, border_style)
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path) / 1024
            print(f"✅ 選單設定成功")
            print(f"   📁 路徑: {image_path}")
            print(f"   📏 尺寸: (2500, 1686)")
            print(f"   💾 大小: {file_size:.1f} KB")
            print(f"   🎯 按鈕數量: {len(button_areas)}")
            return True
        else:
            print("❌ 選單設定失敗：找不到生成的圖片")
            return False
            
    except Exception as e:
        print(f"❌ 選單設定失敗：{e}")
        return False

def preview_menu(user_level, tab, border_style="soft_glow"):
    """預覽分頁選單"""
    print(f"🖼️ 預覽分頁選單")
    print(f"   用戶等級: {user_level}")
    print(f"   活躍分頁: {tab}")
    print(f"   邊界樣式: {border_style}")
    print("-" * 30)
    
    try:
        image_path, button_areas = generate_tabbed_rich_menu(tab, user_level, border_style)
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path) / 1024
            print(f"✅ 選單預覽生成成功")
            print(f"   📁 路徑: {image_path}")
            print(f"   📏 尺寸: (2500, 1686)")
            print(f"   💾 大小: {file_size:.1f} KB")
            print(f"   🎯 按鈕數量: {len(button_areas)}")
            
            # 創建預覽HTML
            preview_file = create_preview_html(image_path, user_level, tab, border_style)
            print(f"   📋 預覽文件: {preview_file}")
            
            # 自動在瀏覽器中打開
            webbrowser.open(f"file://{os.path.abspath(preview_file)}")
            
            return True
        else:
            print("❌ 預覽生成失敗：找不到生成的圖片")
            return False
            
    except Exception as e:
        print(f"❌ 預覽生成失敗：{e}")
        return False

def create_preview_html(image_path, user_level, tab, border_style):
    """創建預覽HTML文件"""
    image_name = os.path.basename(image_path)
    preview_name = f"preview_tabbed_{tab}_{user_level}_{border_style}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>分頁選單預覽 - {user_level.upper()} / {tab.upper()} / {border_style.upper()}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .info {{
            background: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .image-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .menu-image {{
            max-width: 100%;
            border: 2px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .style-info {{
            background: #f0f8ff;
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 分頁選單預覽</h1>
            <h2>{user_level.upper()} 用戶 - {tab.upper()} 分頁</h2>
        </div>
        
        <div class="info">
            <h3>📋 選單資訊</h3>
            <p><strong>用戶等級:</strong> {user_level}</p>
            <p><strong>活躍分頁:</strong> {tab}</p>
            <p><strong>邊界樣式:</strong> {border_style}</p>
            <p><strong>圖片路徑:</strong> {image_path}</p>
        </div>
        
        <div class="image-container">
            <img src="{image_name}" alt="分頁選單" class="menu-image">
        </div>
        
        <div class="style-info">
            <h3>🎨 邊界樣式說明</h3>
            <p><strong>{border_style.upper().replace('_', ' ')}:</strong> 
            {'柔和發光效果，活躍分頁底部有微妙發光' if border_style == 'soft_glow' else
             '微妙分隔線，分頁間有漸變分隔線' if border_style == 'subtle_separator' else
             '漸變邊界，活躍分頁底部有漸變邊界' if border_style == 'gradient' else
             '完全無邊框，純粹依靠背景亮度區分' if border_style == 'no_border' else
             '未知樣式'}
            </p>
        </div>
    </div>
</body>
</html>"""
    
    with open(preview_name, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return preview_name

def compare_border_styles(user_level, tab):
    """比較不同邊界樣式的效果"""
    print(f"🔍 比較邊界樣式效果")
    print(f"   用戶等級: {user_level}")
    print(f"   活躍分頁: {tab}")
    print("-" * 30)
    
    border_styles = get_available_border_styles()
    generated_images = []
    
    # 生成所有樣式的圖片
    for style in border_styles:
        try:
            image_path, button_areas = generate_tabbed_rich_menu(tab, user_level, style)
            if os.path.exists(image_path):
                file_size = os.path.getsize(image_path) / 1024
                print(f"✅ {style}: {file_size:.1f} KB")
                generated_images.append((style, image_path, file_size))
            else:
                print(f"❌ {style}: 生成失敗")
        except Exception as e:
            print(f"❌ {style}: {e}")
    
    if generated_images:
        # 創建比較預覽
        comparison_file = create_comparison_html(generated_images, user_level, tab)
        print(f"\n📋 比較預覽文件: {comparison_file}")
        webbrowser.open(f"file://{os.path.abspath(comparison_file)}")
        return True
    else:
        print("❌ 沒有成功生成任何圖片")
        return False

def create_comparison_html(images, user_level, tab):
    """創建比較預覽HTML文件"""
    preview_name = f"comparison_tabbed_{tab}_{user_level}.html"
    
    image_html = ""
    for style, image_path, file_size in images:
        image_name = os.path.basename(image_path)
        style_desc = {
            'soft_glow': '柔和發光效果，活躍分頁底部有微妙發光',
            'subtle_separator': '微妙分隔線，分頁間有漸變分隔線',
            'gradient': '漸變邊界，活躍分頁底部有漸變邊界',
            'no_border': '完全無邊框，純粹依靠背景亮度區分'
        }.get(style, '未知樣式')
        
        image_html += f"""
        <div class="style-section">
            <h3>🎨 {style.upper().replace('_', ' ')} ({file_size:.1f} KB)</h3>
            <p>{style_desc}</p>
            <img src="{image_name}" alt="{style}" class="menu-image">
        </div>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>邊界樣式比較 - {user_level.upper()} / {tab.upper()}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .style-section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background: #fafafa;
        }}
        .menu-image {{
            max-width: 100%;
            border: 2px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 邊界樣式比較</h1>
            <h2>{user_level.upper()} 用戶 - {tab.upper()} 分頁</h2>
        </div>
        
        {image_html}
    </div>
</body>
</html>"""
    
    with open(preview_name, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return preview_name

def cleanup_old_menus():
    """清理舊的選單文件"""
    print("🧹 清理舊選單文件")
    print("-" * 20)
    
    image_dir = "rich_menu_images"
    if not os.path.exists(image_dir):
        print("📁 圖片目錄不存在")
        return
    
    files = [f for f in os.listdir(image_dir) if f.startswith("tabbed_menu_")]
    
    if not files:
        print("📄 沒有找到舊選單文件")
        return
    
    print(f"📄 找到 {len(files)} 個選單文件")
    
    for file in files:
        file_path = os.path.join(image_dir, file)
        try:
            os.remove(file_path)
            print(f"🗑️ 已刪除: {file}")
        except Exception as e:
            print(f"❌ 刪除失敗 {file}: {e}")
    
    print("✅ 清理完成")

def main():
    parser = argparse.ArgumentParser(description="分頁式 Rich Menu 管理工具")
    parser.add_argument("--status", action="store_true", help="顯示系統狀態")
    parser.add_argument("--setup", help="設定選單 (格式: user_level:tab[:border_style])")
    parser.add_argument("--preview", help="預覽選單 (格式: user_level:tab[:border_style])")
    parser.add_argument("--compare", help="比較邊界樣式 (格式: user_level:tab)")
    parser.add_argument("--cleanup", action="store_true", help="清理舊選單文件")
    parser.add_argument("--set-default-style", help="設置默認邊界樣式")
    parser.add_argument("--list-styles", action="store_true", help="列出可用邊界樣式")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.setup:
        parts = args.setup.split(':')
        if len(parts) >= 2:
            user_level = parts[0]
            tab = parts[1]
            border_style = parts[2] if len(parts) > 2 else "soft_glow"
            setup_menu(user_level, tab, border_style)
        else:
            print("❌ 格式錯誤。請使用: user_level:tab[:border_style]")
    elif args.preview:
        parts = args.preview.split(':')
        if len(parts) >= 2:
            user_level = parts[0]
            tab = parts[1]
            border_style = parts[2] if len(parts) > 2 else "soft_glow"
            preview_menu(user_level, tab, border_style)
        else:
            print("❌ 格式錯誤。請使用: user_level:tab[:border_style]")
    elif args.compare:
        parts = args.compare.split(':')
        if len(parts) >= 2:
            user_level = parts[0]
            tab = parts[1]
            compare_border_styles(user_level, tab)
        else:
            print("❌ 格式錯誤。請使用: user_level:tab")
    elif args.cleanup:
        cleanup_old_menus()
    elif args.set_default_style:
        set_default_border_style(args.set_default_style)
    elif args.list_styles:
        styles = get_available_border_styles()
        print("🎨 可用的邊界樣式:")
        for style in styles:
            desc = {
                'soft_glow': '柔和發光效果',
                'subtle_separator': '微妙分隔線',
                'gradient': '漸變邊界',
                'no_border': '無邊框'
            }.get(style, '未知樣式')
            print(f"   🎨 {style}: {desc}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 