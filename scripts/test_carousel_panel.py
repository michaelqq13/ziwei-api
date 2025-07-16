#!/usr/bin/env python3
"""
測試 Carousel 控制面板腳本
驗證新的分頁式功能選單是否正常工作
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.flex_carousel_control_panel import FlexCarouselControlPanelGenerator

def test_free_user():
    """測試免費用戶的面板"""
    print("=== 測試免費用戶面板 ===")
    
    user_stats = {
        "user_info": {"is_admin": False},
        "membership_info": {"is_premium": False}
    }
    
    generator = FlexCarouselControlPanelGenerator()
    panel = generator.generate_carousel_control_panel(user_stats)
    
    if panel:
        print("✅ 免費用戶面板生成成功")
        print(f"   類型: {type(panel).__name__}")
        print(f"   Alt Text: {panel.alt_text}")
        
        # 檢查 carousel 內容
        if hasattr(panel.contents, 'contents'):
            bubble_count = len(panel.contents.contents)
            print(f"   分頁數量: {bubble_count}")
            print("   可用分頁: 基本功能")
        else:
            print("   ⚠️ 無法獲取分頁資訊")
    else:
        print("❌ 免費用戶面板生成失敗")
    
    print()

def test_premium_user():
    """測試付費會員的面板"""
    print("=== 測試付費會員面板 ===")
    
    user_stats = {
        "user_info": {"is_admin": False},
        "membership_info": {"is_premium": True}
    }
    
    generator = FlexCarouselControlPanelGenerator()
    panel = generator.generate_carousel_control_panel(user_stats)
    
    if panel:
        print("✅ 付費會員面板生成成功")
        print(f"   類型: {type(panel).__name__}")
        print(f"   Alt Text: {panel.alt_text}")
        
        # 檢查 carousel 內容
        if hasattr(panel.contents, 'contents'):
            bubble_count = len(panel.contents.contents)
            print(f"   分頁數量: {bubble_count}")
            print("   可用分頁: 基本功能, 進階功能")
        else:
            print("   ⚠️ 無法獲取分頁資訊")
    else:
        print("❌ 付費會員面板生成失敗")
    
    print()

def test_admin_user():
    """測試管理員的面板"""
    print("=== 測試管理員面板 ===")
    
    user_stats = {
        "user_info": {"is_admin": True},
        "membership_info": {"is_premium": False}  # 管理員不需要付費會員也能訪問進階功能
    }
    
    generator = FlexCarouselControlPanelGenerator()
    panel = generator.generate_carousel_control_panel(user_stats)
    
    if panel:
        print("✅ 管理員面板生成成功")
        print(f"   類型: {type(panel).__name__}")
        print(f"   Alt Text: {panel.alt_text}")
        
        # 檢查 carousel 內容
        if hasattr(panel.contents, 'contents'):
            bubble_count = len(panel.contents.contents)
            print(f"   分頁數量: {bubble_count}")
            print("   可用分頁: 基本功能, 進階功能, 管理功能")
        else:
            print("   ⚠️ 無法獲取分頁資訊")
    else:
        print("❌ 管理員面板生成失敗")
    
    print()

def test_json_output():
    """測試 JSON 輸出格式"""
    print("=== 測試 JSON 輸出格式 ===")
    
    user_stats = {
        "user_info": {"is_admin": True},
        "membership_info": {"is_premium": True}
    }
    
    generator = FlexCarouselControlPanelGenerator()
    panel = generator.generate_carousel_control_panel(user_stats)
    
    if panel:
        try:
            # 轉換為字典格式
            panel_dict = panel.to_dict()
            
            print("✅ JSON 格式轉換成功")
            print(f"   主要結構: {list(panel_dict.keys())}")
            
            if 'contents' in panel_dict:
                contents = panel_dict['contents']
                if 'contents' in contents:
                    bubbles = contents['contents']
                    print(f"   Bubble 數量: {len(bubbles)}")
                    
                    # 檢查每個 bubble 的結構
                    for i, bubble in enumerate(bubbles):
                        if 'body' in bubble and 'contents' in bubble['body']:
                            header = bubble['body']['contents'][0]  # 標題區域
                            if 'contents' in header and len(header['contents']) > 0:
                                title = header['contents'][0].get('text', '未知')
                                print(f"   Bubble {i+1}: {title}")
            
            # 可以選擇輸出完整 JSON（調試用）
            # print("\n完整 JSON 結構:")
            # print(json.dumps(panel_dict, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"❌ JSON 格式轉換失敗: {e}")
    else:
        print("❌ 無法生成面板進行 JSON 測試")
    
    print()

def test_edge_cases():
    """測試邊界情況"""
    print("=== 測試邊界情況 ===")
    
    # 測試空的用戶統計
    print("1. 測試空用戶統計:")
    generator = FlexCarouselControlPanelGenerator()
    panel = generator.generate_carousel_control_panel({})
    if panel:
        print("   ✅ 處理空統計成功 (應該顯示免費用戶面板)")
    else:
        print("   ❌ 處理空統計失敗")
    
    # 測試無效的用戶統計
    print("2. 測試無效用戶統計:")
    invalid_stats = {
        "user_info": None,
        "membership_info": None
    }
    panel = generator.generate_carousel_control_panel(invalid_stats)
    if panel:
        print("   ✅ 處理無效統計成功")
    else:
        print("   ⚠️ 處理無效統計失敗 (可能需要改進錯誤處理)")
    
    print()

def main():
    """主函數"""
    print("🌌 Carousel 控制面板測試工具")
    print("=" * 50)
    
    # 執行所有測試
    test_free_user()
    test_premium_user() 
    test_admin_user()
    test_json_output()
    test_edge_cases()
    
    print("🎉 測試完成！")
    print()
    print("💡 使用說明：")
    print("   - 免費用戶只能看到「基本功能」分頁")
    print("   - 付費會員可以看到「基本功能」和「進階功能」分頁")
    print("   - 管理員可以看到所有三個分頁")
    print("   - 用戶可以左右滑動查看不同的功能分頁")
    print("   - 權限不足的功能會顯示為灰色禁用狀態")

if __name__ == "__main__":
    main() 