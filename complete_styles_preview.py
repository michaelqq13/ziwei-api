#!/usr/bin/env python3
"""
完整樣式預覽生成器
生成太陽、地球、月亮、火箭的所有樣式預覽圖片供用戶選擇
"""

import os
from PIL import Image, ImageDraw, ImageFont
from app.utils.rich_menu_image_generator import RichMenuImageGenerator

def create_complete_styles_preview():
    """創建完整樣式預覽"""
    # 所有樣式配置
    all_styles = {
        "sun": [
            {"name": "classic", "title": "Classic Sun", "description": "Traditional sun with rays"},
            {"name": "cute", "title": "Cute Sun", "description": "Adorable sun with kawaii face"},
            {"name": "cartoon", "title": "Cartoon Sun", "description": "Playful cartoon style"},
            {"name": "modern", "title": "Modern Sun", "description": "Clean modern design"},
            {"name": "kawaii", "title": "Kawaii Sun", "description": "Japanese cute style"}
        ],
        "earth": [
            {"name": "classic", "title": "Classic Earth", "description": "Traditional earth with continents"},
            {"name": "detailed", "title": "Detailed Earth", "description": "Earth with detailed features"},
            {"name": "with_arms", "title": "Earth with Arms", "description": "Earth with cute arms"},
            {"name": "eyes_only", "title": "Earth Eyes Only", "description": "Earth with just eyes"},
            {"name": "kawaii", "title": "Kawaii Earth", "description": "Japanese cute earth style"}
        ],
        "moon": [
            {"name": "classic", "title": "Classic Moon", "description": "Traditional moon with craters"},
            {"name": "sleepy", "title": "Sleepy Moon", "description": "Cute sleeping moon"},
            {"name": "crescent", "title": "Crescent Moon", "description": "Crescent shape moon"},
            {"name": "kawaii", "title": "Kawaii Moon", "description": "Japanese cute moon"},
            {"name": "mystical", "title": "Mystical Moon", "description": "Mysterious dark moon"}
        ],
        "rocket": [
            {"name": "classic", "title": "Classic Rocket", "description": "Traditional rocket design"},
            {"name": "cartoon", "title": "Cartoon Rocket", "description": "Playful cartoon rocket"},
            {"name": "retro", "title": "Retro Rocket", "description": "Vintage retro style"},
            {"name": "modern", "title": "Modern Rocket", "description": "Sleek modern rocket"},
            {"name": "space_shuttle", "title": "Space Shuttle", "description": "Space shuttle design"},
            {"name": "mini", "title": "Mini Rocket", "description": "Small cute rocket"}
        ]
    }
    
    # 創建預覽圖片
    preview_width = 1600
    preview_height = 1200
    preview_img = Image.new('RGB', (preview_width, preview_height), (20, 25, 40))
    draw = ImageDraw.Draw(preview_img)
    
    # 標題
    title_font_size = 40
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", title_font_size)
        section_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
        name_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        desc_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", title_font_size)
            section_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            desc_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except:
            title_font = ImageFont.load_default()
            section_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
    
    # 主標題
    title_text = "Complete Styles Preview - Choose Your Favorites"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((preview_width - title_width) // 2, 20), title_text, fill=(255, 255, 255), font=title_font)
    
    # 創建圖片生成器
    generator = RichMenuImageGenerator()
    
    # 計算布局
    section_height = (preview_height - 100) // 4
    current_y = 80
    
    # 繪製每個類別的樣式
    for category, styles in all_styles.items():
        # 類別標題
        category_titles = {
            "sun": "☀️ Sun Styles",
            "earth": "🌍 Earth Styles", 
            "moon": "🌙 Moon Styles",
            "rocket": "🚀 Rocket Styles"
        }
        
        category_title = category_titles.get(category, category.title())
        category_bbox = draw.textbbox((0, 0), category_title, font=section_font)
        category_width = category_bbox[2] - category_bbox[0]
        draw.text((50, current_y), category_title, fill=(255, 215, 0), font=section_font)
        
        # 計算每個樣式的位置
        styles_per_row = len(styles)
        cell_width = (preview_width - 100) // styles_per_row
        cell_height = section_height - 50
        
        # 繪製每個樣式
        for i, style in enumerate(styles):
            x = 50 + i * cell_width + cell_width // 2
            y = current_y + 50 + cell_height // 2
            
            # 繪製樣式
            radius = 45
            base_color = (200, 200, 200)
            
            try:
                if category == "sun":
                    if style["name"] == "classic":
                        generator._draw_classic_sun(draw, x, y, radius, base_color)
                    elif style["name"] == "cute":
                        generator._draw_cute_sun(draw, x, y, radius, base_color)
                    elif style["name"] == "cartoon":
                        generator._draw_cartoon_sun(draw, x, y, radius, base_color)
                    elif style["name"] == "modern":
                        generator._draw_modern_sun(draw, x, y, radius, base_color)
                    elif style["name"] == "kawaii":
                        generator._draw_kawaii_sun(draw, x, y, radius, base_color)
                
                elif category == "earth":
                    if style["name"] == "classic":
                        generator._draw_classic_earth(draw, x, y, radius, base_color)
                    elif style["name"] == "detailed":
                        generator._draw_detailed_earth(draw, x, y, radius, base_color)
                    elif style["name"] == "with_arms":
                        generator._draw_earth_with_arms(draw, x, y, radius, base_color)
                    elif style["name"] == "eyes_only":
                        generator._draw_earth_eyes_only(draw, x, y, radius, base_color)
                    elif style["name"] == "kawaii":
                        generator._draw_kawaii_earth(draw, x, y, radius, base_color)
                
                elif category == "moon":
                    if style["name"] == "classic":
                        generator._draw_classic_moon(draw, x, y, radius, base_color)
                    elif style["name"] == "sleepy":
                        generator._draw_sleepy_moon(draw, x, y, radius, base_color)
                    elif style["name"] == "crescent":
                        generator._draw_crescent_moon(draw, x, y, radius, base_color)
                    elif style["name"] == "kawaii":
                        generator._draw_kawaii_moon(draw, x, y, radius, base_color)
                    elif style["name"] == "mystical":
                        generator._draw_mystical_moon(draw, x, y, radius, base_color)
                
                elif category == "rocket":
                    if style["name"] == "classic":
                        generator._draw_classic_rocket(draw, x, y, radius, base_color)
                    elif style["name"] == "cartoon":
                        generator._draw_cartoon_rocket(draw, x, y, radius, base_color)
                    elif style["name"] == "retro":
                        generator._draw_retro_rocket(draw, x, y, radius, base_color)
                    elif style["name"] == "modern":
                        generator._draw_modern_rocket(draw, x, y, radius, base_color)
                    elif style["name"] == "space_shuttle":
                        generator._draw_space_shuttle_rocket(draw, x, y, radius, base_color)
                    elif style["name"] == "mini":
                        generator._draw_mini_rocket(draw, x, y, radius, base_color)
            except Exception as e:
                # 如果繪製失敗，畫一個簡單的圓圈
                draw.ellipse([
                    (x - radius, y - radius),
                    (x + radius, y + radius)
                ], fill=(100, 100, 100))
                print(f"Warning: Could not draw {category} {style['name']}: {e}")
            
            # 添加編號
            number_text = f"{i + 1}"
            number_bbox = draw.textbbox((0, 0), number_text, font=name_font)
            number_width = number_bbox[2] - number_bbox[0]
            draw.text((x - number_width // 2, y - radius - 25), number_text, fill=(255, 215, 0), font=name_font)
            
            # 添加樣式名稱
            name_bbox = draw.textbbox((0, 0), style["title"], font=name_font)
            name_width = name_bbox[2] - name_bbox[0]
            draw.text((x - name_width // 2, y + radius + 10), style["title"], fill=(255, 255, 255), font=name_font)
            
            # 添加描述（縮短版本）
            desc_words = style["description"].split()[:3]  # 只取前3個詞
            short_desc = " ".join(desc_words)
            desc_bbox = draw.textbbox((0, 0), short_desc, font=desc_font)
            desc_width = desc_bbox[2] - desc_bbox[0]
            draw.text((x - desc_width // 2, y + radius + 30), short_desc, fill=(180, 180, 180), font=desc_font)
        
        current_y += section_height
    
    # 保存預覽圖片
    preview_path = "complete_styles_preview.png"
    preview_img.save(preview_path)
    
    return preview_path, all_styles

def create_html_complete_preview():
    """創建完整HTML預覽頁面"""
    preview_path, all_styles = create_complete_styles_preview()
    
    # 中文對應
    chinese_categories = {
        "sun": "太陽樣式",
        "earth": "地球樣式",
        "moon": "月球樣式", 
        "rocket": "火箭樣式"
    }
    
    chinese_styles = {
        "sun": {
            "classic": {"title": "經典太陽", "desc": "傳統太陽光芒四射"},
            "cute": {"title": "可愛太陽", "desc": "萌萌的太陽表情"},
            "cartoon": {"title": "卡通太陽", "desc": "活潑卡通風格"},
            "modern": {"title": "現代太陽", "desc": "簡潔現代設計"},
            "kawaii": {"title": "日系太陽", "desc": "日式可愛風格"}
        },
        "earth": {
            "classic": {"title": "經典地球", "desc": "傳統地球大陸板塊"},
            "detailed": {"title": "詳細地球", "desc": "豐富細節地球"},
            "with_arms": {"title": "手臂地球", "desc": "有可愛手臂的地球"},
            "eyes_only": {"title": "眼睛地球", "desc": "只有眼睛的地球"},
            "kawaii": {"title": "日系地球", "desc": "日式可愛地球"}
        },
        "moon": {
            "classic": {"title": "經典月球", "desc": "傳統月球隕石坑"},
            "sleepy": {"title": "睡覺月球", "desc": "閉眼睡覺月球"},
            "crescent": {"title": "月牙樣式", "desc": "彎月造型"},
            "kawaii": {"title": "可愛月球", "desc": "日系可愛月球"},
            "mystical": {"title": "神秘月球", "desc": "神秘深色月球"}
        },
        "rocket": {
            "classic": {"title": "經典火箭", "desc": "傳統火箭設計"},
            "cartoon": {"title": "卡通火箭", "desc": "活潑卡通火箭"},
            "retro": {"title": "復古火箭", "desc": "復古風格火箭"},
            "modern": {"title": "現代火箭", "desc": "流線現代火箭"},
            "space_shuttle": {"title": "太空梭", "desc": "太空梭造型"},
            "mini": {"title": "迷你火箭", "desc": "小巧可愛火箭"}
        }
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>完整樣式選擇預覽</title>
        <style>
            body {{
                font-family: 'PingFang TC', 'Microsoft JhengHei', sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 1600px;
                margin: 0 auto;
                text-align: center;
            }}
            h1 {{
                font-size: 2.5em;
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }}
            .preview-image {{
                max-width: 100%;
                height: auto;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
            }}
            .category-section {{
                margin-bottom: 40px;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
            }}
            .category-title {{
                font-size: 1.8em;
                color: #FFD700;
                margin-bottom: 20px;
                text-align: left;
            }}
            .styles-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            .style-card {{
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }}
            .style-card:hover {{
                transform: translateY(-3px);
            }}
            .style-number {{
                font-size: 1.5em;
                font-weight: bold;
                color: #FFD700;
                margin-bottom: 8px;
            }}
            .style-title {{
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 8px;
                color: #FFFFFF;
            }}
            .style-description {{
                font-size: 0.9em;
                line-height: 1.4;
                color: #CCCCCC;
            }}
            .instructions {{
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                margin-top: 30px;
                text-align: left;
                backdrop-filter: blur(10px);
            }}
            .instructions h3 {{
                color: #FFD700;
                margin-bottom: 15px;
            }}
            .instructions ol, .instructions ul {{
                line-height: 1.8;
            }}
            .instructions li {{
                margin-bottom: 8px;
            }}
            .code-example {{
                background: rgba(0,0,0,0.3);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                color: #00FF00;
            }}
            .selection-guide {{
                background: rgba(255,215,0,0.1);
                border: 2px solid #FFD700;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 完整樣式選擇預覽</h1>
            
            <img src="{preview_path}" alt="完整樣式預覽" class="preview-image">
    """
    
    # 為每個類別創建詳細說明
    for category, styles in all_styles.items():
        chinese_category = chinese_categories.get(category, category)
        
        html_content += f"""
            <div class="category-section">
                <h2 class="category-title">{chinese_category}</h2>
                <div class="styles-grid">
        """
        
        for i, style in enumerate(styles):
            chinese_info = chinese_styles.get(category, {}).get(style["name"], {
                "title": style["title"],
                "desc": style["description"]
            })
            
            html_content += f"""
                    <div class="style-card">
                        <div class="style-number">{category[0].upper()}{i + 1}</div>
                        <div class="style-title">{chinese_info['title']}</div>
                        <div class="style-description">{chinese_info['desc']}</div>
                    </div>
            """
        
        html_content += """
                </div>
            </div>
        """
    
    html_content += """
            <div class="instructions">
                <h3>📋 選擇指南</h3>
                
                <div class="selection-guide">
                    <h4>🎯 如何選擇樣式</h4>
                    <ol>
                        <li><strong>查看預覽圖片</strong>：上方圖片展示了所有樣式的視覺效果</li>
                        <li><strong>按類別選擇</strong>：每個類別（太陽、地球、月球、火箭）選擇您喜歡的樣式</li>
                        <li><strong>記住編號</strong>：每個樣式都有編號（如 S1、E2、M3、R4）</li>
                        <li><strong>告訴我選擇</strong>：列出您要保留的樣式編號</li>
                    </ol>
                </div>
                
                <h3>🎨 樣式編號說明</h3>
                <ul>
                    <li><strong>S1-S5</strong>：太陽樣式（Sun 1-5）</li>
                    <li><strong>E1-E5</strong>：地球樣式（Earth 1-5）</li>
                    <li><strong>M1-M5</strong>：月球樣式（Moon 1-5）</li>
                    <li><strong>R1-R6</strong>：火箭樣式（Rocket 1-6）</li>
                </ul>
                
                <h3>💡 建議選擇</h3>
                <ul>
                    <li><strong>占卜應用</strong>：建議保留神秘、優雅的樣式</li>
                    <li><strong>年輕用戶</strong>：建議保留可愛、卡通的樣式</li>
                    <li><strong>簡潔設計</strong>：建議保留經典、現代的樣式</li>
                    <li><strong>多樣化</strong>：每個類別保留2-3個不同風格的樣式</li>
                </ul>
                
                <div class="code-example">
                    範例回覆：
                    「太陽保留 S1、S4，地球保留 E1、E5，月球保留 M1、M4，火箭保留 R2、R5」
                    
                    或簡化版：
                    「S1,S4 E1,E5 M1,M4 R2,R5」
                </div>
                
                <h3>⚡ 自動清理</h3>
                <p>選擇完成後，我會自動：</p>
                <ul>
                    <li>移除您不需要的樣式函數</li>
                    <li>更新樣式選擇邏輯</li>
                    <li>優化代碼結構</li>
                    <li>生成最終預覽確認</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 保存HTML文件
    html_path = "complete_styles_preview.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

if __name__ == "__main__":
    try:
        html_path = create_html_complete_preview()
        print(f"✅ 完整樣式預覽已生成：{html_path}")
        print("🎨 預覽包含：")
        print("   ☀️  太陽樣式：5種")
        print("   🌍 地球樣式：5種") 
        print("   🌙 月球樣式：5種")
        print("   🚀 火箭樣式：6種")
        print("\n請打開HTML文件查看預覽，然後告訴我您要保留哪些樣式！")
    except Exception as e:
        print(f"❌ 生成預覽時出錯：{e}")
        import traceback
        traceback.print_exc() 