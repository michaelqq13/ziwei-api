#!/usr/bin/env python3
"""
修復BirthInfo構造函數調用
"""

def fix_birth_info_calls():
    """修復linebot_routes.py中的BirthInfo調用"""
    file_path = "app/api/linebot_routes.py"
    
    # 讀取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替換所有BirthInfo構造函數調用
    old_pattern = """birth_info = BirthInfo(
                birth_year=session.birth_info.birth_year,
                birth_month=session.birth_info.birth_month,
                birth_day=session.birth_info.birth_day,
                birth_hour=session.birth_info.birth_hour,
                birth_minute=session.birth_info.birth_minute or 0,
                gender=session.birth_info.gender,
                is_leap_month=session.birth_info.is_leap_month or False,
                calendar_type=session.birth_info.calendar_type or "lunar",
                timezone=session.birth_info.timezone or "Asia/Taipei"
            )"""
    
    new_pattern = """birth_info = BirthInfo(
                year=session.birth_info.birth_year,
                month=session.birth_info.birth_month,
                day=session.birth_info.birth_day,
                hour=session.birth_info.birth_hour,
                minute=session.birth_info.birth_minute or 0,
                gender=session.birth_info.gender,
                longitude=121.5654,  # 台北經度
                latitude=25.0330     # 台北緯度
            )"""
    
    content = content.replace(old_pattern, new_pattern)
    
    # 寫回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修復 {file_path} 中的BirthInfo調用")

if __name__ == "__main__":
    fix_birth_info_calls()
    print("=== 修復完成 ===") 