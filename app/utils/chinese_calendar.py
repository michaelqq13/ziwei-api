from typing import Tuple, Dict, List

class ChineseCalendar:
    """中國曆法工具類"""
    
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
        """解析中文日期為數字
        
        Args:
            chinese_day: 中文日期，如"初一"、"十五"、"廿九"等
            
        Returns:
            對應的數字日期
        """
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
        elif day_str.startswith("卅"):
            # 三十
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
        """根據生年天干計算各宮位天干
        
        Args:
            year_stem: 生年天干
            
        Returns:
            各地支對應的天干字典
        """
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
        """獲取宮位順序
        
        Args:
            gender: 'M' 為男，'F' 為女（保留參數以維持接口兼容性，但不再使用）
            start_branch: 起始地支（命宮地支）
            
        Returns:
            固定的十二地支順序（地支位置永遠不變）
        """
        # 地支位置永遠固定，按照紫微斗數盤的標準排列
        # 順序：子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥
        return cls.EARTHLY_BRANCHES
    
    @classmethod
    def get_element_relationship(cls, element1: str, element2: str) -> str:
        """獲取五行關係
        
        Returns:
            '生' - 相生
            '剋' - 相剋
            '同' - 相同
        """
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
    def parse_chinese_month(cls, chinese_month: str) -> int:
        """解析中文月份為數字
        
        Args:
            chinese_month: 中文月份，如"正月"、"二月"、"五月"、"闰三月"等
            
        Returns:
            對應的數字月份
        """
        month_mapping = {
            "正月": 1, "一月": 1,
            "二月": 2, "三月": 3, "四月": 4, "五月": 5, "六月": 6,
            "七月": 7, "八月": 8, "九月": 9, "十月": 10,
            "十一月": 11, "冬月": 11,
            "十二月": 12, "臘月": 12
        }
        
        # 處理閏月的情況 - 去除"闰"字
        clean_month = chinese_month.replace('闰', '').replace('閏', '')
        
        # 去除"月"字進行匹配
        month_str = clean_month.replace('月', '') + '月'
        
        if month_str in month_mapping:
            return month_mapping[month_str]
        else:
            # 如果無法識別，嘗試直接轉換
            try:
                return int(clean_month.replace('月', ''))
            except ValueError:
                raise ValueError(f"無法解析中文月份: {chinese_month}") 

    @classmethod
    def get_minute_branch(cls, hour: int, minute: int) -> str:
        """根據時分獲取分支
        
        每個時辰120分鐘，等分成12段，每段10分鐘
        按地支順序分配：0-9分鐘→子，10-19分鐘→丑，...，110-119分鐘→亥
        """
        # 計算在當前時辰內的總分鐘數（0-119）
        # 每個時辰跨越兩個小時
        if hour % 2 == 1:  # 奇數小時是時辰的前半段 (0-59分鐘)
            minute_in_shichen = minute
        else:  # 偶數小時是時辰的後半段 (60-119分鐘)  
            minute_in_shichen = 60 + minute
            
        # 每10分鐘一個地支段 (0-11)
        segment = minute_in_shichen // 10
        
        # 限制在0-11範圍內
        segment = min(segment, 11)
        
        # 直接按地支順序分配：0→子，1→丑，2→寅，...，11→亥
        return cls.EARTHLY_BRANCHES[segment]
    
    @classmethod
    def get_hour_stem(cls, hour: int, day_stem: str = None) -> str:
        """根據小時和日干獲取時干
        
        Args:
            hour: 小時（0-23）
            day_stem: 日干（如果提供，則基於日干計算時干）
            
        Returns:
            對應的天干
        """
        if day_stem:
            # 根據日干確定子時天干
            stem_start = {
                "甲": "甲", "己": "甲",  # 甲己日起甲
                "乙": "丙", "庚": "丙",  # 乙庚日起丙
                "丙": "戊", "辛": "戊",  # 丙辛日起戊
                "丁": "庚", "壬": "庚",  # 丁壬日起庚
                "戊": "壬", "癸": "壬"   # 戊癸日起壬
            }[day_stem]
            
            # 獲取子時天干的索引
            start_index = cls.HEAVENLY_STEMS.index(stem_start)
            
            # 計算時辰索引（每兩個小時一個時辰）
            hour_index = hour // 2
            
            # 計算時干索引（每個時辰天干加兩個）
            stem_index = (start_index + hour_index * 2) % 10
            
            return cls.HEAVENLY_STEMS[stem_index]
        else:
            # 如果沒有提供日干，則使用簡化計算（不推薦）
            stem_index = (hour // 2) % 10
            return cls.HEAVENLY_STEMS[stem_index]