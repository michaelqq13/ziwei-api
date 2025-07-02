#!/usr/bin/env python3
"""
簡單四化計算測試腳本
用於驗證四化星計算邏輯，不需要數據庫連接
"""

import os
import sys

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.logic.star_calculator import StarCalculator

def test_four_transformations_logic():
    """測試四化計算邏輯"""
    print("=" * 50)
    print("四化計算邏輯測試")
    print("=" * 50)
    
    star_calculator = StarCalculator()
    
    print("四化對照表：")
    print("=" * 30)
    
    for year_stem, transformations in star_calculator.FOUR_TRANSFORMATIONS.items():
        print(f"年干 {year_stem}：")
        for trans_type, star_name in transformations.items():
            print(f"  {star_name}化{trans_type}")
        print()
    
    print("=" * 30)
    print("測試特定年干的四化")
    print("=" * 30)
    
    # 測試 1995 年（乙年）的四化
    test_year_stem = "乙"
    if test_year_stem in star_calculator.FOUR_TRANSFORMATIONS:
        transformations = star_calculator.FOUR_TRANSFORMATIONS[test_year_stem]
        print(f"1995年（{test_year_stem}年）的四化：")
        for trans_type, star_name in transformations.items():
            print(f"  {star_name}化{trans_type}")
    
    print()
    print("=" * 30)
    print("模擬宮位和星曜")
    print("=" * 30)
    
    # 模擬一個簡單的宮位結構
    mock_palaces = {
        "命宮": {"dizhi": "子", "stars": ["太陰", "天同"]},
        "兄弟": {"dizhi": "丑", "stars": ["天機", "巨門"]},
        "夫妻": {"dizhi": "寅", "stars": ["紫微", "貪狼"]},
        "子女": {"dizhi": "卯", "stars": ["天府", "太陽"]},
        "財帛": {"dizhi": "辰", "stars": ["武曲", "天相"]},
        "疾厄": {"dizhi": "巳", "stars": ["廉貞", "七殺"]},
        "遷移": {"dizhi": "午", "stars": ["破軍"]},
        "交友": {"dizhi": "未", "stars": ["文昌", "文曲"]},
        "官祿": {"dizhi": "申", "stars": ["左輔", "右弼"]},
        "田宅": {"dizhi": "酉", "stars": ["天鉞", "天魁"]},
        "福德": {"dizhi": "戌", "stars": ["祿存"]},
        "父母": {"dizhi": "亥", "stars": ["天馬", "擎羊"]}
    }
    
    print("模擬命盤：")
    for palace_name, palace_info in mock_palaces.items():
        stars = palace_info["stars"]
        print(f"【{palace_name}】{palace_info['dizhi']}：{', '.join(stars)}")
    
    print()
    print("=" * 30)
    print("四化星搜尋測試")
    print("=" * 30)
    
    # 測試四化星搜尋
    if test_year_stem in star_calculator.FOUR_TRANSFORMATIONS:
        transformations = star_calculator.FOUR_TRANSFORMATIONS[test_year_stem]
        for trans_type, star_name in transformations.items():
            found = False
            found_in_palace = "未找到"
            
            for palace_name, palace_info in mock_palaces.items():
                stars = palace_info["stars"]
                for star in stars:
                    # 清理星曜名稱
                    clean_star_name = star.split("（")[0] if "（" in star else star
                    clean_star_name = clean_star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "").strip()
                    
                    if clean_star_name == star_name:
                        found = True
                        found_in_palace = palace_name
                        break
                if found:
                    break
            
            status = "✅ 找到" if found else "❌ 未找到"
            print(f"{star_name}化{trans_type}：{status} (在 {found_in_palace})")
    
    print()
    print("=" * 30)
    print("模擬四化應用")
    print("=" * 30)
    
    # 模擬應用四化
    applied_transformations = []
    missing_stars = []
    
    if test_year_stem in star_calculator.FOUR_TRANSFORMATIONS:
        transformations = star_calculator.FOUR_TRANSFORMATIONS[test_year_stem]
        for trans_type, star_name in transformations.items():
            star_found = False
            
            for palace_name, palace_info in mock_palaces.items():
                stars = palace_info["stars"]
                for i, star in enumerate(stars):
                    clean_star_name = star.split("（")[0] if "（" in star else star
                    clean_star_name = clean_star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "").strip()
                    
                    if clean_star_name == star_name:
                        # 應用四化
                        new_star_name = f"{star_name}化{trans_type}"
                        mock_palaces[palace_name]["stars"][i] = new_star_name
                        applied_transformations.append({
                            "star": star_name,
                            "transformation": trans_type,
                            "palace": palace_name
                        })
                        star_found = True
                        break
                if star_found:
                    break
            
            if not star_found:
                missing_stars.append(f"{star_name}化{trans_type}")
    
    print("成功應用的四化：")
    for trans in applied_transformations:
        print(f"  {trans['star']}化{trans['transformation']} → {trans['palace']}")
    
    if missing_stars:
        print("\n遺漏的四化星：")
        for star in missing_stars:
            print(f"  ❌ {star}")
    
    print()
    print("=" * 30)
    print("應用四化後的命盤")
    print("=" * 30)
    
    sihua_count = 0
    for palace_name, palace_info in mock_palaces.items():
        stars = palace_info["stars"]
        sihua_stars = [star for star in stars if any(marker in star for marker in ["化祿", "化權", "化科", "化忌"])]
        if sihua_stars:
            print(f"【{palace_name}】：{', '.join(sihua_stars)}")
            sihua_count += len(sihua_stars)
    
    print()
    print(f"總共應用了 {sihua_count} 個四化星")
    print(f"遺漏了 {len(missing_stars)} 個四化星")
    
    if sihua_count == 4:
        print("✅ 四化星數量正確")
    else:
        print("❌ 四化星數量不正確，應該是 4 個")

if __name__ == "__main__":
    test_four_transformations_logic() 