#!/usr/bin/env python3
"""
測試新的火箭造型和海王星設計
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.rich_menu_image_generator import RichMenuImageGenerator, generate_admin_starry_rich_menu
from app.config.linebot_config import LineBotConfig

def test_rocket_styles():
    """測試不同的火箭造型"""
    
    # 確保輸出目錄存在
    os.makedirs("rich_menu_images", exist_ok=True)
    
    rocket_styles = [
        ("classic", "經典火箭"),
        ("cartoon", "卡通火箭"),
        ("retro", "復古火箭"),
        ("modern", "現代火箭"),
        ("space_shuttle", "太空梭"),
        ("mini_rocket", "迷你火箭")
    ]
    
    print("🚀 測試不同火箭造型...")
    
    for style_name, style_desc in rocket_styles:
        print(f"  生成 {style_desc} 造型...")
        
        # 管理員選單按鈕配置
        admin_buttons = [
            {"text": "本週占卜", "color": (255, 200, 100), "planet": "太陽"},
            {"text": "流年運勢", "color": (100, 200, 255), "planet": "地球"},
            {"text": "流月運勢", "color": (200, 200, 200), "planet": "月球"},
            {"text": "流日運勢", "color": (70, 130, 180), "planet": "海王星"},  # 新的海王星
            {"text": "命盤綁定", "color": (255, 100, 100), "planet": "火箭", "rocket_style": style_name},  # 不同火箭造型
            {"text": "會員資訊", "color": (180, 180, 180), "planet": "衛星"},
            {"text": "指定時間", "color": (255, 215, 0), "planet": "時鐘"}
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
        output_path = f"rich_menu_images/admin_menu_{style_name}.png"
        background.save(output_path)
        print(f"    ✅ 已生成: {output_path}")

def generate_preview_html():
    """生成預覽 HTML 文件"""
    
    rocket_styles = [
        ("classic", "經典火箭", "三角頭 + 圓柱身體 + 尾翼，傳統火箭造型"),
        ("cartoon", "卡通火箭", "圓潤可愛風格，彩色條紋，大眼睛"),
        ("retro", "復古火箭", "50年代科幻風格，流線型設計"),
        ("modern", "現代火箭", "現代科技感，簡潔設計"),
        ("space_shuttle", "太空梭", "扁平寬體設計，多推進器"),
        ("mini_rocket", "迷你火箭", "小巧可愛風格，超大眼睛")
    ]
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 新火箭造型與海王星設計預覽</title>
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
            max-width: 1200px;
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
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .rocket-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 50px;
        }}
        
        .rocket-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }}
        
        .rocket-card:hover {{
            transform: translateY(-5px);
        }}
        
        .rocket-card h3 {{
            color: #FFD700;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        
        .rocket-card img {{
            width: 100%;
            height: auto;
            border-radius: 15px;
            margin-bottom: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }}
        
        .rocket-description {{
            font-size: 0.9em;
            opacity: 0.9;
            line-height: 1.6;
        }}
        
        .highlight {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            padding: 20px;
            border-radius: 15px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .highlight h2 {{
            margin-bottom: 15px;
            font-size: 1.8em;
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
        
        .feature-card h4 {{
            color: #4ECDC4;
            margin-bottom: 10px;
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
            <h1>🚀 新火箭造型與海王星設計</h1>
            <p>為您提供多種火箭造型選擇，以及全新的海王星設計</p>
        </div>
        
        <div class="highlight">
            <h2>🌟 設計更新重點</h2>
            <div class="features">
                <div class="feature-card">
                    <div class="emoji">🚀</div>
                    <h4>6種火箭造型</h4>
                    <p>從經典到現代，從可愛到科幻，滿足不同喜好</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">🌊</div>
                    <h4>海王星設計</h4>
                    <p>深藍色星球配精緻環帶，溫和友善的表情</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">✨</div>
                    <h4>一體成型</h4>
                    <p>所有設計都是完整一體，沒有拼接感</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">😊</div>
                    <h4>可愛表情</h4>
                    <p>每個設計都有獨特的可愛表情和個性</p>
                </div>
            </div>
        </div>
        
        <div class="rocket-grid">
"""
    
    for style_name, style_desc, description in rocket_styles:
        html_content += f"""
            <div class="rocket-card">
                <h3>🚀 {style_desc}</h3>
                <img src="admin_menu_{style_name}.png" alt="{style_desc}選單">
                <div class="rocket-description">
                    {description}
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="highlight">
            <h2>🌊 海王星特色</h2>
            <p>海王星是太陽系中最遠的行星，以其深藍色和強烈的風暴聞名。在我們的設計中，海王星擁有：</p>
            <div class="features">
                <div class="feature-card">
                    <div class="emoji">💙</div>
                    <h4>深藍色調</h4>
                    <p>從深藍到淺藍的漸層效果，如同真實的海王星</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">🌀</div>
                    <h4>大氣漩渦</h4>
                    <p>表面的漩渦紋理，展現海王星的風暴特色</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">💍</div>
                    <h4>精緻環帶</h4>
                    <p>4層不同顏色的環帶，比土星更加精緻美麗</p>
                </div>
                <div class="feature-card">
                    <div class="emoji">😊</div>
                    <h4>溫和表情</h4>
                    <p>深藍色眼珠配溫和微笑，親切可愛</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    with open("rich_menu_images/rocket_styles_preview.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("📄 已生成預覽文件: rich_menu_images/rocket_styles_preview.html")

def main():
    """主函數"""
    print("🌟 開始測試新的火箭造型和海王星設計...")
    
    # 測試不同火箭造型
    test_rocket_styles()
    
    # 生成預覽 HTML
    generate_preview_html()
    
    print("\n✅ 測試完成！")
    print("📁 請查看 rich_menu_images/ 目錄中的圖片文件")
    print("🌐 請打開 rich_menu_images/rocket_styles_preview.html 查看預覽")

if __name__ == "__main__":
    main() 