#!/usr/bin/env python3
"""
擴展太空元素預覽生成器
提供更多太空和星球元素選項替代地球和月球
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math
import random

class ExtendedSpaceElementsGenerator:
    def __init__(self):
        pass
    
    def _draw_saturn(self, draw, center_x, center_y, radius, base_color):
        """繪製土星"""
        # 土星主體
        saturn_color = (255, 215, 100)  # 金黃色
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=saturn_color)
        
        # 土星環
        ring_color = (200, 180, 80)
        ring_width = 3
        # 外環
        draw.ellipse([
            (center_x - radius * 1.5, center_y - radius * 0.3),
            (center_x + radius * 1.5, center_y + radius * 0.3)
        ], outline=ring_color, width=ring_width)
        # 內環
        draw.ellipse([
            (center_x - radius * 1.3, center_y - radius * 0.25),
            (center_x + radius * 1.3, center_y + radius * 0.25)
        ], outline=ring_color, width=ring_width-1)
        
        # 土星表面條紋
        for i in range(3):
            y_offset = (i - 1) * radius * 0.4
            draw.ellipse([
                (center_x - radius * 0.8, center_y + y_offset - 5),
                (center_x + radius * 0.8, center_y + y_offset + 5)
            ], fill=(240, 200, 80))
    
    def _draw_jupiter(self, draw, center_x, center_y, radius, base_color):
        """繪製木星"""
        # 木星主體
        jupiter_color = (255, 140, 60)  # 橙紅色
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=jupiter_color)
        
        # 木星條紋
        stripe_colors = [(220, 120, 40), (255, 160, 80), (200, 100, 30)]
        for i, color in enumerate(stripe_colors):
            y_offset = (i - 1) * radius * 0.5
            draw.ellipse([
                (center_x - radius * 0.9, center_y + y_offset - 8),
                (center_x + radius * 0.9, center_y + y_offset + 8)
            ], fill=color)
        
        # 大紅斑
        draw.ellipse([
            (center_x - 15, center_y - 10),
            (center_x + 15, center_y + 10)
        ], fill=(180, 60, 40))
    
    def _draw_mars(self, draw, center_x, center_y, radius, base_color):
        """繪製火星"""
        # 火星主體
        mars_color = (200, 80, 60)  # 紅色
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=mars_color)
        
        # 火星表面特徵
        # 極地冰帽
        draw.ellipse([
            (center_x - radius * 0.3, center_y - radius + 5),
            (center_x + radius * 0.3, center_y - radius + 25)
        ], fill=(255, 255, 255))
        
        # 火山和隕石坑
        craters = [(center_x - 20, center_y + 10), (center_x + 15, center_y - 15)]
        for crater_x, crater_y in craters:
            draw.ellipse([
                (crater_x - 8, crater_y - 8),
                (crater_x + 8, crater_y + 8)
            ], fill=(150, 60, 40))
    
    def _draw_venus(self, draw, center_x, center_y, radius, base_color):
        """繪製金星"""
        # 金星主體
        venus_color = (255, 200, 120)  # 金黃色
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=venus_color)
        
        # 金星雲層
        cloud_color = (240, 180, 100)
        for i in range(4):
            angle = i * 90
            cloud_x = center_x + math.cos(math.radians(angle)) * radius * 0.6
            cloud_y = center_y + math.sin(math.radians(angle)) * radius * 0.6
            draw.ellipse([
                (cloud_x - 12, cloud_y - 8),
                (cloud_x + 12, cloud_y + 8)
            ], fill=cloud_color)
    
    def _draw_neptune(self, draw, center_x, center_y, radius, base_color):
        """繪製海王星"""
        # 海王星主體
        neptune_color = (70, 130, 200)  # 藍色
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=neptune_color)
        
        # 海王星風暴
        storm_color = (50, 100, 180)
        draw.ellipse([
            (center_x - 20, center_y - 15),
            (center_x + 20, center_y + 15)
        ], fill=storm_color)
        
        # 海王星環（微弱）
        ring_color = (100, 150, 220)
        draw.ellipse([
            (center_x - radius * 1.2, center_y - radius * 0.2),
            (center_x + radius * 1.2, center_y + radius * 0.2)
        ], outline=ring_color, width=1)
    
    def _draw_asteroid(self, draw, center_x, center_y, radius, base_color):
        """繪製小行星"""
        # 不規則形狀的小行星
        asteroid_color = (120, 120, 120)
        points = []
        num_points = 8
        for i in range(num_points):
            angle = i * (360 / num_points)
            # 隨機變化半徑創造不規則形狀
            r = radius * (0.7 + random.random() * 0.6)
            x = center_x + math.cos(math.radians(angle)) * r
            y = center_y + math.sin(math.radians(angle)) * r
            points.append((x, y))
        
        draw.polygon(points, fill=asteroid_color)
        
        # 隕石坑
        for _ in range(3):
            crater_x = center_x + random.randint(-radius//2, radius//2)
            crater_y = center_y + random.randint(-radius//2, radius//2)
            draw.ellipse([
                (crater_x - 5, crater_y - 5),
                (crater_x + 5, crater_y + 5)
            ], fill=(80, 80, 80))
    
    def _draw_comet(self, draw, center_x, center_y, radius, base_color):
        """繪製彗星"""
        # 彗星核心
        comet_color = (200, 200, 200)
        draw.ellipse([
            (center_x - radius//2, center_y - radius//2),
            (center_x + radius//2, center_y + radius//2)
        ], fill=comet_color)
        
        # 彗星尾巴
        tail_color = (150, 200, 255)
        tail_points = [
            (center_x + radius//2, center_y),
            (center_x + radius * 2, center_y - radius//2),
            (center_x + radius * 2.5, center_y),
            (center_x + radius * 2, center_y + radius//2)
        ]
        draw.polygon(tail_points, fill=tail_color)
        
        # 內層尾巴
        inner_tail_color = (200, 220, 255)
        inner_tail_points = [
            (center_x + radius//2, center_y),
            (center_x + radius * 1.5, center_y - radius//4),
            (center_x + radius * 1.8, center_y),
            (center_x + radius * 1.5, center_y + radius//4)
        ]
        draw.polygon(inner_tail_points, fill=inner_tail_color)
    
    def _draw_star(self, draw, center_x, center_y, radius, base_color):
        """繪製星星"""
        # 五角星
        star_color = (255, 255, 100)
        points = []
        for i in range(10):
            angle = i * 36 - 90  # 從頂部開始
            if i % 2 == 0:
                # 外點
                r = radius
            else:
                # 內點
                r = radius * 0.4
            x = center_x + math.cos(math.radians(angle)) * r
            y = center_y + math.sin(math.radians(angle)) * r
            points.append((x, y))
        
        draw.polygon(points, fill=star_color)
        
        # 星星光芒
        glow_color = (255, 255, 150)
        for i in range(4):
            angle = i * 90
            start_x = center_x + math.cos(math.radians(angle)) * radius * 0.8
            start_y = center_y + math.sin(math.radians(angle)) * radius * 0.8
            end_x = center_x + math.cos(math.radians(angle)) * radius * 1.5
            end_y = center_y + math.sin(math.radians(angle)) * radius * 1.5
            draw.line([(start_x, start_y), (end_x, end_y)], fill=glow_color, width=2)
    
    def _draw_black_hole(self, draw, center_x, center_y, radius, base_color):
        """繪製黑洞"""
        # 黑洞事件視界
        black_color = (20, 20, 20)
        draw.ellipse([
            (center_x - radius * 0.6, center_y - radius * 0.6),
            (center_x + radius * 0.6, center_y + radius * 0.6)
        ], fill=black_color)
        
        # 吸積盤
        disk_colors = [(255, 150, 50), (255, 100, 0), (200, 50, 0)]
        for i, color in enumerate(disk_colors):
            disk_radius = radius * (1.2 + i * 0.2)
            draw.ellipse([
                (center_x - disk_radius, center_y - disk_radius * 0.3),
                (center_x + disk_radius, center_y + disk_radius * 0.3)
            ], outline=color, width=3)
    
    def _draw_galaxy(self, draw, center_x, center_y, radius, base_color):
        """繪製星系"""
        # 星系核心
        core_color = (255, 200, 100)
        draw.ellipse([
            (center_x - radius * 0.3, center_y - radius * 0.3),
            (center_x + radius * 0.3, center_y + radius * 0.3)
        ], fill=core_color)
        
        # 旋臂
        arm_color = (150, 150, 255)
        for i in range(3):
            angle_offset = i * 120
            for j in range(20):
                angle = j * 18 + angle_offset
                r = radius * 0.4 + j * radius * 0.03
                x = center_x + math.cos(math.radians(angle)) * r
                y = center_y + math.sin(math.radians(angle)) * r
                draw.ellipse([
                    (x - 2, y - 2),
                    (x + 2, y + 2)
                ], fill=arm_color)

def create_extended_space_preview():
    """創建擴展太空元素預覽"""
    # 新的太空元素配置
    space_elements = {
        "planets": [
            {"name": "saturn", "title": "Saturn", "description": "Beautiful ringed planet"},
            {"name": "jupiter", "title": "Jupiter", "description": "Gas giant with great red spot"},
            {"name": "mars", "title": "Mars", "description": "Red planet with polar caps"},
            {"name": "venus", "title": "Venus", "description": "Golden cloudy planet"},
            {"name": "neptune", "title": "Neptune", "description": "Blue windy planet"}
        ],
        "space_objects": [
            {"name": "asteroid", "title": "Asteroid", "description": "Rocky space debris"},
            {"name": "comet", "title": "Comet", "description": "Icy body with tail"},
            {"name": "star", "title": "Star", "description": "Bright shining star"},
            {"name": "black_hole", "title": "Black Hole", "description": "Mysterious dark object"},
            {"name": "galaxy", "title": "Galaxy", "description": "Spiral star system"}
        ]
    }
    
    # 創建預覽圖片
    preview_width = 1600
    preview_height = 800
    preview_img = Image.new('RGB', (preview_width, preview_height), (10, 15, 30))
    draw = ImageDraw.Draw(preview_img)
    
    # 標題
    title_font_size = 36
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", title_font_size)
        section_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        name_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        desc_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 11)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", title_font_size)
            section_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            desc_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        except:
            title_font = ImageFont.load_default()
            section_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
    
    # 主標題
    title_text = "Extended Space Elements - Replace Earth & Moon"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((preview_width - title_width) // 2, 20), title_text, fill=(255, 255, 255), font=title_font)
    
    # 創建生成器
    generator = ExtendedSpaceElementsGenerator()
    
    # 計算布局
    section_height = (preview_height - 100) // 2
    current_y = 80
    
    # 繪製每個類別
    for category, elements in space_elements.items():
        # 類別標題
        category_titles = {
            "planets": "🪐 Alternative Planets",
            "space_objects": "⭐ Space Objects"
        }
        
        category_title = category_titles.get(category, category.title())
        draw.text((50, current_y), category_title, fill=(255, 215, 0), font=section_font)
        
        # 計算每個元素的位置
        elements_per_row = len(elements)
        cell_width = (preview_width - 100) // elements_per_row
        cell_height = section_height - 50
        
        # 繪製每個元素
        for i, element in enumerate(elements):
            x = 50 + i * cell_width + cell_width // 2
            y = current_y + 50 + cell_height // 2
            
            # 繪製元素
            radius = 50
            base_color = (200, 200, 200)
            
            # 設置隨機種子以確保一致性
            random.seed(hash(element["name"]))
            
            try:
                method_name = f"_draw_{element['name']}"
                if hasattr(generator, method_name):
                    method = getattr(generator, method_name)
                    method(draw, x, y, radius, base_color)
                else:
                    # 默認圓形
                    draw.ellipse([
                        (x - radius, y - radius),
                        (x + radius, y + radius)
                    ], fill=base_color)
            except Exception as e:
                # 如果繪製失敗，畫一個簡單的圓圈
                draw.ellipse([
                    (x - radius, y - radius),
                    (x + radius, y + radius)
                ], fill=(100, 100, 100))
                print(f"Warning: Could not draw {element['name']}: {e}")
            
            # 添加編號
            prefix = "P" if category == "planets" else "S"
            number_text = f"{prefix}{i + 1}"
            number_bbox = draw.textbbox((0, 0), number_text, font=name_font)
            number_width = number_bbox[2] - number_bbox[0]
            draw.text((x - number_width // 2, y - radius - 25), number_text, fill=(255, 215, 0), font=name_font)
            
            # 添加元素名稱
            name_bbox = draw.textbbox((0, 0), element["title"], font=name_font)
            name_width = name_bbox[2] - name_bbox[0]
            draw.text((x - name_width // 2, y + radius + 15), element["title"], fill=(255, 255, 255), font=name_font)
            
            # 添加描述
            desc_bbox = draw.textbbox((0, 0), element["description"], font=desc_font)
            desc_width = desc_bbox[2] - desc_bbox[0]
            draw.text((x - desc_width // 2, y + radius + 35), element["description"], fill=(180, 180, 180), font=desc_font)
        
        current_y += section_height
    
    # 保存預覽圖片
    preview_path = "extended_space_preview.png"
    preview_img.save(preview_path)
    
    return preview_path, space_elements

def create_html_extended_preview():
    """創建擴展太空元素HTML預覽頁面"""
    preview_path, space_elements = create_extended_space_preview()
    
    # 中文對應
    chinese_categories = {
        "planets": "替代行星",
        "space_objects": "太空物件"
    }
    
    chinese_elements = {
        "planets": {
            "saturn": {"title": "土星", "desc": "美麗的環狀行星"},
            "jupiter": {"title": "木星", "desc": "有大紅斑的氣態巨行星"},
            "mars": {"title": "火星", "desc": "有極地冰帽的紅色行星"},
            "venus": {"title": "金星", "desc": "金黃色雲層行星"},
            "neptune": {"title": "海王星", "desc": "藍色風暴行星"}
        },
        "space_objects": {
            "asteroid": {"title": "小行星", "desc": "岩石太空碎片"},
            "comet": {"title": "彗星", "desc": "有尾巴的冰體"},
            "star": {"title": "恆星", "desc": "明亮閃爍的星星"},
            "black_hole": {"title": "黑洞", "desc": "神秘的黑暗天體"},
            "galaxy": {"title": "星系", "desc": "螺旋星系"}
        }
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>擴展太空元素選擇</title>
        <style>
            body {{
                font-family: 'PingFang TC', 'Microsoft JhengHei', sans-serif;
                background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 100%);
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
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .style-card {{
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }}
            .style-card:hover {{
                transform: translateY(-5px);
            }}
            .style-number {{
                font-size: 1.8em;
                font-weight: bold;
                color: #FFD700;
                margin-bottom: 10px;
            }}
            .style-title {{
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 10px;
                color: #FFFFFF;
            }}
            .style-description {{
                font-size: 1em;
                line-height: 1.5;
                color: #CCCCCC;
            }}
            .current-selection {{
                background: rgba(255,215,0,0.2);
                border: 2px solid #FFD700;
                border-radius: 12px;
                padding: 20px;
                margin: 30px 0;
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌌 擴展太空元素選擇</h1>
            
            <div class="current-selection">
                <h3>✅ 您目前的選擇：</h3>
                <p><strong>太陽：</strong>S1 (經典太陽)</p>
                <p><strong>火箭：</strong>R1 (經典火箭)</p>
                <p><strong>需要替換：</strong>地球 + 月球 → 選擇下方2個新元素</p>
            </div>
            
            <img src="{preview_path}" alt="擴展太空元素預覽" class="preview-image">
    """
    
    # 為每個類別創建詳細說明
    for category, elements in space_elements.items():
        chinese_category = chinese_categories.get(category, category)
        
        html_content += f"""
            <div class="category-section">
                <h2 class="category-title">{chinese_category}</h2>
                <div class="styles-grid">
        """
        
        for i, element in enumerate(elements):
            prefix = "P" if category == "planets" else "S"
            chinese_info = chinese_elements.get(category, {}).get(element["name"], {
                "title": element["title"],
                "desc": element["description"]
            })
            
            html_content += f"""
                    <div class="style-card">
                        <div class="style-number">{prefix}{i + 1}</div>
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
                <h3>🎯 選擇指南</h3>
                
                <h4>📋 您需要選擇2個新元素來替換地球和月球：</h4>
                <ol>
                    <li><strong>從行星類別選擇1個</strong>：P1-P5 (土星、木星、火星、金星、海王星)</li>
                    <li><strong>從太空物件選擇1個</strong>：S1-S5 (小行星、彗星、恆星、黑洞、星系)</li>
                    <li><strong>或者兩個都從同一類別選擇</strong>：完全由您決定！</li>
                </ol>
                
                <h3>🎨 元素編號說明</h3>
                <ul>
                    <li><strong>P1-P5</strong>：行星類別 (Planets 1-5)</li>
                    <li><strong>S1-S5</strong>：太空物件 (Space Objects 1-5)</li>
                </ul>
                
                <h3>💡 搭配建議</h3>
                <ul>
                    <li><strong>經典組合</strong>：土星(P1) + 恆星(S3) - 傳統太空感</li>
                    <li><strong>神秘組合</strong>：海王星(P5) + 黑洞(S4) - 深邃神秘</li>
                    <li><strong>活潑組合</strong>：木星(P2) + 彗星(S2) - 動感活力</li>
                    <li><strong>科幻組合</strong>：火星(P3) + 星系(S5) - 未來感</li>
                </ul>
                
                <div class="code-example">
                    範例回覆：
                    「選擇 P1 和 S3」(土星 + 恆星)
                    
                    或：
                    「我要土星和黑洞」
                    
                    或：
                    「P1, S4」(土星 + 黑洞)
                </div>
                
                <h3>⚡ 最終配置</h3>
                <p>選擇完成後，您的LINE Bot選單將包含：</p>
                <ul>
                    <li>☀️ 太陽 (S1 - 經典太陽)</li>
                    <li>🚀 火箭 (R1 - 經典火箭)</li>
                    <li>🌟 您選擇的第一個新元素</li>
                    <li>🌟 您選擇的第二個新元素</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 保存HTML文件
    html_path = "extended_space_preview.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

if __name__ == "__main__":
    try:
        html_path = create_html_extended_preview()
        print(f"✅ 擴展太空元素預覽已生成：{html_path}")
        print("🌌 新增元素：")
        print("   🪐 行星類別：土星、木星、火星、金星、海王星")
        print("   ⭐ 太空物件：小行星、彗星、恆星、黑洞、星系")
        print("\n請選擇2個新元素來替換地球和月球！")
    except Exception as e:
        print(f"❌ 生成預覽時出錯：{e}")
        import traceback
        traceback.print_exc() 