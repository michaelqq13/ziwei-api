#!/usr/bin/env python3
"""
創建更明顯的邊界樣式測試
讓用戶能清楚看到不同樣式的差異
"""

import os
from app.utils.tabbed_rich_menu_generator import generate_tabbed_rich_menu, get_available_border_styles
import webbrowser

def create_enhanced_border_test():
    """創建增強版的邊界樣式測試"""
    print("🎨 創建增強版邊界樣式測試")
    print("=" * 50)
    
    # 測試配置
    test_configs = [
        {"user": "admin", "tab": "basic", "name": "管理員基本功能"},
        {"user": "admin", "tab": "fortune", "name": "管理員運勢功能"},
        {"user": "admin", "tab": "admin", "name": "管理員進階功能"},
        {"user": "premium", "tab": "basic", "name": "付費會員基本功能"},
        {"user": "premium", "tab": "fortune", "name": "付費會員運勢功能"},
        {"user": "free", "tab": "basic", "name": "免費會員基本功能"}
    ]
    
    border_styles = get_available_border_styles()
    
    for config in test_configs:
        print(f"\n🔧 測試配置: {config['name']}")
        print("-" * 30)
        
        generated_images = []
        
        # 生成所有邊界樣式
        for style in border_styles:
            try:
                image_path, button_areas = generate_tabbed_rich_menu(
                    config["tab"], config["user"], style
                )
                
                if os.path.exists(image_path):
                    file_size = os.path.getsize(image_path) / 1024
                    print(f"✅ {style}: {file_size:.1f} KB")
                    generated_images.append({
                        'style': style,
                        'path': image_path,
                        'size': file_size,
                        'buttons': len(button_areas)
                    })
                else:
                    print(f"❌ {style}: 生成失敗")
                    
            except Exception as e:
                print(f"❌ {style}: {e}")
        
        # 創建詳細比較預覽
        if generated_images:
            preview_file = create_detailed_comparison_html(
                generated_images, config["user"], config["tab"], config["name"]
            )
            print(f"📋 詳細比較預覽: {preview_file}")

def create_detailed_comparison_html(images, user_level, tab, config_name):
    """創建詳細的比較預覽HTML"""
    preview_name = f"detailed_comparison_{tab}_{user_level}.html"
    
    # 樣式描述
    style_descriptions = {
        'soft_glow': {
            'name': '柔和發光',
            'desc': '活躍分頁底部有微妙的白色發光效果，營造溫和的視覺層次',
            'best_for': '適合需要溫和視覺提示的場景'
        },
        'subtle_separator': {
            'name': '微妙分隔',
            'desc': '分頁間有漸變的垂直分隔線，提供清晰但不突兀的分隔',
            'best_for': '適合需要清晰分隔但保持簡潔的設計'
        },
        'gradient': {
            'name': '漸變邊界',
            'desc': '活躍分頁底部有漸變的邊界效果，提供明顯的視覺焦點',
            'best_for': '適合需要明顯視覺焦點的場景'
        },
        'no_border': {
            'name': '無邊框',
            'desc': '完全依靠背景亮度差異來區分分頁，最簡潔的設計',
            'best_for': '適合追求極簡設計的場景'
        }
    }
    
    # 生成圖片展示HTML
    image_sections = ""
    for img in images:
        style = img['style']
        style_info = style_descriptions.get(style, {})
        
        image_sections += f"""
        <div class="style-comparison">
            <div class="style-header">
                <h3>🎨 {style_info.get('name', style.upper())} ({img['size']:.1f} KB)</h3>
                <div class="style-meta">
                    <span class="button-count">📱 {img['buttons']} 個按鈕</span>
                    <span class="style-tag">{style}</span>
                </div>
            </div>
            
            <div class="style-description">
                <p><strong>效果說明:</strong> {style_info.get('desc', '未知效果')}</p>
                <p><strong>適用場景:</strong> {style_info.get('best_for', '通用場景')}</p>
            </div>
            
            <div class="image-container">
                <img src="{os.path.basename(img['path'])}" alt="{style}" class="menu-image">
                <div class="image-overlay">
                    <div class="focus-area">
                        <div class="focus-label">👆 注意分頁標籤區域的差異</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>詳細邊界樣式比較 - {config_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #f0f0f0;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header h2 {{
            color: #7f8c8d;
            font-size: 1.3em;
            margin: 10px 0 0 0;
            font-weight: normal;
        }}
        
        .intro {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #3498db;
        }}
        
        .intro h3 {{
            color: #2980b9;
            margin-top: 0;
        }}
        
        .style-comparison {{
            margin-bottom: 50px;
            background: #fafafa;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }}
        
        .style-comparison:hover {{
            border-color: #3498db;
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.1);
        }}
        
        .style-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .style-header h3 {{
            color: #2c3e50;
            margin: 0;
            font-size: 1.5em;
        }}
        
        .style-meta {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .button-count {{
            background: #27ae60;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .style-tag {{
            background: #34495e;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-family: monospace;
        }}
        
        .style-description {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #9b59b6;
        }}
        
        .style-description p {{
            margin: 5px 0;
            line-height: 1.6;
        }}
        
        .image-container {{
            position: relative;
            text-align: center;
        }}
        
        .menu-image {{
            max-width: 100%;
            border: 3px solid #bdc3c7;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }}
        
        .menu-image:hover {{
            transform: scale(1.02);
        }}
        
        .image-overlay {{
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(231, 76, 60, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 0 0 15px 15px;
            font-weight: bold;
            font-size: 0.9em;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .focus-area {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .focus-label {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        
        .comparison-tip {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .comparison-tip h4 {{
            color: #856404;
            margin-top: 0;
        }}
        
        .comparison-tip p {{
            color: #856404;
            margin-bottom: 0;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 詳細邊界樣式比較</h1>
            <h2>{config_name}</h2>
        </div>
        
        <div class="intro">
            <h3>📋 比較說明</h3>
            <p>以下展示了四種不同的邊界樣式效果。<strong>請特別注意每個圖片頂部的分頁標籤區域</strong>，那裡是主要的視覺差異所在。</p>
            <p>每種樣式都有其獨特的視覺特點和適用場景，您可以根據實際需求選擇最適合的樣式。</p>
        </div>
        
        <div class="comparison-tip">
            <h4>💡 觀察重點</h4>
            <p>請仔細觀察每張圖片<strong>頂部分頁標籤區域</strong>的差異：</p>
            <p>• 活躍分頁（較亮的那個）的底部邊界處理</p>
            <p>• 非活躍分頁之間的分隔效果</p>
            <p>• 整體的視覺層次和和諧感</p>
        </div>
        
        {image_sections}
        
        <div class="comparison-tip">
            <h4>🎯 選擇建議</h4>
            <p>如果您覺得差異不夠明顯，建議選擇 <strong>no_border</strong> 或 <strong>soft_glow</strong> 樣式。</p>
            <p>這兩種樣式都提供了良好的視覺效果，同時保持了界面的簡潔性。</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(preview_name, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return preview_name

if __name__ == "__main__":
    create_enhanced_border_test()
    
    # 自動生成一個推薦的測試配置
    print("\n🌟 生成推薦配置預覽...")
    try:
        # 生成管理員基本功能的詳細比較
        image_path, button_areas = generate_tabbed_rich_menu("basic", "admin", "soft_glow")
        
        if os.path.exists(image_path):
            # 創建詳細比較
            images = []
            for style in get_available_border_styles():
                img_path, _ = generate_tabbed_rich_menu("basic", "admin", style)
                if os.path.exists(img_path):
                    images.append({
                        'style': style,
                        'path': img_path,
                        'size': os.path.getsize(img_path) / 1024,
                        'buttons': len(button_areas)
                    })
            
            if images:
                preview_file = create_detailed_comparison_html(
                    images, "admin", "basic", "管理員基本功能 - 推薦預覽"
                )
                print(f"📋 推薦預覽已創建: {preview_file}")
                
                # 在瀏覽器中打開
                webbrowser.open(f"file://{os.path.abspath(preview_file)}")
                print("🌐 已在瀏覽器中打開推薦預覽")
                
    except Exception as e:
        print(f"❌ 生成推薦預覽失敗: {e}") 