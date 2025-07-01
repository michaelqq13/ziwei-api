from typing import Dict, List, Optional, Tuple
from app.models.stars import Star, star_registry
from app.utils.chinese_calendar import ChineseCalendar
from app.data.heavenly_stems.four_transformations import four_transformations_explanations
import logging

logger = logging.getLogger(__name__)

class StarCalculator:
    """星曜計算工具類"""
    
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    PALACE_NAMES = ["命宮", "父母宮", "福德宮", "田宅宮", "官祿宮", "交友宮", "遷移宮", "疾厄宮", "財帛宮", "子女宮", "夫妻宮", "兄弟宮"]
    
    # 身宮所在宮位對應時辰的對照表
    BODY_PALACE_MAPPING = {
        "子": "命宮",  # 子時(23:00~01:00)
        "午": "命宮",  # 午時(11:00~13:00)
        "丑": "福德", # 丑時(01:00~03:00)
        "未": "福德", # 未時(13:00~15:00)
        "寅": "官祿", # 寅時(03:00~05:00)
        "申": "官祿", # 申時(15:00~17:00)
        "卯": "遷移", # 卯時(05:00~07:00)
        "酉": "遷移", # 酉時(17:00~19:00)
        "辰": "財帛", # 辰時(07:00~09:00)
        "戌": "財帛", # 戌時(19:00~21:00)
        "巳": "夫妻", # 巳時(09:00~11:00)
        "亥": "夫妻"  # 亥時(21:00~23:00)
    }
    
    # 五行局配置
    FIVE_ELEMENTS_CHART = {
        "甲": { "子": "水二局", "丑": "水二局", "寅": "火六局", "卯": "火六局", "辰": "木三局", "巳": "木三局", 
               "午": "土五局", "未": "土五局", "申": "金四局", "酉": "金四局", "戌": "火六局", "亥": "火六局" },
        "己": { "子": "水二局", "丑": "水二局", "寅": "火六局", "卯": "火六局", "辰": "木三局", "巳": "木三局", 
               "午": "土五局", "未": "土五局", "申": "金四局", "酉": "金四局", "戌": "火六局", "亥": "火六局" },
        "乙": { "子": "火六局", "丑": "火六局", "寅": "土五局", "卯": "土五局", "辰": "金四局", "巳": "金四局", 
               "午": "木三局", "未": "木三局", "申": "水二局", "酉": "水二局", "戌": "土五局", "亥": "土五局" },
        "庚": { "子": "火六局", "丑": "火六局", "寅": "土五局", "卯": "土五局", "辰": "金四局", "巳": "金四局", 
               "午": "木三局", "未": "木三局", "申": "水二局", "酉": "水二局", "戌": "土五局", "亥": "土五局" },
        "丙": { "子": "土五局", "丑": "土五局", "寅": "木三局", "卯": "木三局", "辰": "水二局", "巳": "水二局", 
               "午": "金四局", "未": "金四局", "申": "火六局", "酉": "火六局", "戌": "木三局", "亥": "木三局" },
        "辛": { "子": "土五局", "丑": "土五局", "寅": "木三局", "卯": "木三局", "辰": "水二局", "巳": "水二局", 
               "午": "金四局", "未": "金四局", "申": "火六局", "酉": "火六局", "戌": "木三局", "亥": "木三局" },
        "丁": { "子": "木三局", "丑": "木三局", "寅": "金四局", "卯": "金四局", "辰": "火六局", "巳": "火六局", 
               "午": "水二局", "未": "水二局", "申": "土五局", "酉": "土五局", "戌": "金四局", "亥": "金四局" },
        "壬": { "子": "木三局", "丑": "木三局", "寅": "金四局", "卯": "金四局", "辰": "火六局", "巳": "火六局", 
               "午": "水二局", "未": "水二局", "申": "土五局", "酉": "土五局", "戌": "金四局", "亥": "金四局" },
        "戊": { "子": "金四局", "丑": "金四局", "寅": "水二局", "卯": "水二局", "辰": "土五局", "巳": "土五局", 
               "午": "火六局", "未": "火六局", "申": "木三局", "酉": "木三局", "戌": "水二局", "亥": "水二局" },
        "癸": { "子": "金四局", "丑": "金四局", "寅": "水二局", "卯": "水二局", "辰": "土五局", "巳": "土五局", 
               "午": "火六局", "未": "火六局", "申": "木三局", "酉": "木三局", "戌": "水二局", "亥": "水二局" }
    }
    
    # 五行局數值
    FIVE_ELEMENTS_VALUE = {
        "水二局": 2,
        "木三局": 3,
        "金四局": 4,
        "土五局": 5,
        "火六局": 6
    }
    
    # 紫微星落宮對照表
    PURPLE_STAR_POSITIONS = {
        "水二局": {
            "01": "丑", "02": "寅", "03": "寅", "04": "卯", "05": "卯", "06": "辰", "07": "辰", "08": "巳", "09": "巳", "10": "午",
            "11": "午", "12": "未", "13": "未", "14": "申", "15": "申", "16": "酉", "17": "酉", "18": "戌", "19": "戌", "20": "亥",
            "21": "亥", "22": "子", "23": "子", "24": "丑", "25": "丑", "26": "寅", "27": "寅", "28": "卯", "29": "卯", "30": "辰"
        },
        "木三局": {
            "01": "辰", "02": "丑", "03": "寅", "04": "巳", "05": "寅", "06": "卯", "07": "午", "08": "卯", "09": "辰", "10": "未",
            "11": "辰", "12": "巳", "13": "申", "14": "巳", "15": "午", "16": "酉", "17": "午", "18": "未", "19": "戌", "20": "未",
            "21": "申", "22": "亥", "23": "申", "24": "酉", "25": "子", "26": "酉", "27": "戌", "28": "丑", "29": "戌", "30": "亥"
        },
        "金四局": {
            "01": "亥", "02": "辰", "03": "丑", "04": "寅", "05": "子", "06": "巳", "07": "寅", "08": "卯", "09": "丑", "10": "午",
            "11": "卯", "12": "辰", "13": "寅", "14": "未", "15": "辰", "16": "巳", "17": "卯", "18": "申", "19": "巳", "20": "午",
            "21": "辰", "22": "酉", "23": "午", "24": "未", "25": "巳", "26": "戌", "27": "未", "28": "申", "29": "午", "30": "亥"
        },
        "土五局": {
            "01": "午", "02": "亥", "03": "辰", "04": "丑", "05": "寅", "06": "未", "07": "子", "08": "巳", "09": "寅", "10": "卯",
            "11": "申", "12": "丑", "13": "午", "14": "卯", "15": "辰", "16": "酉", "17": "寅", "18": "未", "19": "辰", "20": "巳",
            "21": "戌", "22": "卯", "23": "申", "24": "巳", "25": "午", "26": "亥", "27": "辰", "28": "酉", "29": "午", "30": "未"
        },
        "火六局": {
            "01": "酉", "02": "午", "03": "亥", "04": "辰", "05": "丑", "06": "寅", "07": "戌", "08": "未", "09": "子", "10": "巳",
            "11": "寅", "12": "卯", "13": "亥", "14": "申", "15": "丑", "16": "午", "17": "卯", "18": "辰", "19": "子", "20": "酉",
            "21": "寅", "22": "未", "23": "辰", "24": "巳", "25": "丑", "26": "戌", "27": "卯", "28": "申", "29": "巳", "30": "午"
        }
    }
    
    # 基本盤配置
    BASIC_CHARTS = {
        "子": {
            "子": "紫微（平和）", "丑": "", "寅": "破軍（平和）", "卯": "", 
            "辰": "廉貞（平和）、天府（入廟）", "巳": "太陰（落陷）", 
            "午": "貪狼（旺地）", "未": "天同（落陷）、巨門（落陷）", 
            "申": "武曲（平和）、天相（入廟）", "酉": "太陽（平和）、天梁（平和）", 
            "戌": "七殺（入廟）", "亥": "天機（平和）"
        },
        "丑": {
            "子": "天機（入廟）", "丑": "紫微（入廟）、破軍（旺地）", "寅": "", 
            "卯": "天府（平和）", "辰": "太陰（落陷）", "巳": "廉貞（落陷）、貪狼（落陷）", 
            "午": "巨門（旺地）", "未": "天相（平和）", "申": "天同（旺地）、天梁（落陷）", 
            "酉": "武曲（平和）、七殺（旺地）", "戌": "太陽（落陷）", "亥": ""
        },
        "寅": {
            "子": "破軍（入廟）", "丑": "天機（落陷）", "寅": "紫微（旺地）、天府（入廟）", 
            "卯": "太陰（落陷）", "辰": "貪狼（入廟）", "巳": "巨門（旺地）", 
            "午": "廉貞（平和）、天相（入廟）", "未": "天梁（旺地）", "申": "七殺（入廟）", 
            "酉": "天同（平和）", "戌": "武曲（入廟）", "亥": "太陽（落陷）"
        },
        "卯": {
            "子": "太陽（落陷）", "丑": "天府（入廟）", "寅": "天機（平和）、太陰（旺地）", 
            "卯": "紫微（旺地）、貪狼（平和）", "辰": "巨門（落陷）", "巳": "天相（平和）", 
            "午": "天梁（入廟）", "未": "廉貞（平和）、七殺（入廟）", "申": "", "酉": "", 
            "戌": "天同（平和）", "亥": "武曲（平和）、破軍（平和）"
        },
        "辰": {
            "子": "武曲（平和）、天府（入廟）", "丑": "太陽（落陷）、太陰（入廟）", 
            "寅": "貪狼（平和）", "卯": "天機（旺地）、巨門（入廟）", 
            "辰": "紫微（平和）、天相（平和）", "巳": "天梁（落陷）", "午": "七殺（旺地）", 
            "未": "", "申": "廉貞（入廟）", "酉": "", "戌": "破軍（旺地）", "亥": "天同（入廟）"
        },
        "巳": {
            "子": "天同（旺地）、太陰（入廟）", "丑": "武曲（入廟）、貪狼（入廟）", 
            "寅": "太陽（旺地）、巨門（入廟）", "卯": "天相（落陷）", 
            "辰": "天機（平和）、天梁（入廟）", "巳": "紫微（旺地）、七殺（平和）", 
            "午": "", "未": "", "申": "", "酉": "廉貞（平和）、破軍（落陷）", "戌": "", "亥": "天府（平和）"
        },
        "午": {
            "子": "貪狼（旺地）", "丑": "天同（落陷）、巨門（落陷）", 
            "寅": "武曲（平和）、天相（入廟）", "卯": "太陽（入廟）、天梁（入廟）", 
            "辰": "七殺（入廟）", "巳": "天機（平和）", "午": "紫微（入廟）", 
            "未": "", "申": "破軍（平和）", "酉": "", "戌": "廉貞（平和）、天府（入廟）", "亥": "太陰（入廟）"
        },
        "未": {
            "子": "巨門（旺地）", "丑": "天相（平和）", "寅": "天同（平和）、天梁（廟旺）", 
            "卯": "武曲（平和）、七殺（旺地）", "辰": "太陽（旺地）", "巳": "", 
            "午": "天機（入廟）", "未": "紫微（入廟）、破軍（旺地）", "申": "", 
            "酉": "天府（旺地）", "戌": "太陰（旺地）", "亥": "廉貞（落陷）、貪狼（落陷）"
        },
        "申": {
            "子": "廉貞（平和）、天相（入廟）", "丑": "天梁（旺地）", "寅": "七殺（入廟）", 
            "卯": "天同（平和）", "辰": "武曲（入廟）", "巳": "太陽（旺地）", 
            "午": "破軍（入廟）", "未": "天機（落陷）", "申": "紫微（旺地）、天府（平和）", 
            "酉": "太陰（旺地）", "戌": "貪狼（入廟）", "亥": "巨門（旺地）"
        },
        "酉": {
            "子": "天梁（入廟）", "丑": "廉貞（平和）、七殺（入廟）", "寅": "", "卯": "", 
            "辰": "天同（平和）", "巳": "武曲（平和）、破軍（平和）", "午": "太陽（旺地）", 
            "未": "天府（入廟）", "申": "天機（平和）、太陰（平和）", 
            "酉": "紫微（旺地）、貪狼（平和）", "戌": "巨門（落陷）", "亥": "天相（平和）"
        },
        "戌": {
            "子": "七殺（旺地）", "丑": "", "寅": "廉貞（入廟）", "卯": "", 
            "辰": "破軍（旺地）", "巳": "天同（入廟）", "午": "武曲（旺地）、天府（旺地）", 
            "未": "太陽（平和）、太陰（落陷）", "申": "貪狼（平和）", 
            "酉": "天機（平和）、巨門（入廟）", "戌": "紫微（平和）、天相（平和）", "亥": "天梁（落陷）"
        },
        "亥": {
            "子": "", "丑": "", "寅": "", "卯": "廉貞（平和）、破軍（落陷）", "辰": "", 
            "巳": "天府（平和）", "午": "天同（落陷）、太陰（落陷）", 
            "未": "武曲（廟旺）、貪狼（廟旺）", "申": "太陽（平和）、巨門（入廟）", 
            "酉": "天相（落陷）", "戌": "天機（平和）、天梁（旺地）", "亥": "紫微（旺地）、七殺（平和）"
        }
    }
    
    # 四化對照表
    FOUR_TRANSFORMATIONS = {
        '甲': {'祿': '廉貞', '權': '破軍', '科': '武曲', '忌': '太陽'},
        '乙': {'祿': '天機', '權': '天梁', '科': '紫微', '忌': '太陰'},
        '丙': {'祿': '天同', '權': '天機', '科': '文昌', '忌': '廉貞'},
        '丁': {'祿': '太陰', '權': '天同', '科': '天機', '忌': '巨門'},
        '戊': {'祿': '貪狼', '權': '太陰', '科': '右弼', '忌': '天機'},
        '己': {'祿': '武曲', '權': '貪狼', '科': '天梁', '忌': '文曲'},
        '庚': {'祿': '太陽', '權': '武曲', '科': '太陰', '忌': '天同'},
        '辛': {'祿': '巨門', '權': '太陽', '科': '文曲', '忌': '文昌'},
        '壬': {'祿': '天梁', '權': '紫微', '科': '左輔', '忌': '武曲'},
        '癸': {'祿': '破軍', '權': '巨門', '科': '太陰', '忌': '貪狼'}
    }

    # 年干對應吉凶星地支位置表
    LUCK_TABLE = {
        "甲": { "祿存": "寅", "擎羊": "卯", "陀羅": "丑", "天魁": "丑", "天鉞": "未" },
        "乙": { "祿存": "卯", "擎羊": "辰", "陀羅": "寅", "天魁": "子", "天鉞": "申" },
        "丙": { "祿存": "巳", "擎羊": "午", "陀羅": "辰", "天魁": "亥", "天鉞": "酉" },
        "丁": { "祿存": "午", "擎羊": "未", "陀羅": "巳", "天魁": "亥", "天鉞": "酉" },
        "戊": { "祿存": "巳", "擎羊": "午", "陀羅": "辰", "天魁": "丑", "天鉞": "未" },
        "己": { "祿存": "午", "擎羊": "未", "陀羅": "巳", "天魁": "子", "天鉞": "申" },
        "庚": { "祿存": "申", "擎羊": "酉", "陀羅": "未", "天魁": "丑", "天鉞": "未" },
        "辛": { "祿存": "酉", "擎羊": "戌", "陀羅": "申", "天魁": "午", "天鉞": "寅" },
        "壬": { "祿存": "亥", "擎羊": "子", "陀羅": "戌", "天魁": "卯", "天鉞": "巳" },
        "癸": { "祿存": "子", "擎羊": "丑", "陀羅": "亥", "天魁": "卯", "天鉞": "巳" }
    }

    # 農曆月對應左輔、右弼地支分布表
    MONTHLY_STARS_TABLE = {
        1:  { "左輔": "辰", "右弼": "戌" },
        2:  { "左輔": "巳", "右弼": "酉" },
        3:  { "左輔": "午", "右弼": "申" },
        4:  { "左輔": "未", "右弼": "未" },
        5:  { "左輔": "申", "右弼": "午" },
        6:  { "左輔": "酉", "右弼": "巳" },
        7:  { "左輔": "戌", "右弼": "辰" },
        8:  { "左輔": "亥", "右弼": "卯" },
        9:  { "左輔": "子", "右弼": "寅" },
        10: { "左輔": "丑", "右弼": "丑" },
        11: { "左輔": "寅", "右弼": "子" },
        12: { "左輔": "卯", "右弼": "亥" }
    }

    # 時辰地支對應文曲、文昌、地空、地劫分布表
    HOURLY_STARS_TABLE = {
        "子": { "文曲": "辰", "文昌": "戌", "地空": "亥", "地劫": "亥" },
        "丑": { "文曲": "巳", "文昌": "酉", "地空": "戌", "地劫": "子" },
        "寅": { "文曲": "午", "文昌": "申", "地空": "酉", "地劫": "丑" },
        "卯": { "文曲": "未", "文昌": "未", "地空": "申", "地劫": "寅" },
        "辰": { "文曲": "申", "文昌": "午", "地空": "未", "地劫": "卯" },
        "巳": { "文曲": "酉", "文昌": "巳", "地空": "午", "地劫": "辰" },
        "午": { "文曲": "戌", "文昌": "辰", "地空": "巳", "地劫": "巳" },
        "未": { "文曲": "亥", "文昌": "卯", "地空": "辰", "地劫": "午" },
        "申": { "文曲": "子", "文昌": "寅", "地空": "卯", "地劫": "未" },
        "酉": { "文曲": "丑", "文昌": "丑", "地空": "寅", "地劫": "申" },
        "戌": { "文曲": "寅", "文昌": "子", "地空": "丑", "地劫": "酉" },
        "亥": { "文曲": "卯", "文昌": "亥", "地空": "子", "地劫": "戌" }
    }

    # 時辰順序為 ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    # 火星落宮表
    FIRE_STAR_TABLE = {
        "子": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
        "丑": ["卯","辰","巳","午","未","申","酉","戌","亥","子","丑","寅"],
        "寅": ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"],
        "卯": ["酉","戌","亥","子","丑","寅","卯","辰","巳","午","未","申"],
        "辰": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
        "巳": ["卯","辰","巳","午","未","申","酉","戌","亥","子","丑","寅"],
        "午": ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"],
        "未": ["酉","戌","亥","子","丑","寅","卯","辰","巳","午","未","申"],
        "申": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
        "酉": ["卯","辰","巳","午","未","申","酉","戌","亥","子","丑","寅"],
        "戌": ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"],
        "亥": ["酉","戌","亥","子","丑","寅","卯","辰","巳","午","未","申"]
    }

    # 鈴星落宮表
    BELL_STAR_TABLE = {
        "子": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "丑": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "寅": ["卯","辰","巳","午","未","申","酉","戌","亥","子","丑","寅"],
        "卯": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "辰": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "巳": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "午": ["卯","辰","巳","午","未","申","酉","戌","亥","子","丑","寅"],
        "未": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "申": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "酉": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"],
        "戌": ["卯","辰","巳","午","未","申","酉","戌","亥","子","丑","寅"],
        "亥": ["戌","亥","子","丑","寅","卯","辰","巳","午","未","申","酉"]
    }

    # 需要受時辰地支影響的凶星名稱
    EVIL_STARS_AFFECTED_BY_HOUR = ['文昌', '文曲', '地空', '地劫', '火星', '鈴星']

    # 年支對應紅鸞、天喜地支分布表
    HONG_LUAN_TIAN_XI_TABLE = {
        "子": {"紅鸞": "卯", "天喜": "酉"},
        "丑": {"紅鸞": "寅", "天喜": "申"},
        "寅": {"紅鸞": "丑", "天喜": "未"},
        "卯": {"紅鸞": "子", "天喜": "午"},
        "辰": {"紅鸞": "亥", "天喜": "巳"},
        "巳": {"紅鸞": "戌", "天喜": "辰"},
        "午": {"紅鸞": "酉", "天喜": "卯"},
        "未": {"紅鸞": "申", "天喜": "寅"},
        "申": {"紅鸞": "未", "天喜": "丑"},
        "酉": {"紅鸞": "午", "天喜": "子"},
        "戌": {"紅鸞": "巳", "天喜": "亥"},
        "亥": {"紅鸞": "辰", "天喜": "戌"}
    }
    
    # 年支對應天馬地支分布表
    TIAN_MA_TABLE = {
        # 申子辰年：天馬居寅宮
        "申": "寅", "子": "寅", "辰": "寅",
        # 亥卯未年：天馬居巳宮
        "亥": "巳", "卯": "巳", "未": "巳", 
        # 寅午戌年：天馬居申宮
        "寅": "申", "午": "申", "戌": "申",
        # 巳酉丑年：天馬居亥宮
        "巳": "亥", "酉": "亥", "丑": "亥"
    }
    
    # 大限計算相關常數
    # 天干分類
    ODD_STEMS = ["甲", "丙", "戊", "庚", "壬"]  # 奇數天干
    EVEN_STEMS = ["乙", "丁", "己", "辛", "癸"]  # 偶數天干
    
    # 五行局起運年齡
    BUREAU_START_AGE = {
        "水二局": 2,
        "木三局": 3, 
        "金四局": 4,
        "土五局": 5,
        "火六局": 6
    }

    # 小限起始位置對照表
    MINOR_LIMIT_START_POSITIONS = {
        # 寅午戌年支在辰位
        "寅": "辰", "午": "辰", "戌": "辰",
        # 申子辰年支在戌位  
        "申": "戌", "子": "戌", "辰": "戌",
        # 巳酉丑年支在未位
        "巳": "未", "酉": "未", "丑": "未",
        # 亥卯未年支在丑位
        "亥": "丑", "卯": "丑", "未": "丑"
    }

    def __init__(self):
        self.stars = {}

    def calculate_stars(self, birth_info: Dict, palaces: Dict):
        """
        計算所有星曜位置。

        Args:
            birth_info (Dict): 包含生辰資訊的字典
            palaces (Dict): 宮位資訊字典
        """
        # 1. 定命宮和身宮
        self._determine_life_and_body_palace(birth_info, palaces)
        
        # 2. 安放紫微星
        self._place_purple_star(birth_info, palaces)
        
        # 3. 安放其他主星（根據紫微星位置對照基本盤）
        self._place_main_stars(palaces)
        
        # 4. 安放生年天干吉凶星（祿存、擎羊、陀羅、天魁、天鉞）
        self._place_yearly_luck_stars(birth_info, palaces)
        
        # 5. 安放生月星曜（左輔、右弼）
        self._place_monthly_stars(birth_info, palaces)
        
        # 6. 安放生年地支天馬
        self._place_tian_ma_star(birth_info, palaces)
        
        # 7. 安放生時星曜（文昌、文曲、地空、地劫）
        self._place_hourly_stars(birth_info, palaces)
        
        # 8. 安放生年地支星曜（紅鸞、天喜）
        self._place_yearly_branch_stars(birth_info, palaces)
        
        # 9. 安放火星和鈴星（根據年支和時辰）
        self._place_fire_bell_stars(birth_info, palaces)
        
        # 10. 安放四化（祿權科忌）
        self._apply_four_transformations(birth_info, palaces)
    
    def _determine_five_elements_bureau(self, year_stem: str, ming_branch: str) -> str:
        """
        根據生年天干和命宮地支確定五行局
        
        Args:
            year_stem: 生年天干
            ming_branch: 命宮地支
            
        Returns:
            五行局名稱（如"水二局"）
        """
        return self.FIVE_ELEMENTS_CHART[year_stem][ming_branch]
    
    def _get_purple_star_position(self, five_elements_bureau: str, lunar_day: int) -> str:
        """
        根據五行局和農曆日期確定紫微星位置
        
        Args:
            five_elements_bureau: 五行局名稱
            lunar_day: 農曆日期(1-30)
            
        Returns:
            紫微星所在地支
        """
        # 將日期格式化為兩位數字符串
        day_str = f"{lunar_day:02d}"
        return self.PURPLE_STAR_POSITIONS[five_elements_bureau][day_str]
    
    def _place_purple_star(self, birth_info: Dict, palaces: Dict):
        """
        安放紫微星
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        # 獲取需要的資料
        year_stem = birth_info['year_stem']  # 生年天干
        ming_branch = birth_info['ming_branch']  # 命宮地支  
        lunar_day = birth_info['lunar_day']  # 農曆日期
        
        # 1. 確定五行局
        five_elements_bureau = self._determine_five_elements_bureau(year_stem, ming_branch)
        
        # 2. 確定紫微星位置
        purple_star_branch = self._get_purple_star_position(five_elements_bureau, lunar_day)
        
        # 3. 將紫微星安放到對應宮位
        # 找到對應的宮位名稱
        for palace_name, palace_info in palaces.items():
            if palace_info.branch == purple_star_branch:
                palace_info.stars.append("紫微")
                break

    def _place_main_stars(self, palaces: Dict):
        """
        根據紫微星位置對照基本盤，安放其他主星
        
        Args:
            palaces: 宮位資訊
        """
        # 1. 找到紫微星所在地支
        purple_star_branch = None
        for palace_name, palace_info in palaces.items():
            if "紫微" in palace_info.stars:
                purple_star_branch = palace_info.branch
                break
        
        if not purple_star_branch:
            return  # 如果找不到紫微星，直接返回
        
        # 2. 根據紫微星位置，對照基本盤安放其他主星
        basic_chart = self.BASIC_CHARTS[purple_star_branch]
        
        for branch, star_info in basic_chart.items():
            if star_info:  # 只排除空字串
                # 解析星曜資訊（可能包含多顆星和狀態）
                stars_with_states = self._parse_star_info(star_info)
                
                # 找到對應的宮位並添加星曜
                for palace_name, palace_info in palaces.items():
                    if palace_info.branch == branch:
                        for star_name, state in stars_with_states:
                            # 檢查該星曜是否已經存在於宮位中
                            existing_star_found = False
                            updated_stars = []
                            
                            for existing_star in palace_info.stars:
                                existing_star_name = existing_star.split("（")[0] if "（" in existing_star else existing_star
                                if existing_star_name == star_name:
                                    # 找到已存在的星曜，更新其狀態
                                    if state:
                                        updated_stars.append(f"{star_name}（{state}）")
                                    else:
                                        updated_stars.append(star_name)
                                    existing_star_found = True
                                else:
                                    updated_stars.append(existing_star)
                            
                            if existing_star_found:
                                # 更新宮位的星曜列表
                                palace_info.stars = updated_stars
                            else:
                                # 星曜不存在，添加新星曜
                                if state:
                                    palace_info.stars.append(f"{star_name}（{state}）")
                                else:
                                    palace_info.stars.append(star_name)
                        break

    def _parse_star_info(self, star_info: str) -> list:
        """
        解析星曜資訊字串，提取星曜名稱和狀態
        
        Args:
            star_info: 星曜資訊字串，如 "太陽（入廟）、天梁（入廟）"
            
        Returns:
            list: 包含 (星曜名稱, 狀態) 的元組列表
        """
        result = []
        
        # 按頓號分割多個星曜
        star_parts = star_info.split("、")
        
        for part in star_parts:
            part = part.strip()
            if "（" in part and "）" in part:
                # 有狀態的星曜，如 "太陽（入廟）"
                star_name = part.split("（")[0]
                state = part.split("（")[1].replace("）", "")
                result.append((star_name, state))
            else:
                # 沒有狀態的星曜
                result.append((part, None))
        
        return result

    def _place_yearly_luck_stars(self, birth_info: Dict, palaces: Dict):
        """
        根據生年天干安放吉凶星（祿存、擎羊、陀羅、天魁、天鉞）
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        year_stem = birth_info['year_stem']  # 生年天干
        
        # 獲取該年干對應的吉凶星位置
        if year_stem not in self.LUCK_TABLE:
            return  # 如果年干不在對照表中，直接返回
        
        luck_stars = self.LUCK_TABLE[year_stem]
        
        # 遍歷每個吉凶星，將其安放到對應宮位
        for star_name, target_branch in luck_stars.items():
            # 找到對應的宮位
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == target_branch:
                    palace_info.stars.append(star_name)
                    break

    def _place_monthly_stars(self, birth_info: Dict, palaces: Dict):
        """
        根據農曆生月安放左輔、右弼
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        lunar_month = birth_info['lunar_month']  # 農曆月份
        
        # 獲取該月份對應的左輔右弼位置
        if lunar_month not in self.MONTHLY_STARS_TABLE:
            return  # 如果月份不在對照表中，直接返回
        
        monthly_stars = self.MONTHLY_STARS_TABLE[lunar_month]
        
        # 遍歷左輔右弼，將其安放到對應宮位
        for star_name, target_branch in monthly_stars.items():
            # 找到對應的宮位
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == target_branch:
                    palace_info.stars.append(star_name)
                    break

    def _place_tian_ma_star(self, birth_info: Dict, palaces: Dict):
        """
        根據生年地支安放天馬
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        year_branch = birth_info['year_branch']  # 生年地支
        
        # 獲取該年支對應的天馬位置
        if year_branch not in self.TIAN_MA_TABLE:
            return  # 如果年支不在對照表中，直接返回
        
        tian_ma_branch = self.TIAN_MA_TABLE[year_branch]
        
        # 將天馬安放到對應宮位
        for palace_name, palace_info in palaces.items():
            if palace_info.branch == tian_ma_branch:
                palace_info.stars.append("天馬")
                break

    def _place_hourly_stars(self, birth_info: Dict, palaces: Dict):
        """
        根據生時地支安放星曜（文昌、文曲、地空、地劫）
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        birth_hour_branch = birth_info['lunar_hour_branch']  # 生時地支
        
        # 獲取該時辰對應的星曜位置
        if birth_hour_branch not in self.HOURLY_STARS_TABLE:
            return  # 如果時辰不在對照表中，直接返回
        
        hourly_stars = self.HOURLY_STARS_TABLE[birth_hour_branch]
        
        # 遍歷每個時辰星，將其安放到對應宮位
        for star_name, target_branch in hourly_stars.items():
            # 找到對應的宮位
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == target_branch:
                    palace_info.stars.append(star_name)
                    break

    def _place_yearly_branch_stars(self, birth_info: Dict, palaces: Dict):
        """
        根據生年地支安放星曜（紅鸞、天喜）
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        year_branch = birth_info['year_branch']  # 生年地支
        
        # 獲取該年支對應的星曜位置
        if year_branch not in self.HONG_LUAN_TIAN_XI_TABLE:
            return  # 如果年支不在對照表中，直接返回
        
        branch_stars = self.HONG_LUAN_TIAN_XI_TABLE[year_branch]
        
        # 遍歷每個星曜，將其安放到對應宮位
        for star_name, target_branch in branch_stars.items():
            # 找到對應的宮位
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == target_branch:
                    palace_info.stars.append(star_name)
                    break

    def _place_fire_bell_stars(self, birth_info: Dict, palaces: Dict):
        """
        根據生年地支和生時地支安放火星和鈴星
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        year_branch = birth_info['year_branch']  # 生年地支
        hour_branch = birth_info['lunar_hour_branch']  # 生時地支
        
        # 檢查年支是否在對照表中
        if year_branch not in self.FIRE_STAR_TABLE or year_branch not in self.BELL_STAR_TABLE:
            return
        
        # 獲取時辰索引（子=0, 丑=1, ..., 亥=11）
        hour_index = self.EARTHLY_BRANCHES.index(hour_branch)
        
        # 根據年支和時辰索引確定火星和鈴星位置
        fire_star_branch = self.FIRE_STAR_TABLE[year_branch][hour_index]
        bell_star_branch = self.BELL_STAR_TABLE[year_branch][hour_index]
        
        # 安放火星
        for palace_name, palace_info in palaces.items():
            if palace_info.branch == fire_star_branch:
                palace_info.stars.append("火星")
                break
        
        # 安放鈴星
        for palace_name, palace_info in palaces.items():
            if palace_info.branch == bell_star_branch:
                palace_info.stars.append("鈴星")
                break

    def recalculate_evil_stars_with_minute_branch(self, birth_info: Dict, palaces: Dict, minute_branch: str):
        """
        使用分鐘地支重新計算凶星位置（文昌、文曲、地空、地劫、火星、鈴星）
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
            minute_branch: 排盤時間的分鐘地支
        """
        # 先移除原有的凶星
        for palace_info in palaces.values():
            palace_info.stars = [star for star in palace_info.stars 
                               if star not in self.EVIL_STARS_AFFECTED_BY_HOUR]
        
        # 使用分鐘地支重新計算文昌、文曲、地空、地劫
        if minute_branch in self.HOURLY_STARS_TABLE:
            hourly_stars = self.HOURLY_STARS_TABLE[minute_branch]
            
            for star_name, target_branch in hourly_stars.items():
                for palace_name, palace_info in palaces.items():
                    if palace_info.branch == target_branch:
                        palace_info.stars.append(star_name)
                        break
        
        # 使用分鐘地支重新計算火星和鈴星
        year_branch = birth_info['year_branch']
        
        if year_branch in self.FIRE_STAR_TABLE and year_branch in self.BELL_STAR_TABLE:
            # 獲取分鐘地支的索引
            minute_index = self.EARTHLY_BRANCHES.index(minute_branch)
            
            # 根據年支和分鐘地支索引確定火星和鈴星位置
            fire_star_branch = self.FIRE_STAR_TABLE[year_branch][minute_index]
            bell_star_branch = self.BELL_STAR_TABLE[year_branch][minute_index]
            
            # 安放火星
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == fire_star_branch:
                    palace_info.stars.append("火星")
                    break
            
            # 安放鈴星
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == bell_star_branch:
                    palace_info.stars.append("鈴星")
                    break

    def _apply_four_transformations(self, birth_info: Dict, palaces: Dict):
        """
        安放四化（祿權科忌）
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
        """
        year_stem = birth_info['year_stem']  # 生年天干
        
        logger.info(f"開始應用四化，年干: {year_stem}")
        
        # 獲取該年干對應的四化星曜
        if year_stem not in self.FOUR_TRANSFORMATIONS:
            logger.error(f"年干 {year_stem} 不在四化對照表中")
            return  # 如果年干不在對照表中，直接返回
        
        transformations = self.FOUR_TRANSFORMATIONS[year_stem]
        logger.info(f"該年干的四化: {transformations}")
        
        # 遍歷四化（祿、權、科、忌）
        for transformation_type, star_name in transformations.items():
            logger.info(f"處理四化 {transformation_type} -> {star_name}")
            # 在所有宮位中找到該星曜
            star_found = False
            for palace_name, palace_info in palaces.items():
                logger.info(f"檢查宮位 {palace_name} 的星曜: {palace_info.stars}")
                # 檢查該宮位是否有此星曜
                updated_stars = []
                
                for star in palace_info.stars:
                    # 提取星曜名稱（去除狀態描述）
                    clean_star_name = star.split("（")[0] if "（" in star else star
                    logger.info(f"比對星曜: {clean_star_name} vs {star_name}")
                    
                    if clean_star_name == star_name:
                        # 找到了要四化的星曜，加上四化標記
                        if "（" in star:
                            # 已有狀態的星曜，如 "太陽（入廟）" -> "太陽（入廟）化祿"
                            base_star = star.replace("）", f"）化{transformation_type}")
                        else:
                            # 沒有狀態的星曜，如 "太陽" -> "太陽化祿"
                            base_star = f"{star}化{transformation_type}"
                        logger.info(f"找到星曜 {star}，添加四化標記: {base_star}")
                        updated_stars.append(base_star)
                        star_found = True
                    else:
                        # 保持原星曜不變
                        updated_stars.append(star)
                
                # 更新該宮位的星曜列表
                if star_found:
                    logger.info(f"更新宮位 {palace_name} 的星曜列表: {updated_stars}")
                    palace_info.stars = updated_stars
                    break
            
            if not star_found:
                logger.warning(f"未找到星曜 {star_name} 進行四化 {transformation_type}")
        
        logger.info("四化應用完成")

    def get_four_transformations_explanations(self, birth_info: Dict, palaces: Dict) -> Dict:
        """
        獲取四化解釋
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
            
        Returns:
            四化解釋資訊
        """
        year_stem = birth_info['year_stem']  # 生年天干
        
        # 獲取該年干對應的四化星曜
        if year_stem not in self.FOUR_TRANSFORMATIONS:
            return {}
        
        transformations = self.FOUR_TRANSFORMATIONS[year_stem]
        explanations = {}
        
        # 遍歷四化（祿、權、科、忌）
        for transformation_type, star_name in transformations.items():
            # 在所有宮位中找到該星曜
            for palace_name, palace_info in palaces.items():
                # 檢查該宮位是否有此星曜
                for star in palace_info.stars:
                    # 提取星曜名稱（去除狀態描述）
                    clean_star_name = star.split("（")[0] if "（" in star else star
                    
                    if clean_star_name == star_name:
                        # 找到了四化星曜，獲取解釋
                        if year_stem in four_transformations_explanations:
                            transformation_data = four_transformations_explanations[year_stem].get(transformation_type, {})
                            
                            # 找到對應宮位的解釋
                            palace_explanation = None
                            if "解釋" in transformation_data:
                                for explanation in transformation_data["解釋"]:
                                    # 匹配宮位名稱：程式中是"父母"，解釋資料中是"父母宮"
                                    palace_name_with_suffix = palace_info.name + "宮" if not palace_info.name.endswith("宮") else palace_info.name
                                    
                                    # 處理宮位名稱的別名對應
                                    explanation_palace_name = explanation["宮位"]
                                    if explanation_palace_name == palace_name_with_suffix:
                                        palace_explanation = explanation
                                        break
                                    # 處理「交友宮」和「僕役宮」的對應
                                    elif (palace_name_with_suffix == "交友宮" and explanation_palace_name == "僕役宮") or \
                                         (palace_name_with_suffix == "僕役宮" and explanation_palace_name == "交友宮"):
                                        palace_explanation = explanation
                                        break
                            
                            if palace_explanation:
                                explanations[f"{star_name}化{transformation_type}"] = {
                                    "星曜": star_name,
                                    "四化": transformation_type,
                                    "宮位": palace_info.name,
                                    "主星": transformation_data.get("主星", ""),
                                    "現象": palace_explanation.get("現象", ""),
                                    "心理傾向": palace_explanation.get("心理傾向", ""),
                                    "可能事件": palace_explanation.get("可能事件", ""),
                                    "提示": palace_explanation.get("提示", ""),
                                    "來意不明建議": palace_explanation.get("來意不明建議", "")
                                }
                        break
        
        return explanations

    def get_four_transformations_explanations_by_stem(self, custom_stem: str, palaces: Dict) -> Dict:
        """
        根據自定義天干獲取四化解釋
        
        Args:
            custom_stem: 自定義天干
            palaces: 宮位資訊
            
        Returns:
            四化解釋資訊
        """
        # 獲取該天干對應的四化星曜
        if custom_stem not in self.FOUR_TRANSFORMATIONS:
            return {}
        
        transformations = self.FOUR_TRANSFORMATIONS[custom_stem]
        explanations = {}
        
        # 遍歷四化（祿、權、科、忌）
        for transformation_type, star_name in transformations.items():
            # 在所有宮位中找到該星曜
            for palace_name, palace_info in palaces.items():
                # 檢查該宮位是否有此星曜
                for star in palace_info.stars:
                    # 提取星曜名稱（去除狀態描述）
                    clean_star_name = star.split("（")[0] if "（" in star else star
                    
                    if clean_star_name == star_name:
                        # 找到了四化星曜，獲取解釋
                        if custom_stem in four_transformations_explanations:
                            transformation_data = four_transformations_explanations[custom_stem].get(transformation_type, {})
                            
                            # 找到對應宮位的解釋
                            palace_explanation = None
                            if "解釋" in transformation_data:
                                for explanation in transformation_data["解釋"]:
                                    # 匹配宮位名稱：程式中是"父母"，解釋資料中是"父母宮"
                                    palace_name_with_suffix = palace_info.name + "宮" if not palace_info.name.endswith("宮") else palace_info.name
                                    
                                    # 處理宮位名稱的別名對應
                                    explanation_palace_name = explanation["宮位"]
                                    if explanation_palace_name == palace_name_with_suffix:
                                        palace_explanation = explanation
                                        break
                                    # 處理「交友宮」和「僕役宮」的對應
                                    elif (palace_name_with_suffix == "交友宮" and explanation_palace_name == "僕役宮") or \
                                         (palace_name_with_suffix == "僕役宮" and explanation_palace_name == "交友宮"):
                                        palace_explanation = explanation
                                        break
                            
                            if palace_explanation:
                                explanations[f"{star_name}化{transformation_type}"] = {
                                    "星曜": star_name,
                                    "四化": transformation_type,
                                    "宮位": palace_info.name,
                                    "主星": transformation_data.get("主星", ""),
                                    "現象": palace_explanation.get("現象", ""),
                                    "心理傾向": palace_explanation.get("心理傾向", ""),
                                    "可能事件": palace_explanation.get("可能事件", ""),
                                    "提示": palace_explanation.get("提示", ""),
                                    "來意不明建議": palace_explanation.get("來意不明建議", ""),
                                    "自定義天干": custom_stem
                                }
                        break
        
        return explanations

    def _determine_life_and_body_palace(self, birth_info: Dict, palaces: Dict):
        """
        根據生日的月和時辰來確定命宮和身宮的位置。
        身宮計算：根據生時地支直接對應到特定宮位
        """
        lunar_hour_branch = birth_info['lunar_hour_branch']

        # 根據時辰直接查詢身宮所在的宮位名稱
        body_palace_name = self.BODY_PALACE_MAPPING[lunar_hour_branch]
        
        # 標記身宮
        for palace_name, palace_info in palaces.items():
            if palace_info.name == body_palace_name:
                palace_info.body_palace = True
                break

    def calculate_major_limits(self, birth_info: Dict, palaces: Dict, current_age: int = None):
        """
        計算大限
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
            current_age: 當前年齡（可選，用於確定當前大限）
        
        Returns:
            Dict: 大限資訊
        """
        # 1. 確定五行局
        year_stem = birth_info['year_stem']
        ming_branch = birth_info['ming_branch']
        five_elements_bureau = self._determine_five_elements_bureau(year_stem, ming_branch)
        
        # 2. 確定起運年齡
        start_age = self.BUREAU_START_AGE[five_elements_bureau]
        
        # 3. 確定大限順序（順行或逆行）
        gender = birth_info.get('gender', 'M')  # 默認為男性
        is_forward = self._determine_major_limit_direction(year_stem, gender)
        
        # 4. 計算所有大限
        major_limits = self._calculate_all_major_limits(palaces, start_age, is_forward)
        
        # 5. 如果提供當前年齡，確定當前大限
        current_major_limit = None
        if current_age is not None:
            current_major_limit = self._find_current_major_limit(major_limits, current_age)
        
        return {
            "五行局": five_elements_bureau,
            "起運年齡": start_age,
            "大限順序": "順行" if is_forward else "逆行",
            "所有大限": major_limits,
            "當前大限": current_major_limit
        }
    
    def _determine_major_limit_direction(self, year_stem: str, gender: str) -> bool:
        """
        確定大限順序方向
        
        Args:
            year_stem: 生年天干
            gender: 性別 ('M'=男, 'F'=女)
            
        Returns:
            bool: True=順行, False=逆行
        """
        is_odd_stem = year_stem in self.ODD_STEMS
        is_male = gender == 'M'
        
        # 陽男(天干奇數) + 陰女(天干偶數) = 順行
        # 陰男(天干偶數) + 陽女(天干奇數) = 逆行
        if (is_male and is_odd_stem) or (not is_male and not is_odd_stem):
            return True  # 順行
        else:
            return False  # 逆行
    
    def _calculate_all_major_limits(self, palaces: Dict, start_age: int, is_forward: bool) -> List[Dict]:
        """
        計算所有大限
        
        Args:
            palaces: 宮位資訊
            start_age: 起運年齡
            is_forward: 是否順行
            
        Returns:
            List[Dict]: 所有大限列表
        """
        major_limits = []
        palace_names = list(palaces.keys())
        
        # 從命宮開始
        start_index = 0  # 命宮索引
        
        for i in range(12):  # 12個大限
            if is_forward:
                # 順行：命宮 -> 兄弟宮 -> 夫妻宮 -> ...
                palace_index = (start_index + i) % 12
            else:
                # 逆行：命宮 -> 父母宮 -> 福德宮 -> ...
                palace_index = (start_index - i) % 12
            
            palace_name = palace_names[palace_index]
            palace_info = palaces[palace_name]
            
            # 計算年齡範圍
            age_start = start_age + i * 10
            age_end = age_start + 9
            
            major_limit = {
                "序號": i + 1,
                "宮位名稱": palace_name,
                "地支": palace_info.branch,
                "天干": palace_info.stem,
                "五行": palace_info.element,
                "年齡範圍": f"{age_start}~{age_end}歲",
                "年齡開始": age_start,
                "年齡結束": age_end,
                "星曜": palace_info.stars.copy()  # 複製星曜列表
            }
            
            major_limits.append(major_limit)
        
        return major_limits
    
    def _find_current_major_limit(self, major_limits: List[Dict], current_age: int) -> Dict:
        """
        根據當前年齡找到對應的大限
        
        Args:
            major_limits: 所有大限列表
            current_age: 當前年齡
            
        Returns:
            Dict: 當前大限資訊，如果未找到則返回None
        """
        for major_limit in major_limits:
            if major_limit["年齡開始"] <= current_age <= major_limit["年齡結束"]:
                return major_limit
        
        return None
    
    def calculate_minor_limits(self, birth_info: Dict, palaces: Dict, target_age: int = None):
        """
        計算小限
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
            target_age: 目標年齡（可選，用於確定特定年齡的小限）
        
        Returns:
            Dict: 小限資訊
        """
        # 1. 確定小限起始位置
        year_branch = birth_info['year_branch']
        start_branch = self.MINOR_LIMIT_START_POSITIONS[year_branch]
        
        # 2. 確定小限順序（男順女逆）
        gender = birth_info.get('gender', 'M')
        is_forward = gender == 'M'  # 男命順行，女命逆行
        
        # 3. 計算所有小限或特定年齡的小限
        if target_age is not None:
            # 計算特定年齡的小限
            minor_limit = self._calculate_specific_minor_limit(palaces, start_branch, is_forward, target_age)
            return {
                "年支": year_branch,
                "起始位置": start_branch,
                "小限順序": "順行" if is_forward else "逆行",
                "目標年齡": target_age,
                "小限資訊": minor_limit
            }
        else:
            # 計算前12年的小限（作為示例）
            minor_limits = self._calculate_multiple_minor_limits(palaces, start_branch, is_forward, 12)
            return {
                "年支": year_branch,
                "起始位置": start_branch,
                "小限順序": "順行" if is_forward else "逆行",
                "小限列表": minor_limits
            }
    
    def _calculate_specific_minor_limit(self, palaces: Dict, start_branch: str, is_forward: bool, age: int) -> Dict:
        """
        計算特定年齡的小限
        
        Args:
            palaces: 宮位資訊
            start_branch: 起始地支
            is_forward: 是否順行
            age: 年齡
            
        Returns:
            Dict: 該年齡的小限資訊
        """
        # 計算該年齡對應的地支位置
        start_index = self.EARTHLY_BRANCHES.index(start_branch)
        
        if is_forward:
            # 順行：1歲在起始位置，2歲在下一位置...
            target_index = (start_index + age - 1) % 12
        else:
            # 逆行：1歲在起始位置，2歲在上一位置...
            target_index = (start_index - age + 1) % 12
        
        target_branch = self.EARTHLY_BRANCHES[target_index]
        
        # 找到對應的宮位
        target_palace = None
        for palace_name, palace_info in palaces.items():
            if palace_info.branch == target_branch:
                target_palace = {
                    "年齡": age,
                    "地支": target_branch,
                    "宮位名稱": palace_name,
                    "天干": palace_info.stem,
                    "五行": palace_info.element,
                    "星曜": palace_info.stars.copy()
                }
                break
        
        return target_palace
    
    def _calculate_multiple_minor_limits(self, palaces: Dict, start_branch: str, is_forward: bool, years: int) -> List[Dict]:
        """
        計算多個年齡的小限
        
        Args:
            palaces: 宮位資訊
            start_branch: 起始地支
            is_forward: 是否順行
            years: 要計算的年數
            
        Returns:
            List[Dict]: 小限列表
        """
        minor_limits = []
        
        for age in range(1, years + 1):
            minor_limit = self._calculate_specific_minor_limit(palaces, start_branch, is_forward, age)
            if minor_limit:
                minor_limits.append(minor_limit)
        
        return minor_limits
    
    def calculate_annual_fortune(self, birth_info: Dict, palaces: Dict, target_year: int = None):
        """
        計算流年
        
        Args:
            birth_info: 生辰資訊
            palaces: 宮位資訊
            target_year: 目標年份（西元年，如2024）
        
        Returns:
            Dict: 流年資訊
        """
        # 如果沒有指定目標年份，使用當前年份
        if target_year is None:
            from datetime import datetime
            target_year = datetime.now().year
        
        # 1. 確定目標年份的地支
        target_year_branch = self._get_year_branch(target_year)
        
        # 2. 確定本命命宮地支
        ming_branch = birth_info['ming_branch']
        
        # 3. 計算流年命宮位置
        annual_ming_branch = self._calculate_annual_ming_palace(ming_branch, target_year_branch)
        
        # 4. 計算流年十二宮
        annual_palaces = self._calculate_annual_palaces(palaces, annual_ming_branch)
        
        return {
            "目標年份": target_year,
            "年份地支": target_year_branch,
            "本命命宮": ming_branch,
            "流年命宮": annual_ming_branch,
            "流年宮位": annual_palaces
        }
    
    def _get_year_branch(self, year: int) -> str:
        """
        根據西元年份計算地支
        
        Args:
            year: 西元年份
            
        Returns:
            str: 地支
        """
        # 地支循環：子(1900, 1912, 1924...) 丑(1901, 1913, 1925...) ...
        # 1900年是庚子年，所以1900年對應子
        branch_index = (year - 1900) % 12
        return self.EARTHLY_BRANCHES[branch_index]
    
    def _calculate_annual_ming_palace(self, ming_branch: str, target_year_branch: str) -> str:
        """
        計算流年命宮位置
        
        Args:
            ming_branch: 本命命宮地支（這個參數保留但不使用，為了保持接口一致性）
            target_year_branch: 目標年份地支
            
        Returns:
            str: 流年命宮地支
        """
        # 流年命宮直接對應年份地支
        # 辰年流年命宮在辰宮，巳年流年命宮在巳宮
        return target_year_branch
    
    def _calculate_annual_palaces(self, palaces: Dict, annual_ming_branch: str) -> Dict:
        """
        計算流年十二宮
        
        Args:
            palaces: 本命宮位資訊
            annual_ming_branch: 流年命宮地支
            
        Returns:
            Dict: 流年宮位對應關係
        """
        # 流年十二宮名稱（固定順序）
        annual_palace_names = [
            "流年命宮", "流年父母", "流年福德", "流年田宅", 
            "流年官祿", "流年交友", "流年遷移", "流年疾厄", 
            "流年財帛", "流年子女", "流年夫妻", "流年兄弟"
        ]
        
        # 從流年命宮開始，按地支順序排列
        annual_ming_index = self.EARTHLY_BRANCHES.index(annual_ming_branch)
        annual_palaces = {}
        
        for i, annual_name in enumerate(annual_palace_names):
            # 計算該流年宮位對應的地支
            branch_index = (annual_ming_index + i) % 12
            branch = self.EARTHLY_BRANCHES[branch_index]
            
            # 找到本命盤中對應該地支的宮位
            corresponding_palace = None
            for palace_name, palace_info in palaces.items():
                if palace_info.branch == branch:
                    corresponding_palace = {
                        "本命宮位": palace_name,
                        "地支": branch,
                        "天干": palace_info.stem,
                        "五行": palace_info.element,
                        "星曜": palace_info.stars.copy()
                    }
                    break
            
            annual_palaces[annual_name] = corresponding_palace
        
        return annual_palaces
    
    def calculate_monthly_fortune(self, birth_info: Dict, palaces: Dict, annual_fortune: Dict, target_month: int = None):
        """
        計算流月
        
        Args:
            birth_info: 生辰資訊
            palaces: 本命宮位資訊
            annual_fortune: 流年資訊
            target_month: 目標月份（農曆月，1-12）
        
        Returns:
            Dict: 流月資訊
        """
        # 如果沒有指定目標月份，使用當前農曆月份
        if target_month is None:
            from datetime import datetime
            # 這裡簡化處理，實際應該轉換為農曆月份
            target_month = datetime.now().month
        
        # 1. 找到本命盤寅位對應的宮位名稱
        yin_palace_name = self._find_palace_by_branch(palaces, "寅")
        
        # 2. 在流年盤中找到該宮位的位置（地支），這就是流月一月的起始位置
        monthly_start_branch = self._find_annual_palace_branch(annual_fortune, yin_palace_name)
        
        # 3. 計算流月十二宮
        monthly_palaces = self._calculate_monthly_palaces(annual_fortune, monthly_start_branch, target_month)
        
        return {
            "目標月份": target_month,
            "寅位宮位": yin_palace_name,
            "流月起始位置": monthly_start_branch,
            "流月宮位": monthly_palaces
        }
    
    def _find_palace_by_branch(self, palaces: Dict, target_branch: str) -> str:
        """
        根據地支找到對應的宮位名稱
        
        Args:
            palaces: 宮位資訊
            target_branch: 目標地支
            
        Returns:
            str: 宮位名稱
        """
        for palace_name, palace_info in palaces.items():
            if palace_info.branch == target_branch:
                return palace_name
        return None
    
    def _find_annual_palace_branch(self, annual_fortune: Dict, target_palace_name: str) -> str:
        """
        在流年盤中找到指定宮位名稱對應的地支
        
        Args:
            annual_fortune: 流年資訊
            target_palace_name: 目標宮位名稱（如"福德宮"）
            
        Returns:
            str: 對應的地支
        """
        annual_palaces = annual_fortune.get("流年宮位", {})
        
        # 構建流年宮位名稱，例如"福德宮" -> "流年福德"
        if target_palace_name.endswith("宮"):
            target_palace_name = target_palace_name[:-1]  # 移除"宮"字
        annual_palace_key = f"流年{target_palace_name}"
        
        palace_info = annual_palaces.get(annual_palace_key)
        if palace_info:
            return palace_info.get("地支")
        
        return None
    
    def _calculate_monthly_palaces(self, annual_fortune: Dict, monthly_start_branch: str, target_month: int) -> Dict:
        """
        計算流月十二宮
        
        Args:
            annual_fortune: 流年資訊
            monthly_start_branch: 流月起始地支（一月位置）
            target_month: 目標月份
            
        Returns:
            Dict: 流月宮位對應關係
        """
        if not monthly_start_branch:
            return {}
        
        # 流月十二宮名稱（固定順序）
        monthly_palace_names = [
            "流月命宮", "流月父母", "流月福德", "流月田宅", 
            "流月官祿", "流月交友", "流月遷移", "流月疾厄", 
            "流月財帛", "流月子女", "流月夫妻", "流月兄弟"
        ]
        
        # 計算目標月份的流月命宮位置
        # 一月在起始位置，二月在下一位置，以此類推
        start_index = self.EARTHLY_BRANCHES.index(monthly_start_branch)
        target_month_index = (start_index + target_month - 1) % 12
        target_month_branch = self.EARTHLY_BRANCHES[target_month_index]
        
        # 從目標月份的流月命宮開始，按地支順序排列流月十二宮
        monthly_palaces = {}
        annual_palaces = annual_fortune.get("流年宮位", {})
        
        for i, monthly_name in enumerate(monthly_palace_names):
            # 計算該流月宮位對應的地支
            branch_index = (target_month_index + i) % 12
            branch = self.EARTHLY_BRANCHES[branch_index]
            
            # 找到流年盤中對應該地支的宮位資訊
            corresponding_palace = None
            for annual_palace_name, annual_palace_info in annual_palaces.items():
                if annual_palace_info and annual_palace_info.get("地支") == branch:
                    corresponding_palace = {
                        "流年宮位": annual_palace_name,
                        "本命宮位": annual_palace_info.get("本命宮位"),
                        "地支": branch,
                        "天干": annual_palace_info.get("天干"),
                        "五行": annual_palace_info.get("五行"),
                        "星曜": annual_palace_info.get("星曜", []).copy()
                    }
                    break
            
            monthly_palaces[monthly_name] = corresponding_palace
        
        return monthly_palaces
    
    def calculate_daily_fortune(self, birth_info: Dict, palaces: Dict, annual_fortune: Dict, monthly_fortune: Dict, target_day: int = None):
        """
        計算流日
        
        Args:
            birth_info: 生辰資訊
            palaces: 本命宮位資訊
            annual_fortune: 流年資訊
            monthly_fortune: 流月資訊
            target_day: 目標日期（農曆日，1-30）
        
        Returns:
            Dict: 流日資訊
        """
        # 如果沒有指定目標日期，使用當前農曆日期
        if target_day is None:
            from datetime import datetime
            # 這裡簡化處理，實際應該轉換為農曆日期
            target_day = datetime.now().day
        
        # 1. 找到流月命宮的位置
        monthly_ming_branch = self._find_monthly_ming_palace_branch(monthly_fortune)
        
        # 2. 計算流日一日的起始位置（流月命宮的下一個宮位）
        daily_start_branch = self._get_next_branch(monthly_ming_branch)
        
        # 3. 計算流日十二宮
        daily_palaces = self._calculate_daily_palaces(annual_fortune, monthly_fortune, daily_start_branch, target_day)
        
        return {
            "目標日期": target_day,
            "流月命宮位置": monthly_ming_branch,
            "流日起始位置": daily_start_branch,
            "流日宮位": daily_palaces
        }
    
    def _find_monthly_ming_palace_branch(self, monthly_fortune: Dict) -> str:
        """
        找到流月命宮的地支位置
        
        Args:
            monthly_fortune: 流月資訊
            
        Returns:
            str: 流月命宮的地支
        """
        monthly_palaces = monthly_fortune.get("流月宮位", {})
        ming_palace_info = monthly_palaces.get("流月命宮")
        
        if ming_palace_info:
            return ming_palace_info.get("地支")
        
        return None
    
    def _get_next_branch(self, current_branch: str) -> str:
        """
        獲取下一個地支
        
        Args:
            current_branch: 當前地支
            
        Returns:
            str: 下一個地支
        """
        if not current_branch:
            return None
            
        current_index = self.EARTHLY_BRANCHES.index(current_branch)
        next_index = (current_index + 1) % 12
        return self.EARTHLY_BRANCHES[next_index]
    
    def _calculate_daily_palaces(self, annual_fortune: Dict, monthly_fortune: Dict, daily_start_branch: str, target_day: int) -> Dict:
        """
        計算流日十二宮
        
        Args:
            annual_fortune: 流年資訊
            monthly_fortune: 流月資訊
            daily_start_branch: 流日起始地支（一日位置）
            target_day: 目標日期
            
        Returns:
            Dict: 流日宮位對應關係
        """
        if not daily_start_branch:
            return {}
        
        # 流日十二宮名稱（固定順序）
        daily_palace_names = [
            "流日命宮", "流日父母", "流日福德", "流日田宅", 
            "流日官祿", "流日交友", "流日遷移", "流日疾厄", 
            "流日財帛", "流日子女", "流日夫妻", "流日兄弟"
        ]
        
        # 計算目標日期的流日命宮位置
        # 一日在起始位置，二日在下一位置，以此類推
        start_index = self.EARTHLY_BRANCHES.index(daily_start_branch)
        target_day_index = (start_index + target_day - 1) % 12
        target_day_branch = self.EARTHLY_BRANCHES[target_day_index]
        
        # 從目標日期的流日命宮開始，按地支順序排列流日十二宮
        daily_palaces = {}
        annual_palaces = annual_fortune.get("流年宮位", {})
        monthly_palaces = monthly_fortune.get("流月宮位", {})
        
        for i, daily_name in enumerate(daily_palace_names):
            # 計算該流日宮位對應的地支
            branch_index = (target_day_index + i) % 12
            branch = self.EARTHLY_BRANCHES[branch_index]
            
            # 找到對應的宮位資訊（優先從流月盤中找，再從流年盤中找）
            corresponding_palace = None
            
            # 先從流月盤中找
            for monthly_palace_name, monthly_palace_info in monthly_palaces.items():
                if monthly_palace_info and monthly_palace_info.get("地支") == branch:
                    corresponding_palace = {
                        "流月宮位": monthly_palace_name,
                        "流年宮位": monthly_palace_info.get("流年宮位"),
                        "本命宮位": monthly_palace_info.get("本命宮位"),
                        "地支": branch,
                        "天干": monthly_palace_info.get("天干"),
                        "五行": monthly_palace_info.get("五行"),
                        "星曜": monthly_palace_info.get("星曜", []).copy()
                    }
                    break
            
            # 如果流月盤中沒找到，從流年盤中找
            if not corresponding_palace:
                for annual_palace_name, annual_palace_info in annual_palaces.items():
                    if annual_palace_info and annual_palace_info.get("地支") == branch:
                        corresponding_palace = {
                            "流月宮位": None,
                            "流年宮位": annual_palace_name,
                            "本命宮位": annual_palace_info.get("本命宮位"),
                            "地支": branch,
                            "天干": annual_palace_info.get("天干"),
                            "五行": annual_palace_info.get("五行"),
                            "星曜": annual_palace_info.get("星曜", []).copy()
                        }
                        break
            
            daily_palaces[daily_name] = corresponding_palace
        
        return daily_palaces

    def get_explanation_for_palace(self, star_name: str, transformation_type: str, palace_name: str, birth_info: Dict) -> Dict:
        """
        獲取指定宮位的四化解釋
        
        Args:
            star_name: 星曜名稱
            transformation_type: 四化類型（祿/權/科/忌）
            palace_name: 宮位名稱
            birth_info: 生辰資訊
            
        Returns:
            四化解釋資訊
        """
        year_stem = birth_info.get('year_stem')
        
        if not year_stem or year_stem not in four_transformations_explanations:
            return {}
        
        transformation_data = four_transformations_explanations[year_stem].get(transformation_type, {})
        
        if "解釋" not in transformation_data:
            return {}
        
        # 找到對應宮位的解釋
        palace_explanation = None
        
        # 確保宮位名稱格式一致（添加"宮"字後綴）
        target_palace_name = palace_name + "宮" if not palace_name.endswith("宮") else palace_name
        
        for explanation in transformation_data["解釋"]:
            explanation_palace_name = explanation["宮位"]
            
            if explanation_palace_name == target_palace_name:
                palace_explanation = explanation
                break
            # 處理「交友宮」和「僕役宮」的對應
            elif (target_palace_name == "交友宮" and explanation_palace_name == "僕役宮") or \
                 (target_palace_name == "僕役宮" and explanation_palace_name == "交友宮"):
                palace_explanation = explanation
                break
        
        if palace_explanation:
            return {
                "星曜": star_name,
                "四化": transformation_type,
                "宮位": palace_name,
                "主星": transformation_data.get("主星", ""),
                "現象": palace_explanation.get("現象", ""),
                "心理傾向": palace_explanation.get("心理傾向", ""),
                "可能事件": palace_explanation.get("可能事件", ""),
                "提示": palace_explanation.get("提示", ""),
                "來意不明建議": palace_explanation.get("來意不明建議", "")
            }
        
        return {}