#!/usr/bin/env python3
"""
測試太陽、地球、月亮的多種樣式選擇
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.rich_menu_image_generator import RichMenuImageGenerator
from app.config.linebot_config import LineBotConfig

def test_multiple_styles():
    """測試太陽、地球、月亮的多種樣式"""
    
    # 確保輸出目錄存在
    os.makedirs("rich_menu_images", exist_ok=True)
    
    # 定義所有樣式組合
    style_combinations = [
        {
            "name": "經典組合",
            "sun_style": "classic",
            "earth_style": "classic", 
            "moon_style": "classic",
            "description": "經典傳統樣式，溫和友善"
        },
        {
            "name": "可愛組合",
            "sun_style": "cute",
            "earth_style": "kawaii",
            "moon_style": "kawaii",
            "description": "超可愛風格，粉嫩色彩"
        },
        {
            "name": "卡通組合",
            "sun_style": "cartoon",
            "earth_style": "detailed",
            "moon_style": "sleepy",
            "description": "卡通風格，細節豐富"
        },
        {
            "name": "現代組合",
            "sun_style": "modern",
            "earth_style": "eyes_only",
            "moon_style": "crescent",
            "description": "現代簡約風格，線條簡潔"
        },
        {
            "name": "特色組合",
            "sun_style": "kawaii",
            "earth_style": "with_arms",
            "moon_style": "mystical",
            "description": "特色創意風格，個性十足"
        }
    ]
    
    print("🌟 測試多種樣式組合...")
    
    for combo in style_combinations:
        print(f"  生成 {combo['name']} 樣式...")
        
        # 管理員選單按鈕配置 - 使用不同樣式
        admin_buttons = [
            {
                "text": "本週占卜", 
                "color": (255, 200, 100), 
                "planet": "太陽",
                "sun_style": combo["sun_style"]
            },
            {
                "text": "流年運勢", 
                "color": (100, 200, 255), 
                "planet": "地球",
                "earth_style": combo["earth_style"]
            },
            {
                "text": "流月運勢", 
                "color": (200, 200, 200), 
                "planet": "月球",
                "moon_style": combo["moon_style"]
            },
            {
                "text": "流日運勢", 
                "color": (70, 130, 180), 
                "planet": "海王星"
            },
            {
                "text": "命盤綁定", 
                "color": (255, 100, 100), 
                "planet": "火箭", 
                "rocket_style": "space_shuttle"
            },
            {
                "text": "會員資訊", 
                "color": (180, 180, 180), 
                "planet": "衛星"
            },
            {
                "text": "指定時間", 
                "color": (255, 215, 0), 
                "planet": "時鐘"
            }
        ]
        
        # 創建圖片生成器
        generator = RichMenuImageGenerator()
        
        # 生成星空背景
        background = generator.create_starry_background()
        
        # 生成按鈕位置（3區域分佈）
        button_positions = generator.generate_three_zone_positions(
            num_buttons=7,
            width=LineBotConfig.RICH_MENU_WIDTH,
            height=LineBotConfig.RICH_MENU_HEIGHT
        )
        
        # 在背景上繪製按鈕
        for i, button_config in enumerate(admin_buttons):
            if i < len(button_positions):
                # 創建按鈕圖片
                button_img, _ = generator.create_planet_button(button_config)
                
                # 計算按鈕位置
                x, y = button_positions[i]
                button_x = x - button_img.width // 2
                button_y = y - button_img.height // 2
                
                # 將按鈕貼到背景上
                background.paste(button_img, (button_x, button_y), button_img)
        
        # 保存圖片
        safe_name = combo["name"].replace(" ", "_")
        output_path = f"rich_menu_images/admin_menu_{safe_name}.png"
        background.save(output_path)
        print(f"    ✅ 已生成: {output_path}")

def test_individual_styles():
    """測試個別星球的所有樣式"""
    
    print("\n🎨 測試個別星球樣式...")
    
    # 太陽樣式
    sun_styles = ["classic", "cute", "cartoon", "modern", "kawaii"]
    for style in sun_styles:
        print(f"  生成太陽 {style} 樣式...")
        
        buttons = [
            {"text": "太陽", "color": (255, 200, 100), "planet": "太陽", "sun_style": style},
            {"text": "地球", "color": (100, 200, 255), "planet": "地球"},
            {"text": "月球", "color": (200, 200, 200), "planet": "月球"},
            {"text": "海王星", "color": (70, 130, 180), "planet": "海王星"},
            {"text": "火箭", "color": (255, 100, 100), "planet": "火箭"},
            {"text": "衛星", "color": (180, 180, 180), "planet": "衛星"},
            {"text": "時鐘", "color": (255, 215, 0), "planet": "時鐘"}
        ]
        
        generate_single_style_menu(buttons, f"sun_{style}")
    
    # 地球樣式
    earth_styles = ["classic", "detailed", "with_arms", "eyes_only", "kawaii"]
    for style in earth_styles:
        print(f"  生成地球 {style} 樣式...")
        
        buttons = [
            {"text": "太陽", "color": (255, 200, 100), "planet": "太陽"},
            {"text": "地球", "color": (100, 200, 255), "planet": "地球", "earth_style": style},
            {"text": "月球", "color": (200, 200, 200), "planet": "月球"},
            {"text": "海王星", "color": (70, 130, 180), "planet": "海王星"},
            {"text": "火箭", "color": (255, 100, 100), "planet": "火箭"},
            {"text": "衛星", "color": (180, 180, 180), "planet": "衛星"},
            {"text": "時鐘", "color": (255, 215, 0), "planet": "時鐘"}
        ]
        
        generate_single_style_menu(buttons, f"earth_{style}")
    
    # 月球樣式
    moon_styles = ["classic", "sleepy", "crescent", "kawaii", "mystical"]
    for style in moon_styles:
        print(f"  生成月球 {style} 樣式...")
        
        buttons = [
            {"text": "太陽", "color": (255, 200, 100), "planet": "太陽"},
            {"text": "地球", "color": (100, 200, 255), "planet": "地球"},
            {"text": "月球", "color": (200, 200, 200), "planet": "月球", "moon_style": style},
            {"text": "海王星", "color": (70, 130, 180), "planet": "海王星"},
            {"text": "火箭", "color": (255, 100, 100), "planet": "火箭"},
            {"text": "衛星", "color": (180, 180, 180), "planet": "衛星"},
            {"text": "時鐘", "color": (255, 215, 0), "planet": "時鐘"}
        ]
        
        generate_single_style_menu(buttons, f"moon_{style}")

def generate_single_style_menu(buttons, style_name):
    """生成單一樣式的選單"""
    
    # 創建圖片生成器
    generator = RichMenuImageGenerator()
    
    # 生成星空背景
    background = generator.create_starry_background()
    
    # 生成按鈕位置
    button_positions = generator.generate_three_zone_positions(
        num_buttons=7,
        width=LineBotConfig.RICH_MENU_WIDTH,
        height=LineBotConfig.RICH_MENU_HEIGHT
    )
    
    # 在背景上繪製按鈕
    for i, button_config in enumerate(buttons):
        if i < len(button_positions):
            # 創建按鈕圖片
            button_img, _ = generator.create_planet_button(button_config)
            
            # 計算按鈕位置
            x, y = button_positions[i]
            button_x = x - button_img.width // 2
            button_y = y - button_img.height // 2
            
            # 將按鈕貼到背景上
            background.paste(button_img, (button_x, button_y), button_img)
    
    # 保存圖片
    output_path = f"rich_menu_images/individual_{style_name}.png"
    background.save(output_path)

def generate_preview_html():
    """生成預覽 HTML 文件"""
    
    style_combinations = [
        {
            "name": "經典組合",
            "sun_style": "classic",
            "earth_style": "classic", 
            "moon_style": "classic",
            "description": "經典傳統樣式，溫和友善"
        },
        {
            "name": "可愛組合",
            "sun_style": "cute",
            "earth_style": "kawaii",
            "moon_style": "kawaii",
            "description": "超可愛風格，粉嫩色彩"
        },
        {
            "name": "卡通組合",
            "sun_style": "cartoon",
            "earth_style": "detailed",
            "moon_style": "sleepy",
            "description": "卡通風格，細節豐富"
        },
        {
            "name": "現代組合",
            "sun_style": "modern",
            "earth_style": "eyes_only",
            "moon_style": "crescent",
            "description": "現代簡約風格，線條簡潔"
        },
        {
            "name": "特色組合",
            "sun_style": "kawaii",
            "earth_style": "with_arms",
            "moon_style": "mystical",
            "description": "特色創意風格，個性十足"
        }
    ]
    
    sun_styles = [
        ("classic", "經典太陽", "改善光芒比例，溫暖友善"),
        ("cute", "可愛太陽", "粉嫩色彩，超萌表情"),
        ("cartoon", "卡通太陽", "豐富表情，活潑動感"),
        ("modern", "現代太陽", "簡約線條，科技感"),
        ("kawaii", "日式太陽", "日式可愛風格")
    ]
    
    earth_styles = [
        ("classic", "經典地球", "傳統地球樣式"),
        ("detailed", "詳細地球", "豐富細節和大氣層"),
        ("with_arms", "手腳地球", "可愛手腳造型"),
        ("eyes_only", "眼睛地球", "只有眼睛的簡潔風格"),
        ("kawaii", "日式地球", "日式可愛風格")
    ]
    
    moon_styles = [
        ("classic", "經典月球", "去除背景圓圈的傳統月球"),
        ("sleepy", "睡覺月球", "睡眠表情和ZZZ符號"),
        ("crescent", "新月造型", "彎月造型設計"),
        ("kawaii", "日式月球", "日式可愛風格"),
        ("mystical", "神秘月球", "神秘魔法風格")
    ]
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 多種樣式選擇預覽</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            font-size: 2em;
            margin-bottom: 20px;
            color: #FFD700;
            text-align: center;
        }}
        
        .combo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .combo-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .combo-card h3 {{
            color: #4ECDC4;
            margin-bottom: 15px;
        }}
        
        .combo-card img {{
            width: 100%;
            height: auto;
            border-radius: 15px;
            margin-bottom: 15px;
        }}
        
        .style-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .style-card {{
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
        }}
        
        .style-card h4 {{
            color: #FF6B6B;
            margin-bottom: 10px;
        }}
        
        .style-card img {{
            width: 100%;
            height: auto;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
        
        .highlight {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            padding: 20px;
            border-radius: 15px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .feature-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        
        .emoji {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 多種樣式選擇預覽</h1>
            <p>太陽、地球、月亮的多種設計風格</p>
        </div>
        
        <div class="highlight">
            <h2>✨ 樣式組合選單</h2>
            <p>不同風格的完美搭配，為您的LINE Bot選單增添個性</p>
        </div>
        
        <div class="section">
            <h2>🎨 樣式組合</h2>
            <div class="combo-grid">
"""
    
    for combo in style_combinations:
        safe_name = combo["name"].replace(" ", "_")
        html_content += f"""
                <div class="combo-card">
                    <h3>{combo["name"]}</h3>
                    <img src="rich_menu_images/admin_menu_{safe_name}.png" alt="{combo['name']}">
                    <p>{combo["description"]}</p>
                    <div style="font-size: 0.9em; opacity: 0.8;">
                        太陽: {combo["sun_style"]} | 地球: {combo["earth_style"]} | 月球: {combo["moon_style"]}
                    </div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="section">
            <h2>☀️ 太陽樣式</h2>
            <div class="style-grid">
"""
    
    for style_name, style_desc, description in sun_styles:
        html_content += f"""
                <div class="style-card">
                    <h4>{style_desc}</h4>
                    <img src="rich_menu_images/individual_sun_{style_name}.png" alt="{style_desc}">
                    <p>{description}</p>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="section">
            <h2>🌍 地球樣式</h2>
            <div class="style-grid">
"""
    
    for style_name, style_desc, description in earth_styles:
        html_content += f"""
                <div class="style-card">
                    <h4>{style_desc}</h4>
                    <img src="rich_menu_images/individual_earth_{style_name}.png" alt="{style_desc}">
                    <p>{description}</p>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="section">
            <h2>🌙 月球樣式</h2>
            <div class="style-grid">
"""
    
    for style_name, style_desc, description in moon_styles:
        html_content += f"""
                <div class="style-card">
                    <h4>{style_desc}</h4>
                    <img src="rich_menu_images/individual_moon_{style_name}.png" alt="{style_desc}">
                    <p>{description}</p>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="emoji">🎨</div>
                <h4>多樣化設計</h4>
                <p>每個星球都有5種不同樣式，總共15種設計選擇</p>
            </div>
            <div class="feature-card">
                <div class="emoji">🌟</div>
                <h4>完美搭配</h4>
                <p>精心設計的樣式組合，確保視覺和諧統一</p>
            </div>
            <div class="feature-card">
                <div class="emoji">✨</div>
                <h4>個性化選擇</h4>
                <p>從經典到可愛，從現代到神秘，滿足不同喜好</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open("multiple_styles_preview.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("\n✅ 預覽 HTML 文件已生成: multiple_styles_preview.html")

def main():
    """主函數"""
    print("🚀 開始測試多種樣式選擇...")
    
    # 測試樣式組合
    test_multiple_styles()
    
    # 測試個別樣式
    test_individual_styles()
    
    # 生成預覽 HTML
    generate_preview_html()
    
    print("\n🎉 所有測試完成！")
    print("📁 生成的文件:")
    print("   - rich_menu_images/admin_menu_*.png (樣式組合)")
    print("   - rich_menu_images/individual_*.png (個別樣式)")
    print("   - multiple_styles_preview.html (預覽頁面)")

if __name__ == "__main__":
    main() 