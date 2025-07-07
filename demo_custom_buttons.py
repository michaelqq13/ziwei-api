#!/usr/bin/env python3
"""
自定義按鈕生成器示範腳本
展示如何使用用戶提供的圖片創建Rich Menu按鈕
"""

import os
from app.utils.custom_button_generator import CustomButtonGenerator, create_custom_button_example

def demo_basic_usage():
    """基本使用示範"""
    print("🎨 自定義按鈕生成器示範")
    print("=" * 50)
    
    generator = CustomButtonGenerator()
    
    # 創建示範目錄
    os.makedirs("user_images", exist_ok=True)
    os.makedirs("demo_output", exist_ok=True)
    
    print("\n📝 使用說明:")
    print("1. 將您的圖片放在 'user_images' 資料夾中")
    print("2. 支援的格式: PNG, JPG, JPEG, GIF")
    print("3. 建議圖片大小: 200x200 像素以上")
    print("4. 圖片會自動調整大小並保持比例")
    
    # 檢查是否有用戶圖片
    user_images_dir = "user_images"
    if os.path.exists(user_images_dir):
        image_files = [f for f in os.listdir(user_images_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if image_files:
            print(f"\n🖼️  找到 {len(image_files)} 張圖片:")
            for img in image_files:
                print(f"   - {img}")
            
            # 為每張圖片創建按鈕
            configs = []
            for i, img_file in enumerate(image_files[:6]):  # 最多6個按鈕
                configs.append({
                    'image_path': os.path.join(user_images_dir, img_file),
                    'button_text': f'按鈕{i+1}',
                    'output_name': f'custom_button_{i+1}.png',
                    'text_color': (255, 255, 255)
                })
            
            print(f"\n🔧 正在創建 {len(configs)} 個按鈕...")
            button_paths = generator.create_button_set_from_images(configs, "demo_output")
            
            print(f"\n✅ 按鈕創建完成! 檔案位置:")
            for path in button_paths:
                print(f"   - {path}")
            
            # 創建Rich Menu
            print(f"\n🎯 正在創建Rich Menu...")
            button_configs = [
                {"action": {"type": "message", "text": f"用戶按鈕{i+1}被點擊"}}
                for i in range(len(configs))
            ]
            
            menu_path, button_areas = generator.integrate_with_rich_menu(
                button_paths, button_configs, "user_custom"
            )
            
            print(f"✅ Rich Menu創建完成: {menu_path}")
            print(f"📊 按鈕區域數量: {len(button_areas)}")
            
            return menu_path, button_areas
        
        else:
            print(f"\n⚠️  在 '{user_images_dir}' 中沒有找到圖片檔案")
            print("請將您的圖片放入該資料夾後重新執行")
    
    else:
        print(f"\n⚠️  '{user_images_dir}' 資料夾不存在")
        print("已自動創建，請將您的圖片放入該資料夾")
    
    return None, []

def demo_advanced_usage():
    """進階使用示範"""
    print("\n🚀 進階功能示範")
    print("=" * 50)
    
    generator = CustomButtonGenerator()
    
    # 進階配置示範
    advanced_configs = [
        {
            'image_path': 'user_images/icon1.png',
            'button_text': '主要功能',
            'output_name': 'main_feature.png',
            'text_color': (255, 255, 100),  # 黃色文字
            'button_size': (250, 250),      # 大尺寸按鈕
            'add_background': True,
            'add_border': True,
            'add_shadow': True
        },
        {
            'image_path': 'user_images/icon2.png',
            'button_text': '次要功能',
            'output_name': 'secondary_feature.png',
            'text_color': (100, 255, 100),  # 綠色文字
            'button_size': (200, 200),      # 標準尺寸
            'add_background': True,
            'add_border': False,            # 無邊框
            'add_shadow': True
        },
        {
            'image_path': 'user_images/icon3.png',
            'button_text': '簡約風格',
            'output_name': 'minimal_style.png',
            'text_color': (255, 255, 255),
            'button_size': (180, 180),      # 小尺寸
            'add_background': False,        # 無背景
            'add_border': False,            # 無邊框
            'add_shadow': False             # 無陰影
        }
    ]
    
    print("🎨 進階配置選項:")
    print("- 自定義按鈕尺寸")
    print("- 自定義文字顏色")
    print("- 選擇性添加背景、邊框、陰影")
    print("- 批量處理多張圖片")
    
    # 檢查圖片是否存在
    available_configs = []
    for config in advanced_configs:
        if os.path.exists(config['image_path']):
            available_configs.append(config)
    
    if available_configs:
        print(f"\n🔧 找到 {len(available_configs)} 張圖片，正在處理...")
        button_paths = generator.create_button_set_from_images(
            available_configs, "demo_output/advanced"
        )
        
        print("✅ 進階按鈕創建完成!")
        return button_paths
    else:
        print("\n⚠️  沒有找到對應的圖片檔案")
        print("請確保以下檔案存在:")
        for config in advanced_configs:
            print(f"   - {config['image_path']}")
    
    return []

def create_sample_images():
    """創建示範圖片（如果用戶沒有提供圖片）"""
    print("\n🎭 創建示範圖片")
    print("=" * 30)
    
    from PIL import Image, ImageDraw
    import random
    
    os.makedirs("user_images", exist_ok=True)
    
    # 創建幾個簡單的示範圖片
    sample_configs = [
        {"name": "heart.png", "color": (255, 100, 100), "shape": "heart"},
        {"name": "star.png", "color": (255, 255, 100), "shape": "star"},
        {"name": "diamond.png", "color": (100, 255, 255), "shape": "diamond"},
    ]
    
    for config in sample_configs:
        img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if config["shape"] == "heart":
            # 簡單的心形
            draw.ellipse([50, 60, 100, 110], fill=config["color"])
            draw.ellipse([100, 60, 150, 110], fill=config["color"])
            draw.polygon([(75, 100), (125, 100), (100, 140)], fill=config["color"])
        
        elif config["shape"] == "star":
            # 五角星
            center_x, center_y = 100, 100
            points = []
            for i in range(10):
                angle = i * 36 * 3.14159 / 180
                if i % 2 == 0:
                    radius = 40
                else:
                    radius = 20
                x = center_x + radius * math.cos(angle - 3.14159/2)
                y = center_y + radius * math.sin(angle - 3.14159/2)
                points.append((x, y))
            draw.polygon(points, fill=config["color"])
        
        elif config["shape"] == "diamond":
            # 菱形
            draw.polygon([(100, 50), (150, 100), (100, 150), (50, 100)], 
                        fill=config["color"])
        
        img_path = os.path.join("user_images", config["name"])
        img.save(img_path)
        print(f"✅ 創建示範圖片: {img_path}")
    
    print("🎉 示範圖片創建完成!")

def main():
    """主程式"""
    print("🎨 自定義按鈕生成器")
    print("=" * 50)
    print("這個工具可以將您的圖片轉換為LINE Rich Menu按鈕")
    print()
    
    # 檢查是否有用戶圖片
    if not os.path.exists("user_images") or not os.listdir("user_images"):
        print("🤔 沒有找到用戶圖片，要創建示範圖片嗎？")
        response = input("輸入 'y' 創建示範圖片，或直接按Enter跳過: ").strip().lower()
        
        if response == 'y':
            create_sample_images()
            print()
    
    # 基本使用示範
    menu_path, button_areas = demo_basic_usage()
    
    # 進階使用示範
    advanced_buttons = demo_advanced_usage()
    
    print("\n" + "=" * 50)
    print("🎯 使用總結:")
    print("1. 將圖片放入 'user_images' 資料夾")
    print("2. 執行此腳本自動生成按鈕")
    print("3. 生成的按鈕會保存在 'demo_output' 資料夾")
    print("4. Rich Menu圖片會保存在 'rich_menu_images' 資料夾")
    
    if menu_path:
        print(f"\n✅ 成功創建Rich Menu: {menu_path}")
        print("📱 可以直接上傳到LINE Bot使用!")
    
    print("\n💡 提示:")
    print("- 支援PNG、JPG、JPEG、GIF格式")
    print("- 圖片會自動調整大小並保持比例")
    print("- 可以自定義按鈕樣式和文字顏色")
    print("- 最多支援9個按鈕")

if __name__ == "__main__":
    import math
    main() 