#!/usr/bin/env python3
"""
快速打開三個推薦邊界樣式的預覽
"""

import os
import webbrowser
import time

def open_recommended_previews():
    """打開三個推薦方案的預覽"""
    print("🎨 打開三個推薦邊界樣式的預覽")
    print("=" * 40)
    
    # 三個推薦方案
    recommended_styles = [
        ("no_border", "完全無邊框"),
        ("soft_glow", "柔和發光效果"),
        ("subtle_separator", "微妙分隔線")
    ]
    
    for style, description in recommended_styles:
        preview_file = f"preview_tabbed_basic_admin_{style}.html"
        
        if os.path.exists(preview_file):
            print(f"🌟 {description} ({style})")
            print(f"   📁 文件: {preview_file}")
            
            # 在瀏覽器中打開
            webbrowser.open(f"file://{os.path.abspath(preview_file)}")
            
            # 稍微延遲，避免同時打開太多標籤
            time.sleep(1)
            
            print(f"   ✅ 已在瀏覽器中打開")
        else:
            print(f"❌ {description} ({style})")
            print(f"   📁 文件不存在: {preview_file}")
            print(f"   💡 請先運行: python3 manage_tabbed_rich_menu.py --preview admin:basic:{style}")
        
        print()
    
    # 同時打開比較預覽
    comparison_file = "comparison_tabbed_basic_admin.html"
    if os.path.exists(comparison_file):
        print("🔍 完整比較預覽")
        print(f"   📁 文件: {comparison_file}")
        webbrowser.open(f"file://{os.path.abspath(comparison_file)}")
        print(f"   ✅ 已在瀏覽器中打開")
    else:
        print("❌ 比較預覽文件不存在")
        print("   💡 請先運行: python3 manage_tabbed_rich_menu.py --compare admin:basic")
    
    print("\n🎉 所有預覽已打開！")
    print("💡 提示：現在您可以在瀏覽器中比較三個推薦方案的視覺效果")

if __name__ == "__main__":
    open_recommended_previews() 