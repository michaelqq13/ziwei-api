#!/usr/bin/env python3
"""
使用6tail完整時間資料的干支計算系統
支援1900-2100年區間的準確農曆和干支計算
"""

import sys
import os
from datetime import datetime, timedelta
import logging

# 嘗試導入sxtwl（壽星萬年曆）庫
try:
    import sxtwl
    HAS_SXTWL = True
    print("✅ 成功導入sxtwl庫")
except ImportError:
    HAS_SXTWL = False
    print("❌ 未找到sxtwl庫，請先安裝：pip install sxtwl")

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SixTailCalendar:
    """使用6tail（壽星萬年曆）的完整時間資料處理類"""
    
    def __init__(self):
        """初始化6tail農曆計算器"""
        if not HAS_SXTWL:
            raise ImportError("請先安裝sxtwl庫：pip install sxtwl")
        
        self.year_range = (1900, 2100)
        
        # 天干地支對照表
        self.gan_names = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.zhi_names = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 農曆月份中文對照
        self.lunar_month_names = ["", "正月", "二月", "三月", "四月", "五月", "六月", 
                                 "七月", "八月", "九月", "十月", "十一月", "十二月"]
        
        # 農曆日期中文對照
        self.lunar_day_names = {
            1: "初一", 2: "初二", 3: "初三", 4: "初四", 5: "初五", 6: "初六", 7: "初七", 8: "初八", 9: "初九", 10: "初十",
            11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五", 16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
            21: "廿一", 22: "廿二", 23: "廿三", 24: "廿四", 25: "廿五", 26: "廿六", 27: "廿七", 28: "廿八", 29: "廿九", 30: "三十"
        }
        
        logger.info(f"6tail農曆計算器初始化完成，支援年份範圍：{self.year_range[0]}-{self.year_range[1]}")
    
    def get_complete_calendar_info(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> dict:
        """
        獲取完整的日曆信息
        
        Args:
            year: 西元年份（1900-2100）
            month: 月份（1-12）
            day: 日期（1-31）
            hour: 小時（0-23）
            minute: 分鐘（0-59）
            
        Returns:
            包含完整農曆和干支信息的字典
        """
        if not (self.year_range[0] <= year <= self.year_range[1]):
            raise ValueError(f"年份必須在{self.year_range[0]}-{self.year_range[1]}範圍內")
        
        try:
            # 使用sxtwl的fromSolar方法獲取農曆日期
            day_obj = sxtwl.fromSolar(year, month, day)
            
            # 獲取干支四柱（GZ對象）
            year_gz_obj = day_obj.getYearGZ()
            month_gz_obj = day_obj.getMonthGZ() 
            day_gz_obj = day_obj.getDayGZ()
            hour_gz_obj = day_obj.getHourGZ(hour)
            
            # 轉換GZ對象為中文干支
            year_gz = self.gan_names[year_gz_obj.tg] + self.zhi_names[year_gz_obj.dz]
            month_gz = self.gan_names[month_gz_obj.tg] + self.zhi_names[month_gz_obj.dz]
            day_gz = self.gan_names[day_gz_obj.tg] + self.zhi_names[day_gz_obj.dz]
            hour_gz = self.gan_names[hour_gz_obj.tg] + self.zhi_names[hour_gz_obj.dz]
            
            # 獲取農曆信息
            lunar_year = day_obj.getLunarYear()
            lunar_month = day_obj.getLunarMonth()
            lunar_day = day_obj.getLunarDay()
            is_leap = day_obj.isLunarLeap()
            
            # 獲取農曆月份和日期的中文表示
            lunar_month_chinese = self._get_lunar_month_chinese(lunar_month, is_leap)
            lunar_day_chinese = self._get_lunar_day_chinese(lunar_day)
            
            # 獲取節氣信息
            solar_term = ""
            if day_obj.hasJieQi():
                solar_term = day_obj.getJieQi()
            
            # 構建完整信息
            calendar_info = {
                "gregorian": {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "datetime": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
                },
                "lunar": {
                    "year": lunar_year,
                    "month": lunar_month,
                    "day": lunar_day,
                    "is_leap": is_leap,
                    "year_chinese": f"{year_gz}年",
                    "month_chinese": lunar_month_chinese,
                    "day_chinese": lunar_day_chinese,
                    "is_leap_month": is_leap
                },
                "ganzhi": {
                    "year": year_gz,
                    "month": month_gz,
                    "day": day_gz,
                    "hour": hour_gz
                },
                "solar_term": solar_term,
                "data_source": "sxtwl_6tail",
                "year_range": f"{self.year_range[0]}-{self.year_range[1]}"
            }
            
            logger.info(f"成功計算 {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} 的完整農曆信息")
            return calendar_info
            
        except Exception as e:
            logger.error(f"計算農曆信息失敗：{e}")
            raise
    
    def _get_year_ganzhi(self, lunar_year: int) -> str:
        """獲取年干支（已經在Day對象中提供，這裡保留作為參考）"""
        # 計算天干地支索引（以甲子年為起點）
        gan_index = (lunar_year - 4) % 10  # 甲子年是公元前2697年，但實際計算需要調整
        zhi_index = (lunar_year - 4) % 12
        return self.gan_names[gan_index] + self.zhi_names[zhi_index]
    
    def _get_month_ganzhi(self, lunar_year: int, lunar_month: int) -> str:
        """獲取月干支（已經在Day對象中提供，這裡保留作為參考）"""
        # 根據年干推算月干
        year_gan_index = (lunar_year - 4) % 10
        month_gan_index = (year_gan_index * 2 + lunar_month) % 10
        month_zhi_index = (lunar_month + 1) % 12  # 正月對應寅月
        return self.gan_names[month_gan_index] + self.zhi_names[month_zhi_index]
    
    def _get_day_ganzhi(self, year: int, month: int, day: int) -> str:
        """獲取日干支（已經在Day對象中提供，這裡保留作為參考）"""
        # 使用Time對象計算儒略日
        time_obj = sxtwl.Time()
        time_obj.setYear(year)
        time_obj.setMonth(month)
        time_obj.setDay(day)
        
        jd = sxtwl.toJD(time_obj)  # 轉換為儒略日
        day_cycle = int(jd - 1) % 60  # 甲子日循環
        
        gan_index = day_cycle % 10
        zhi_index = day_cycle % 12
        return self.gan_names[gan_index] + self.zhi_names[zhi_index]
    
    def _get_hour_ganzhi(self, day_ganzhi: str, hour: int) -> str:
        """獲取時干支（已經在Day對象中提供，這裡保留作為參考）"""
        # 計算時辰索引
        hour_zhi_index = self._hour_to_zhi_index(hour)
        
        # 根據日干推算時干
        day_gan = day_ganzhi[0]
        day_gan_index = self.gan_names.index(day_gan)
        hour_gan_index = (day_gan_index * 2 + hour_zhi_index) % 10
        
        return self.gan_names[hour_gan_index] + self.zhi_names[hour_zhi_index]
    
    def _hour_to_zhi_index(self, hour: int) -> int:
        """將24小時制轉換為地支索引"""
        # 23-1點是子時（0）, 1-3點是丑時（1）, 以此類推
        if hour == 23:
            return 0  # 子
        else:
            return (hour + 1) // 2 % 12
    
    def _get_lunar_month_chinese(self, lunar_month: int, is_leap: bool) -> str:
        """獲取農曆月份的中文表示"""
        if lunar_month < len(self.lunar_month_names):
            month_name = self.lunar_month_names[lunar_month]
            if is_leap:
                return f"閏{month_name}"
            return month_name
        return f"{lunar_month}月"
    
    def _get_lunar_day_chinese(self, lunar_day: int) -> str:
        """獲取農曆日期的中文表示"""
        return self.lunar_day_names.get(lunar_day, f"{lunar_day}日")
    
    def batch_generate_data(self, start_year: int, end_year: int, save_to_file: bool = True) -> list:
        """
        批量生成指定年份範圍的完整時間資料
        
        Args:
            start_year: 開始年份
            end_year: 結束年份
            save_to_file: 是否保存到文件
            
        Returns:
            生成的資料列表
        """
        logger.info(f"開始批量生成 {start_year}-{end_year} 年的完整時間資料...")
        
        all_data = []
        total_records = 0
        
        for year in range(start_year, end_year + 1):
            logger.info(f"處理 {year} 年...")
            
            # 處理該年的每一天
            current_date = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31)
            
            while current_date <= year_end:
                # 為每一天的每個小時生成資料（可選擇只生成關鍵時辰）
                for hour in [0, 6, 12, 18]:  # 只生成四個關鍵時辰的資料
                    try:
                        calendar_info = self.get_complete_calendar_info(
                            current_date.year, current_date.month, current_date.day, hour
                        )
                        all_data.append(calendar_info)
                        total_records += 1
                        
                        if total_records % 1000 == 0:
                            logger.info(f"已生成 {total_records} 條記錄...")
                            
                    except Exception as e:
                        logger.error(f"生成 {current_date.date()} {hour}:00 資料失敗：{e}")
                
                current_date += timedelta(days=1)
        
        logger.info(f"✅ 批量生成完成！總共生成 {total_records} 條記錄")
        
        if save_to_file:
            self._save_to_json(all_data, f"complete_6tail_data_{start_year}_{end_year}.json")
        
        return all_data
    
    def _save_to_json(self, data: list, filename: str):
        """保存資料到JSON文件"""
        import json
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"資料已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存資料失敗：{e}")


def test_6tail_calendar():
    """測試6tail農曆計算功能"""
    if not HAS_SXTWL:
        print("請先安裝sxtwl庫：pip install sxtwl")
        return
    
    try:
        calendar = SixTailCalendar()
        
        # 測試當前時間
        now = datetime.now()
        result = calendar.get_complete_calendar_info(
            now.year, now.month, now.day, now.hour, now.minute
        )
        
        print("\n=== 6tail完整時間資料測試 ===")
        print(f"西元日期：{result['gregorian']['datetime']}")
        print(f"農曆日期：{result['lunar']['year_chinese']} {result['lunar']['month_chinese']}{result['lunar']['day_chinese']}")
        print(f"年干支：{result['ganzhi']['year']}")
        print(f"月干支：{result['ganzhi']['month']}")
        print(f"日干支：{result['ganzhi']['day']}")
        print(f"時干支：{result['ganzhi']['hour']}")
        print(f"節氣：{result['solar_term'] or '無'}")
        print(f"資料來源：{result['data_source']}")
        print(f"支援年份：{result['year_range']}")
        
        # 測試一些特殊日期
        test_dates = [
            (2000, 1, 1),  # 千禧年
            (2024, 2, 10), # 龍年春節
            (2025, 1, 29), # 蛇年春節
            (1900, 1, 1),  # 範圍起始
            (2100, 12, 31) # 範圍結束
        ]
        
        print("\n=== 特殊日期測試 ===")
        for year, month, day in test_dates:
            try:
                result = calendar.get_complete_calendar_info(year, month, day)
                print(f"{year}-{month:02d}-{day:02d}: {result['ganzhi']['day']} | {result['lunar']['month_chinese']}{result['lunar']['day_chinese']}")
            except Exception as e:
                print(f"{year}-{month:02d}-{day:02d}: 計算失敗 - {e}")
        
        print("\n✅ 6tail時間資料測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗：{e}")


if __name__ == "__main__":
    print("6tail完整時間資料系統")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_6tail_calendar()
        
        elif command == "generate":
            if not HAS_SXTWL:
                print("請先安裝sxtwl庫：pip install sxtwl")
                sys.exit(1)
            
            start_year = int(sys.argv[2]) if len(sys.argv) > 2 else 2020
            end_year = int(sys.argv[3]) if len(sys.argv) > 3 else 2030
            
            calendar = SixTailCalendar()
            calendar.batch_generate_data(start_year, end_year)
        
        else:
            print("用法：")
            print("  python main.py test          # 測試功能")
            print("  python main.py generate 2020 2030  # 生成指定年份資料")
    
    else:
        # 默認執行測試
        test_6tail_calendar() 