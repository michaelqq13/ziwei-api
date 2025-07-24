from typing import Tuple, Dict, List

class ChineseCalendar:
    """中國曆法工具類 - 簡化版本，準備整合6tail系統"""
    
    # 天干
    HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支
    EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 五行
    FIVE_ELEMENTS = ["木", "火", "土", "金", "水"]
    
    # 天干五行對應
    STEM_ELEMENTS = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水"
    }
    
    # 地支五行對應
    BRANCH_ELEMENTS = {
        "子": "水", "丑": "土",
        "寅": "木", "卯": "木",
        "辰": "土", "巳": "火",
        "午": "火", "未": "土",
        "申": "金", "酉": "金",
        "戌": "土", "亥": "水"
    }
    
    # 時辰對應地支
    HOUR_BRANCHES = {
        23: "子", 0: "子", 1: "丑", 2: "丑",
        3: "寅", 4: "寅", 5: "卯", 6: "卯",
        7: "辰", 8: "辰", 9: "巳", 10: "巳",
        11: "午", 12: "午", 13: "未", 14: "未",
        15: "申", 16: "申", 17: "酉", 18: "酉",
        19: "戌", 20: "戌", 21: "亥", 22: "亥"
    }
    
    # 宮干起始天干對照表（根據生年天干確定寅位天干）
    PALACE_STEM_START = {
        "甲": "丙", "己": "丙",
        "乙": "戊", "庚": "戊", 
        "丙": "庚", "辛": "庚",
        "丁": "壬", "壬": "壬",
        "戊": "甲", "癸": "甲"
    }
    
    # 中文數字對照表
    CHINESE_NUMBERS = {
        "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
        "廿": 20, "卅": 30
    }

    @classmethod
    def parse_chinese_day(cls, chinese_day: str) -> int:
        """解析中文日期為數字"""
        # 去除"日"字
        day_str = chinese_day.replace('日', '')
        
        # 處理特殊情況
        if day_str == "初一":
            return 1
        elif day_str.startswith("初"):
            # 初二到初九
            return cls.CHINESE_NUMBERS[day_str[1]]
        elif day_str == "十":
            return 10
        elif day_str.startswith("十"):
            # 十一到十九
            return 10 + cls.CHINESE_NUMBERS[day_str[1]]
        elif day_str.startswith("廿"):
            # 廿一到廿九
            if len(day_str) == 1:  # 只有"廿"
                return 20
            else:
                return 20 + cls.CHINESE_NUMBERS[day_str[1]]
        elif day_str.startswith("卅") or day_str == "三十":
            # 三十 或 卅
            return 30
        else:
            # 如果無法識別，嘗試直接轉換
            try:
                return int(day_str)
            except ValueError:
                raise ValueError(f"無法解析中文日期: {chinese_day}")

    @classmethod
    def get_hour_branch(cls, hour: int) -> str:
        """根據時辰獲取地支"""
        return cls.HOUR_BRANCHES[hour]
    
    @classmethod
    def get_month_stem(cls, year_stem: str, month: int) -> str:
        """根據年干和月份獲取月干"""
        # 月干起始天干
        month_stem_start = {
            "甲": "丙", "己": "丙",
            "乙": "戊", "庚": "戊",
            "丙": "庚", "辛": "庚",
            "丁": "壬", "壬": "壬",
            "戊": "甲", "癸": "甲"
        }
        
        start_stem = month_stem_start[year_stem]
        start_index = cls.HEAVENLY_STEMS.index(start_stem)
        month_index = (start_index + (month - 1) * 2) % 10
        return cls.HEAVENLY_STEMS[month_index]
    
    @classmethod
    def get_palace_stems(cls, year_stem: str) -> Dict[str, str]:
        """根據生年天干計算各宮位天干"""
        # 獲取寅位的起始天干
        yin_stem = cls.PALACE_STEM_START[year_stem]
        yin_stem_index = cls.HEAVENLY_STEMS.index(yin_stem)
        
        # 從寅位開始分配天干
        palace_stems = {}
        
        # 地支順序：從寅開始重新排列
        branches_from_yin = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
        
        for i, branch in enumerate(branches_from_yin):
            # 天干按順序循環
            stem_index = (yin_stem_index + i) % 10
            palace_stems[branch] = cls.HEAVENLY_STEMS[stem_index]
            
        return palace_stems
    
    @classmethod
    def get_palace_order(cls, gender: str, start_branch: str) -> list:
        """獲取宮位順序"""
        # 地支位置永遠固定，按照紫微斗數盤的標準排列
        return cls.EARTHLY_BRANCHES
    
    @classmethod
    def get_element_relationship(cls, element1: str, element2: str) -> str:
        """獲取五行關係"""
        if element1 == element2:
            return "同"
            
        relationships = {
            "木": {"火": "生", "土": "剋"},
            "火": {"土": "生", "金": "剋"},
            "土": {"金": "生", "水": "剋"},
            "金": {"水": "生", "木": "剋"},
            "水": {"木": "生", "火": "剋"}
        }
        
        return relationships[element1][element2]

    @classmethod
    def parse_chinese_month(cls, lunar_month: str) -> int:
        """解析農曆月份為數字"""
        month_mapping = {
            "正月": 1, "一月": 1,
            "二月": 2, "三月": 3, "四月": 4, "五月": 5, "六月": 6,
            "七月": 7, "八月": 8, "九月": 9, "十月": 10, "十一月": 11, "十二月": 12
        }
        
        # 去除"月"字
        month_str = lunar_month.replace('月', '')
        
        return month_mapping.get(lunar_month, month_mapping.get(month_str, 1))

    @classmethod
    def get_minute_branch(cls, hour: int, minute: int) -> str:
        """
        計算分鐘地支 - 根據分鐘數計算對應地支
        每10分鐘為一個地支單位：
        0-9分鐘 -> 子, 10-19分鐘 -> 丑, 20-29分鐘 -> 寅, 30-39分鐘 -> 卯,
        40-49分鐘 -> 辰, 50-59分鐘 -> 巳
        然後循環：60-69分鐘 -> 午, 70-79分鐘 -> 未, 80-89分鐘 -> 申,
        90-99分鐘 -> 酉, 100-109分鐘 -> 戌, 110-119分鐘 -> 亥
        """
        # 計算在整個時辰內的總分鐘數
        # 每個時辰是2個小時，需要確定是時辰的第一個小時還是第二個小時
        
        # 特殊處理子時（23:00-1:00）
        if hour == 23:
            total_minutes_in_shichen = minute
        elif hour == 0:
            total_minutes_in_shichen = minute + 60
        else:
            # 其他時辰：每個時辰是連續的兩個小時
            # 時辰對照：1-3丑時，3-5寅時，5-7卯時，7-9辰時，9-11巳時，11-13午時
            # 13-15未時，15-17申時，17-19酉時，19-21戌時，21-23亥時
            
            # 判斷是時辰的第一個小時還是第二個小時
            # 奇數小時（1,3,5,7,9,11,13,15,17,19,21）是第一個小時
            # 偶數小時（2,4,6,8,10,12,14,16,18,20,22）是第二個小時
            if hour % 2 == 0:  # 偶數小時是第二個小時
                total_minutes_in_shichen = minute + 60
            else:  # 奇數小時是第一個小時
                total_minutes_in_shichen = minute
        
        # 根據總分鐘數計算地支索引
        # 每10分鐘一個地支，從子開始
        branch_index = (total_minutes_in_shichen // 10) % 12
        
        return cls.EARTHLY_BRANCHES[branch_index]

    @classmethod
    def get_hour_stem(cls, hour: int, day_stem: str = None) -> str:
        """計算時干 - 將由6tail系統替代"""
        # 暫時保留接口，實際計算將由6tail系統處理
        if day_stem:
            return day_stem
        return "甲"

    # 以下方法標記為已棄用，將由6tail系統替代
    @classmethod
    def get_year_ganzhi(cls, year: int) -> str:
        """已棄用 - 將由6tail系統替代"""
        return "甲子"
    
    @classmethod
    def get_month_ganzhi(cls, year: int, month: int) -> str:
        """已棄用 - 將由6tail系統替代"""
        return "甲子"
    
    @classmethod
    def get_day_ganzhi(cls, year: int, month: int, day: int) -> str:
        """已棄用 - 將由6tail系統替代"""
        return "甲子"
    
    @classmethod
    def get_hour_ganzhi(cls, hour: int, day_stem: str) -> str:
        """已棄用 - 將由6tail系統替代"""
        return "甲子"