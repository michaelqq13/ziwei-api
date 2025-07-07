#!/usr/bin/env python3
"""
簡化測試腳本 - 測試基本的太陽、地球、月亮樣式
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.rich_menu_image_generator import RichMenuImageGenerator

def simple_test():
    """簡化測試"""
    
    # 確保輸出目錄存在
    os.makedirs("rich_menu_images", exist_ok=True)
    
    # 創建圖片生成器
    generator = RichMenuImageGenerator()
    
    # 測試基本按鈕
    test_buttons = [
        {"text": "太陽", "color": (255, 200, 100), "planet": "太陽", "sun_style": "classic"},
        {"text": "地球", "color": (100, 200, 255), "planet": "地球", "earth_style": "classic"},
        {"text": "月球", "color": (200, 200, 200), "planet": "月球", "moon_style": "classic"},
    ]
    
    for i, button_config in enumerate(test_buttons):
        try:
            print(f"測試按鈕 {i+1}: {button_config['text']}")
            button_img, _ = generator.create_planet_button(button_config)
            
            # 保存單個按鈕圖片
            output_path = f"rich_menu_images/test_button_{i+1}_{button_config['text']}.png"
            button_img.save(output_path)
            print(f"  ✅ 成功生成: {output_path}")
            
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    simple_test() 