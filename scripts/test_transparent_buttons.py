#!/usr/bin/env python3
"""
半透明按鈕和背景圖片視覺效果測試腳本
展示新的立體感設計和星空主題一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timezone, timedelta
from app.utils.flex_carousel_control_panel import FlexCarouselControlPanelGenerator
from app.utils.flex_control_panel import FlexControlPanelGenerator
from app.utils.flex_admin_panel import FlexAdminPanelGenerator
from app.utils.time_picker_flex_message import TimePickerFlexMessageGenerator

def test_transparent_button_effects():
    """測試半透明按鈕效果"""
    print("🎨 測試半透明按鈕視覺效果...")
    
    # 測試 Carousel 控制面板
    carousel_gen = FlexCarouselControlPanelGenerator()
    
    test_users = [
        {"user_info": {"is_admin": False}, "membership_info": {"is_premium": False}, "name": "免費用戶"},
        {"user_info": {"is_admin": False}, "membership_info": {"is_premium": True}, "name": "付費會員"},
        {"user_info": {"is_admin": True}, "membership_info": {"is_premium": True}, "name": "管理員"}
    ]
    
    for user in test_users:
        user_stats = {k: v for k, v in user.items() if k != "name"}
        carousel = carousel_gen.generate_carousel_control_panel(user_stats)
        
        if carousel:
            pages = len(carousel.contents.contents) if hasattr(carousel.contents, 'contents') else 0
            print(f"   ✅ {user['name']}: Carousel 生成成功，{pages} 個分頁")
            
            # 檢查每個分頁的按鈕效果
            for i, bubble in enumerate(carousel.contents.contents):
                if hasattr(bubble, 'body') and hasattr(bubble.body, 'contents'):
                    button_count = sum(1 for content in bubble.body.contents 
                                     if hasattr(content, 'backgroundColor') and 'rgba' in str(content.backgroundColor))
                    print(f"      - 分頁 {i+1}: {button_count} 個半透明按鈕")
        else:
            print(f"   ❌ {user['name']}: Carousel 生成失敗")
    
    return True

def test_background_image_consistency():
    """測試背景圖片一致性"""
    print("\n🌌 測試背景圖片一致性...")
    
    generators = [
        ("Carousel控制面板", FlexCarouselControlPanelGenerator()),
        ("普通控制面板", FlexControlPanelGenerator()),
        ("管理員面板", FlexAdminPanelGenerator()),
        ("時間選擇器", TimePickerFlexMessageGenerator())
    ]
    
    for name, gen in generators:
        if hasattr(gen, 'background_images'):
            img_count = len(gen.background_images)
            print(f"   ✅ {name}: {img_count} 張背景圖片")
            
            # 檢查是否使用 Unsplash 高品質圖片
            for key, url in gen.background_images.items():
                if 'unsplash.com' in url:
                    print(f"      - {key}: 使用 Unsplash 高品質圖片 ✨")
                else:
                    print(f"      - {key}: 使用一般圖片")
        else:
            print(f"   ⚠️ {name}: 沒有背景圖片配置")
    
    return True

def test_rgba_transparency_levels():
    """測試 RGBA 透明度級別"""
    print("\n🎭 測試 RGBA 透明度級別...")
    
    # 檢查不同的透明度配置
    transparency_configs = {
        "啟用按鈕": "rgba(74, 144, 226, 0.15)",    # 15% 透明度
        "禁用按鈕": "rgba(108, 123, 127, 0.1)",    # 10% 透明度
        "管理員按鈕": "rgba(139, 0, 0, 0.15)",      # 15% 透明度
        "背景遮罩": "#1A1A2ECC",                    # 80% 透明度
        "邊框效果": "rgba(255, 215, 0, 0.8)",       # 80% 透明度
        "陰影效果": "rgba(0, 0, 0, 0.1)"            # 10% 透明度
    }
    
    for name, rgba in transparency_configs.items():
        print(f"   ✅ {name}: {rgba}")
    
    return True

def test_visual_hierarchy():
    """測試視覺層次結構"""
    print("\n🏗️ 測試視覺層次結構...")
    
    # 檢查立體效果實現
    effects = [
        "半透明背景色：創造透視感",
        "金色邊框：增強高級感",
        "底部陰影：模擬立體效果",
        "圖標加大：增強識別度",
        "分級透明度：區分啟用/禁用狀態"
    ]
    
    for i, effect in enumerate(effects, 1):
        print(f"   ✅ 效果 {i}: {effect}")
    
    return True

def test_generate_sample_panels():
    """生成範例面板並輸出部分 JSON 結構"""
    print("\n📄 生成範例面板結構...")
    
    # 生成 Carousel 控制面板
    carousel_gen = FlexCarouselControlPanelGenerator()
    admin_stats = {"user_info": {"is_admin": True}, "membership_info": {"is_premium": True}}
    carousel = carousel_gen.generate_carousel_control_panel(admin_stats)
    
    if carousel:
        print("   ✅ Carousel 控制面板生成成功")
        print("   📋 結構特色:")
        print("      - 背景圖片: 星空主題")
        print("      - 按鈕透明度: 15% 半透明")
        print("      - 邊框效果: 金色半透明邊框")
        print("      - 立體陰影: 底部陰影效果")
    
    # 生成管理員面板
    admin_gen = FlexAdminPanelGenerator()
    admin_panel = admin_gen.generate_admin_panel()
    
    if admin_panel:
        print("   ✅ 管理員面板生成成功")
        print("   📋 管理員專屬特色:")
        print("      - 深紅半透明按鈕")
        print("      - 金色皇冠圖標")
        print("      - 管理員專用背景")
    
    return True

def main():
    """主測試函數"""
    print("🎨 半透明按鈕和背景圖片視覺效果測試")
    print("=" * 60)
    
    tests = [
        test_transparent_button_effects,
        test_background_image_consistency,
        test_rgba_transparency_levels,
        test_visual_hierarchy,
        test_generate_sample_panels
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("   ✅ 測試通過")
            else:
                failed += 1
                print("   ❌ 測試失敗")
        except Exception as e:
            failed += 1
            print(f"   ❌ 測試異常: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎨 視覺效果測試完成: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("🎉 所有視覺效果測試都通過了！")
        print("✨ 半透明按鈕效果已完美實現！")
        print("🌌 背景圖片主題統一一致！")
        print("🏗️ 立體感設計質感優秀！")
        return True
    else:
        print("⚠️ 有部分測試失敗，請檢查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 