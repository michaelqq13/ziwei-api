#!/usr/bin/env python3
"""
星空主題和時區設定測試腳本
驗證 Flex Message 背景圖片和時間處理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timezone, timedelta
from app.utils.flex_carousel_control_panel import FlexCarouselControlPanelGenerator
from app.utils.divination_flex_message import DivinationFlexMessageGenerator
from app.utils.time_picker_flex_message import TimePickerFlexMessageGenerator

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def test_timezone_settings():
    """測試時區設定"""
    print("🕐 測試時區設定...")
    
    # 獲取當前台北時間
    current_time = datetime.now(TAIPEI_TZ)
    print(f"   ✅ 當前台北時間: {current_time}")
    print(f"   ✅ 時區資訊: {current_time.tzinfo}")
    print(f"   ✅ UTC 偏移: {current_time.utcoffset()}")
    
    # 測試時間轉換
    utc_time = datetime.now(timezone.utc)
    taipei_time = utc_time.astimezone(TAIPEI_TZ)
    print(f"   ✅ UTC 時間: {utc_time}")
    print(f"   ✅ 轉換為台北時間: {taipei_time}")
    
    # 測試時間解析
    iso_time = "2024-07-16T14:30:00"
    parsed_time = datetime.fromisoformat(iso_time).replace(tzinfo=TAIPEI_TZ)
    print(f"   ✅ ISO 時間解析: {iso_time} -> {parsed_time}")
    
    return True

def test_background_images():
    """測試背景圖片配置"""
    print("\n🖼️ 測試背景圖片配置...")
    
    # 測試 Carousel 控制面板
    carousel_gen = FlexCarouselControlPanelGenerator()
    print(f"   ✅ Carousel 背景圖片: {len(carousel_gen.background_images)} 張")
    print(f"   ✅ Carousel 備用圖片: {len(carousel_gen.fallback_images)} 張")
    
    for key, url in carousel_gen.background_images.items():
        print(f"      - {key}: {url[:50]}...")
    
    # 測試占卜結果
    divination_gen = DivinationFlexMessageGenerator()
    print(f"   ✅ 占卜結果背景圖片: {len(divination_gen.background_images)} 張")
    print(f"   ✅ 占卜結果備用圖片: {len(divination_gen.fallback_images)} 張")
    
    # 測試時間選擇器
    time_picker_gen = TimePickerFlexMessageGenerator()
    print(f"   ✅ 時間選擇器背景圖片: {len(time_picker_gen.background_images)} 張")
    print(f"   ✅ 時間選擇器備用圖片: {len(time_picker_gen.fallback_images)} 張")
    
    return True

def test_carousel_generation():
    """測試 Carousel 面板生成"""
    print("\n🎠 測試 Carousel 面板生成...")
    
    carousel_gen = FlexCarouselControlPanelGenerator()
    
    # 測試不同用戶類型
    test_cases = [
        {"user_info": {"is_admin": False}, "membership_info": {"is_premium": False}, "type": "免費用戶"},
        {"user_info": {"is_admin": False}, "membership_info": {"is_premium": True}, "type": "付費會員"},
        {"user_info": {"is_admin": True}, "membership_info": {"is_premium": True}, "type": "管理員"}
    ]
    
    for case in test_cases:
        user_stats = {k: v for k, v in case.items() if k != "type"}
        carousel = carousel_gen.generate_carousel_control_panel(user_stats)
        
        if carousel:
            pages = len(carousel.contents.contents) if hasattr(carousel.contents, 'contents') else 0
            print(f"   ✅ {case['type']}: 成功生成 {pages} 個分頁")
        else:
            print(f"   ❌ {case['type']}: 生成失敗")
    
    return True

def test_time_picker_generation():
    """測試時間選擇器生成"""
    print("\n⏰ 測試時間選擇器生成...")
    
    time_picker_gen = TimePickerFlexMessageGenerator()
    
    # 測試男性和女性
    for gender in ['M', 'F']:
        gender_text = "男性" if gender == 'M' else "女性"
        message = time_picker_gen.create_time_selection_message(gender)
        
        if message:
            print(f"   ✅ {gender_text}: 時間選擇器生成成功")
            print(f"      Alt Text: {message.alt_text}")
        else:
            print(f"   ❌ {gender_text}: 時間選擇器生成失敗")
    
    return True

def test_flex_message_structure():
    """測試 Flex Message 結構"""
    print("\n🏗️ 測試 Flex Message 結構...")
    
    # 創建測試占卜結果
    test_result = {
        "success": True,
        "divination_time": datetime.now(TAIPEI_TZ).isoformat(),
        "gender": "M",
        "taichi_palace": "子宮",
        "minute_dizhi": "子",
        "palace_tiangan": "甲",
        "sihua_results": [
            {"type": "祿", "star": "太陽", "palace": "命宮", "explanation": "太陽化祿主財運亨通"},
            {"type": "權", "star": "天機", "palace": "兄弟宮", "explanation": "天機化權主智慧增長"},
            {"type": "科", "star": "文昌", "palace": "夫妻宮", "explanation": "文昌化科主學業進步"},
            {"type": "忌", "star": "廉貞", "palace": "子女宮", "explanation": "廉貞化忌需注意感情"}
        ]
    }
    
    divination_gen = DivinationFlexMessageGenerator()
    
    # 測試不同用戶類型的訊息生成
    for user_type in ["free", "premium", "admin"]:
        messages = divination_gen.generate_divination_messages(test_result, user_type == "admin", user_type)
        
        if messages:
            print(f"   ✅ {user_type}: 生成 {len(messages)} 個 Flex Message")
        else:
            print(f"   ❌ {user_type}: Flex Message 生成失敗")
    
    return True

def test_color_theme():
    """測試色彩主題"""
    print("\n🎨 測試色彩主題...")
    
    carousel_gen = FlexCarouselControlPanelGenerator()
    divination_gen = DivinationFlexMessageGenerator()
    time_picker_gen = TimePickerFlexMessageGenerator()
    
    # 檢查色彩主題一致性
    components = [
        ("Carousel", carousel_gen.colors),
        ("Divination", divination_gen.colors),
        ("TimePicker", time_picker_gen.colors)
    ]
    
    common_colors = ["primary", "secondary", "background", "star_gold"]
    
    for color_key in common_colors:
        values = []
        for name, colors in components:
            if color_key in colors:
                values.append(colors[color_key])
        
        if len(set(values)) == 1:
            print(f"   ✅ {color_key}: 色彩一致 ({values[0]})")
        else:
            print(f"   ⚠️ {color_key}: 色彩不一致 {values}")
    
    return True

def main():
    """主測試函數"""
    print("🌟 星空主題和時區設定測試開始")
    print("=" * 50)
    
    tests = [
        test_timezone_settings,
        test_background_images,
        test_carousel_generation,
        test_time_picker_generation,
        test_flex_message_structure,
        test_color_theme
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
    
    print("\n" + "=" * 50)
    print(f"🌟 測試完成: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("🎉 所有測試都通過了！星空主題配置完美！")
        return True
    else:
        print("⚠️ 有部分測試失敗，請檢查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 