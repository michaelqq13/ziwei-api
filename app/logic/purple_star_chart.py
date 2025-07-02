import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import traceback
from sqlalchemy.orm import Session

# 項目模組導入
from app.utils.chinese_calendar import ChineseCalendar
from app.models.birth_info import BirthInfo
from app.models.calendar_data import CalendarData
from app.logic.star_calculator import StarCalculator
from app.data.heavenly_stems.four_transformations import four_transformations_explanations
from app.db.repository import CalendarRepository

logger = logging.getLogger(__name__)

@dataclass
class Palace:
    name: str  # 宮位名稱
    stars: List[str]  # 宮內星曜
    element: str  # 五行屬性
    stem: str  # 天干
    branch: str  # 地支
    body_palace: bool = False  # 是否為身宮

class PurpleStarChart:
    def __init__(self, year: int = None, month: int = None, day: int = None, hour: int = None, minute: int = None, gender: str = None, birth_info: BirthInfo = None, db: Session = None):
        """
        初始化紫微斗數命盤
        
        Args:
            year: 年份（可選，如果提供 birth_info 則不需要）
            month: 月份（可選，如果提供 birth_info 則不需要）
            day: 日期（可選，如果提供 birth_info 則不需要）
            hour: 小時（可選，如果提供 birth_info 則不需要）
            minute: 分鐘（可選，如果提供 birth_info 則不需要）
            gender: 性別（可選，如果提供 birth_info 則不需要）
            birth_info: BirthInfo 對象（可選，如果提供年月日時分和性別則不需要）
            db: 數據庫會話（可選，如果沒有提供則使用簡化模式）
        """
        if birth_info:
            self.birth_info = birth_info
        else:
            self.birth_info = BirthInfo(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                gender=gender,
                longitude=121.5654,  # 預設台北經度
                latitude=25.0330     # 預設台北緯度
            )
        
        # 數據庫會話現在是可選的
        self.db = db
        self.calendar_repo = CalendarRepository(db) if db else None
        self.star_calculator = StarCalculator()
        self.palaces: Dict[str, Palace] = {}
        self.calendar_data: Optional[CalendarData] = None
        self.palace_order: List[str] = []
        self.simplified_mode = db is None  # 標記是否為簡化模式
        
        if self.simplified_mode:
            logger.warning("PurpleStarChart 以簡化模式初始化（無數據庫）")
        
        # 初始化命盤
        self.initialize()
        
        # 計算星曜位置
        self.calculate_stars()
        
    def initialize(self):
        """初始化命盤"""
        logger.info("開始初始化命盤")
        
        if self.simplified_mode:
            # 簡化模式：使用內置農曆轉換（專門用於占卜功能）
            logger.info("使用簡化模式初始化（無數據庫）")
            self._initialize_simplified_mode()
        else:
            # 正常模式：使用數據庫中的準確農曆資料
            logger.info("使用正常模式初始化（有數據庫）")
            self._initialize_normal_mode()
        
        # 設置宮位和星曜的初始空字典
        self.palaces = {}
        self.stars = {}
        self.palace_order = []
        
        # 2. 計算命宮位置
        self._calculate_ming_palace()
        
        # 3. 初始化十二宮位
        self._initialize_palaces()
        
        logger.info("命盤初始化完成")
    
    def _initialize_normal_mode(self):
        """正常模式初始化：使用數據庫中的準確農曆資料"""
        # 1. 獲取農曆資料
        self.calendar_data = self.calendar_repo.get_calendar_data(self.birth_info)
        if not self.calendar_data:
            logger.error("無法獲取對應的農曆數據")
            raise ValueError("無法獲取對應的農曆數據")
            
        logger.info(f"獲取到農曆數據: {self.calendar_data.__dict__}")
            
        # 在此計算並添加分鐘干支
        # 使用日干和時辰來計算時干
        day_stem = self.calendar_data.day_gan_zhi[0]  # 取日干
        hour_stem = ChineseCalendar.get_hour_stem(self.birth_info.hour, day_stem)  # 基於日干計算時干
        minute_branch = ChineseCalendar.get_minute_branch(self.birth_info.hour, self.birth_info.minute)
        self.calendar_data.minute_gan_zhi = f"{hour_stem}{minute_branch}"
        
        logger.info(f"計算分鐘干支: {self.calendar_data.minute_gan_zhi}")
    
    def _initialize_simplified_mode(self):
        """簡化模式初始化：使用內置農曆轉換（僅用於占卜）"""
        logger.warning("使用簡化模式，農曆轉換可能不如數據庫版本準確")
        
        # 創建一個模擬的 calendar_data 對象
        from app.models.calendar import CalendarData
        
        # 使用內置的簡化農曆轉換
        try:
            # 這裡使用簡化的農曆計算（可以根據需要實現更準確的演算法）
            # 注意：這只是用於無數據庫時的緊急措施
            
            # 使用農曆轉換算法（簡化版）
            lunar_data = self._calculate_lunar_data_simplified(
                self.birth_info.year, 
                self.birth_info.month, 
                self.birth_info.day
            )
            
            # 計算干支
            year_ganzhi = ChineseCalendar.get_year_ganzhi(self.birth_info.year)
            month_ganzhi = ChineseCalendar.get_month_ganzhi(self.birth_info.year, self.birth_info.month)
            day_ganzhi = ChineseCalendar.get_day_ganzhi(self.birth_info.year, self.birth_info.month, self.birth_info.day)
            hour_ganzhi = ChineseCalendar.get_hour_ganzhi(self.birth_info.hour, day_ganzhi[0])
            
            # 創建模擬的 calendar_data
            self.calendar_data = CalendarData()
            self.calendar_data.gregorian_year = self.birth_info.year
            self.calendar_data.gregorian_month = self.birth_info.month
            self.calendar_data.gregorian_day = self.birth_info.day
            self.calendar_data.gregorian_hour = self.birth_info.hour
            
            self.calendar_data.lunar_year_in_chinese = lunar_data['lunar_year']
            self.calendar_data.lunar_month_in_chinese = lunar_data['lunar_month']
            self.calendar_data.lunar_day_in_chinese = lunar_data['lunar_day']
            self.calendar_data.is_leap_month_in_chinese = lunar_data['is_leap']
            
            self.calendar_data.year_gan_zhi = year_ganzhi
            self.calendar_data.month_gan_zhi = month_ganzhi
            self.calendar_data.day_gan_zhi = day_ganzhi
            self.calendar_data.hour_gan_zhi = hour_ganzhi
            
            # 計算分鐘干支
            day_stem = self.calendar_data.day_gan_zhi[0]
            hour_stem = ChineseCalendar.get_hour_stem(self.birth_info.hour, day_stem)
            minute_branch = ChineseCalendar.get_minute_branch(self.birth_info.hour, self.birth_info.minute)
            self.calendar_data.minute_gan_zhi = f"{hour_stem}{minute_branch}"
            
            logger.info(f"簡化模式計算結果：農曆 {lunar_data['lunar_year']}年{lunar_data['lunar_month']}月{lunar_data['lunar_day']}日")
            logger.info(f"年干支：{year_ganzhi}, 月干支：{month_ganzhi}, 日干支：{day_ganzhi}, 時干支：{hour_ganzhi}")
            logger.info(f"分鐘干支：{self.calendar_data.minute_gan_zhi}")
            
        except Exception as e:
            logger.error(f"簡化模式初始化失敗：{e}")
            raise ValueError(f"簡化模式初始化失敗：{e}")
    
    def _calculate_lunar_data_simplified(self, year: int, month: int, day: int) -> Dict[str, str]:
        """
        簡化的農曆計算（僅用於無數據庫時的緊急措施）
        注意：這個實現可能不夠準確，主要用於系統緊急運行
        """
        # 這是一個極其簡化的實現，實際上農曆轉換非常複雜
        # 理想情況下，你應該啟動數據庫來獲取準確的農曆資料
        
        # 暫時使用一個非常基礎的近似值
        # 注意：這不是準確的農曆轉換，只是讓系統能運行
        
        # 農曆年份（簡化）
        lunar_year_cycle = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
                           "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
                           "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
                           "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
                           "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
                           "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"]
        
        lunar_year = lunar_year_cycle[(year - 1984) % 60]  # 1984年為甲子年
        
        # 農曆月份（極其簡化的近似）
        lunar_months = ["正月", "二月", "三月", "四月", "五月", "六月", 
                       "七月", "八月", "九月", "十月", "十一月", "十二月"]
        
        # 大致的農曆月份對應（這只是近似值！）
        approx_lunar_month = ((month - 2) % 12)  # 大致偏移
        if approx_lunar_month < 0:
            approx_lunar_month += 12
        lunar_month = lunar_months[approx_lunar_month]
        
        # 農曆日期（簡化）
        chinese_numbers = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                          "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                          "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
        
        # 大致對應農曆日（這只是近似值！）
        approx_lunar_day = (day - 1 + 3) % 30  # 大致偏移
        lunar_day = chinese_numbers[approx_lunar_day]
        
        return {
            'lunar_year': lunar_year,
            'lunar_month': lunar_month,
            'lunar_day': lunar_day,
            'is_leap': False  # 簡化版本不處理閏月
        }
        
    def _calculate_ming_palace(self):
        """計算命宮位置"""
        # 1. 獲取時辰地支
        hour_branch = ChineseCalendar.get_hour_branch(self.birth_info.hour)
        
        # 2. 獲取農曆月份
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        # 3. 計算命宮地支
        # 口訣：寅起順行至生月，生月起子兩頭通，逆至生時為命宮
        branches = ChineseCalendar.EARTHLY_BRANCHES
        
        # 從寅宮開始，順數到農曆生月
        yin_index = branches.index("寅")
        month_palace_index = (yin_index + lunar_month - 1) % 12
        
        # 從該宮的子位逆數到生時，得到命宮
        hour_branch_index = branches.index(hour_branch)
        zi_index = branches.index("子")
        ming_branch_index = (month_palace_index + zi_index - hour_branch_index) % 12
        ming_branch = branches[ming_branch_index]
        
        # 4. 計算命宮天干
        # 獲取月干
        year_stem = self.calendar_data.year_gan_zhi[0]  # 取年干
        month_stem = ChineseCalendar.get_month_stem(year_stem, lunar_month)
        
        # 命宮天干 = 月干 + 2
        month_stem_index = ChineseCalendar.HEAVENLY_STEMS.index(month_stem)
        ming_stem_index = (month_stem_index + 2) % 10
        ming_stem = ChineseCalendar.HEAVENLY_STEMS[ming_stem_index]
        
        # 5. 設置宮位順序 - 從命宮地支開始的順序
        # 找到命宮地支在固定地支順序中的位置
        ming_index_in_fixed_order = branches.index(ming_branch)
        # 創建從命宮開始的地支順序
        self.palace_order = [branches[(ming_index_in_fixed_order + i) % 12] for i in range(12)]
        
        logger.info(f"命宮計算結果 - 天干：{ming_stem} 地支：{ming_branch}")
        logger.info(f"宮位順序：{self.palace_order}")
        
        return ming_stem, ming_branch
        
    def _initialize_palaces(self):
        """初始化十二宮位"""
        # 修正宮位名稱順序：命宮後面應該是父母宮，不是兄弟宮
        palace_names = [
            "命宮", "父母", "福德", "田宅", "官祿", "交友",
            "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"
        ]
        
        # 根據生年天干計算各宮位天干
        year_stem = self.calendar_data.year_gan_zhi[0]  # 取年干
        palace_stems = ChineseCalendar.get_palace_stems(year_stem)
        
        # 地支位置是固定的，不變動
        # 根據命宮地支位置來分配宮位名稱
        ming_branch = self.palace_order[0]  # 命宮地支
        ming_index = ChineseCalendar.EARTHLY_BRANCHES.index(ming_branch)
        
        for i, name in enumerate(palace_names):
            # 計算該宮位對應的地支索引（順時針排列）
            branch_index = (ming_index + i) % 12
            branch = ChineseCalendar.EARTHLY_BRANCHES[branch_index]
            
            # 從宮干對照表獲取對應的天干
            stem = palace_stems[branch]
            
            # 獲取宮位五行
            element = ChineseCalendar.BRANCH_ELEMENTS[branch]
            
            self.palaces[name] = Palace(
                name=name,
                stars=[],
                element=element,
                stem=stem,
                branch=branch
            )
            
    def calculate_stars(self):
        """計算星曜位置"""
        logger.info("開始計算星曜位置")
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,  # 使用農曆月份
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour)
        }
        
        logger.info(f"準備傳遞給StarCalculator的birth_info: {birth_info_for_calculator}")
        
        self.star_calculator.calculate_stars(birth_info_for_calculator, self.palaces)
        
        # 檢查計算結果
        for palace_name, palace_info in self.palaces.items():
            logger.info(f"宮位 {palace_name} 的星曜: {palace_info.stars}")
        
        logger.info("星曜位置計算完成")
        
    def calculate_transformations(self) -> Dict[str, Dict[str, str]]:
        """計算四化"""
        if not self.calendar_data:
            return {}
            
        # 獲取年干
        year_stem = self.calendar_data.year_gan_zhi[0]
        
        # 獲取四化星
        transformations = self.star_calculator.FOUR_TRANSFORMATIONS.get(year_stem, {})
        
        # 準備結果字典
        result = {}
        
        # 遍歷每個四化類型
        for trans_type, star_name in transformations.items():
            # 找到該星所在的宮位
            palace_name = self.find_star_palace(star_name)
            if palace_name:
                # 獲取該四化的解釋
                explanation = self.get_explanation_for_palace(
                    star_name=star_name,
                    transformation_type=trans_type,
                    palace_name=palace_name,
                    birth_info={
                        'year_stem': year_stem,
                        'gender': self.birth_info.gender
                    }
                )
                
                # 將結果添加到字典中
                result[star_name] = {
                    '四化': trans_type,
                    '宮位': palace_name,
                    **explanation
                }
        
        return result
        
    def get_four_transformations_explanations(self):
        """獲取四化解釋"""
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour),
            'gender': self.birth_info.gender
        }
        
        return self.star_calculator.get_four_transformations_explanations(
            birth_info_for_calculator, 
            self.palaces
        )
        
    def get_four_transformations_explanations_by_stem(self, custom_stem: str):
        """獲取自定義天干的四化解釋"""
        return self.star_calculator.get_four_transformations_explanations_by_stem(
            custom_stem, 
            self.palaces
        )

    def apply_custom_stem_transformations(self, custom_stem: str):
        """應用自定義天干的四化到命盤中，並回傳解釋"""
        # 首先清除所有現有的四化標記
        self._clear_all_transformations()
        
        # 準備birth_info給StarCalculator使用
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': custom_stem,  # 使用自定義天干替代原生年天干
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour)
        }
        
        # 應用自定義天干的四化
        self.star_calculator._apply_four_transformations(birth_info_for_calculator, self.palaces)

        # 回傳計算後的四化解釋
        return self.get_four_transformations_explanations_by_stem(custom_stem)

    def _clear_all_transformations(self):
        """清除所有宮位中星曜的四化標記"""
        for palace_name, palace_info in self.palaces.items():
            updated_stars = []
            for star in palace_info.stars:
                # 移除所有四化標記（化祿、化權、化科、化忌）
                cleaned_star = star
                for transformation in ['化祿', '化權', '化科', '化忌']:
                    cleaned_star = cleaned_star.replace(transformation, '')
                updated_stars.append(cleaned_star)
            palace_info.stars = updated_stars

    def calculate_major_limits(self, current_age: int = None):
        """計算大限"""
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour),
            'gender': self.birth_info.gender
        }
        
        return self.star_calculator.calculate_major_limits(
            birth_info_for_calculator, 
            self.palaces, 
            current_age
        )
    
    def calculate_minor_limits(self, target_age: int = None):
        """計算小限"""
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour),
            'gender': self.birth_info.gender
        }
        
        return self.star_calculator.calculate_minor_limits(
            birth_info_for_calculator, 
            self.palaces, 
            target_age
        )
    
    def calculate_annual_fortune(self, target_year: int = None):
        """計算流年"""
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour),
            'gender': self.birth_info.gender
        }
        
        return self.star_calculator.calculate_annual_fortune(
            birth_info_for_calculator, 
            self.palaces, 
            target_year
        )
    
    def calculate_monthly_fortune(self, target_year: int = None, target_month: int = None):
        """計算流月"""
        # 首先計算流年
        annual_fortune = self.calculate_annual_fortune(target_year)
        
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour),
            'gender': self.birth_info.gender
        }
        
        return self.star_calculator.calculate_monthly_fortune(
            birth_info_for_calculator, 
            self.palaces, 
            annual_fortune,
            target_month
        )
    
    def calculate_daily_fortune(self, target_year: int = None, target_month: int = None, target_day: int = None):
        """計算流日"""
        # 首先計算流年和流月
        annual_fortune = self.calculate_annual_fortune(target_year)
        monthly_fortune = self.calculate_monthly_fortune(target_year, target_month)
        
        # 準備傳遞給StarCalculator的birth_info
        year_stem = self.calendar_data.year_gan_zhi[0]  # 生年天干
        year_branch = self.calendar_data.year_gan_zhi[1]  # 生年地支
        ming_branch = self.palace_order[0]  # 命宮地支（第一個宮位）
        
        # 從calendar_data中獲取農曆日期和月份
        lunar_day = ChineseCalendar.parse_chinese_day(self.calendar_data.lunar_day_in_chinese)
        lunar_month = ChineseCalendar.parse_chinese_month(self.calendar_data.lunar_month_in_chinese)
        
        birth_info_for_calculator = {
            'year_stem': year_stem,
            'year_branch': year_branch,
            'ming_branch': ming_branch,
            'lunar_day': lunar_day,
            'lunar_month': lunar_month,
            'lunar_hour_branch': ChineseCalendar.get_hour_branch(self.birth_info.hour),
            'gender': self.birth_info.gender
        }
        
        return self.star_calculator.calculate_daily_fortune(
            birth_info_for_calculator, 
            self.palaces, 
            annual_fortune,
            monthly_fortune,
            target_day
        )
        
    def get_chart(self, include_major_limits: bool = False, current_age: int = None, include_minor_limits: bool = False, target_age: int = None) -> Dict:
        """
        獲取完整命盤數據
        
        Args:
            include_major_limits: 是否包含大限
            current_age: 當前年齡（用於計算大限）
            include_minor_limits: 是否包含小限
            target_age: 目標年齡（用於計算小限）
            
        Returns:
            命盤數據字典
        """
        try:
            logger.info("開始獲取命盤數據")
            
            # 基本命盤資訊
            chart_data = {
                "birth_info": {
                    "year": self.birth_info.year,
                    "month": self.birth_info.month,
                    "day": self.birth_info.day,
                    "hour": self.birth_info.hour,
                    "minute": self.birth_info.minute,
                    "gender": self.birth_info.gender,
                    "longitude": self.birth_info.longitude,
                    "latitude": self.birth_info.latitude
                },
                "lunar_info": {
                    "year": self.calendar_data.lunar_year_in_chinese,
                    "month": self.calendar_data.lunar_month_in_chinese,
                    "day": self.calendar_data.lunar_day_in_chinese,
                    "year_gan_zhi": self.calendar_data.year_gan_zhi,
                    "month_gan_zhi": self.calendar_data.month_gan_zhi,
                    "day_gan_zhi": self.calendar_data.day_gan_zhi,
                    "hour_gan_zhi": self.calendar_data.hour_gan_zhi,
                    "minute_gan_zhi": self.calendar_data.minute_gan_zhi
                },
                "palaces": {}
            }
            
            # 添加宮位資訊
            for name, palace in self.palaces.items():
                chart_data["palaces"][name] = {
                    "name": palace.name,
                    "stars": palace.stars,
                    "element": palace.element,
                    "tiangan": palace.stem,
                    "dizhi": palace.branch,
                    "is_body_palace": palace.body_palace
                }
            
            # 添加大限資訊
            if include_major_limits and current_age is not None:
                major_limits = self.calculate_major_limits(current_age)
                chart_data["major_limits"] = major_limits
            
            # 添加小限資訊
            if include_minor_limits and target_age is not None:
                minor_limits = self.calculate_minor_limits(target_age)
                chart_data["minor_limits"] = minor_limits
            
            logger.info("命盤數據獲取完成")
            return chart_data
            
        except Exception as e:
            logger.error(f"獲取命盤數據時發生錯誤：{str(e)}")
            raise

    def find_star_palace(self, star_name: str) -> Optional[str]:
        """找到星曜所在的宮位
        
        Args:
            star_name: 要查找的星曜名稱
            
        Returns:
            宮位名稱，如果找不到則返回 None
        """
        logger.info(f"開始查找星曜 {star_name} 所在宮位")
        
        # 清理星曜名稱，去除可能的狀態描述和四化標記
        clean_target_name = star_name.split("（")[0] if "（" in star_name else star_name
        clean_target_name = clean_target_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
        
        logger.info(f"清理後的星曜名稱: {clean_target_name}")
        
        for palace_name, palace_info in self.palaces.items():
            logger.info(f"檢查宮位 {palace_name} 的星曜: {palace_info.stars}")
            for star in palace_info.stars:
                # 清理當前星曜名稱
                clean_star_name = star.split("（")[0] if "（" in star else star
                clean_star_name = clean_star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
                
                logger.info(f"比對星曜: {clean_star_name} vs {clean_target_name}")
                
                if clean_star_name == clean_target_name:
                    logger.info(f"找到星曜 {star_name} 在宮位 {palace_name}")
                    return palace_name
        
        logger.warning(f"未找到星曜 {star_name} 所在宮位")
        return None

    def get_explanation_for_palace(self, star_name: str, transformation_type: str, palace_name: str, birth_info: Dict) -> Dict[str, str]:
        """獲取宮位解釋"""
        # 獲取四化解釋
        explanation = four_transformations_explanations.get(transformation_type, {})
        
        # 獲取星曜解釋
        star_explanation = explanation.get(star_name, {})
        
        # 獲取宮位解釋
        palace_explanation = star_explanation.get(palace_name, {})
        
        # 根據性別獲取解釋
        gender = birth_info.get('gender', 'M')
        gender_explanation = palace_explanation.get(gender, {})
        
        return {
            '現象': gender_explanation.get('現象', ''),
            '心理傾向': gender_explanation.get('心理傾向', ''),
            '可能事件': gender_explanation.get('可能事件', ''),
            '提示': gender_explanation.get('提示', ''),
            '來意不明建議': gender_explanation.get('來意不明建議', '')
        }

    def apply_taichi(self, taichi_branch: str):
        """
        將原盤轉換為太極盤：根據太極點地支重新旋轉十二宮位
        
        這個方法會：
        1. 將原本的 self.palaces 按太極點地支重新排序
        2. 更新每個宮位的名稱、地支、天干、星曜位置
        3. 替換 self.palaces 為太極盤
        4. 後續所有計算都基於這個太極盤
        
        Args:
            taichi_branch: 太極點地支（作為新命宮的地支）
        """
        try:
            logger.info(f"開始應用太極點旋轉，太極點地支：{taichi_branch}")
            
            # 十二地支順序
            branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
            
            # 十二宮位順序（以命宮為起點）
            palace_names = ["命宮", "父母宮", "福德宮", "田宅宮", "官祿宮", "交友宮", 
                           "遷移宮", "疾厄宮", "財帛宮", "子女宮", "夫妻宮", "兄弟宮"]
            
            # 找到太極點地支的索引
            try:
                taichi_index = branches.index(taichi_branch)
            except ValueError:
                logger.error(f"無效的太極點地支: {taichi_branch}")
                return  # 不執行旋轉
            
            # 建立原盤地支到宮位對象的映射
            original_branch_to_palace = {}
            for palace_name, palace in self.palaces.items():
                original_branch_to_palace[palace.branch] = palace
            
            logger.info(f"原盤地支對應：{list(original_branch_to_palace.keys())}")
            
            # 建立新的太極盤
            new_palaces = {}
            new_palace_order = []
            
            for i in range(12):
                # 計算新宮位對應的原始地支
                original_branch_index = (taichi_index + i) % 12
                original_branch = branches[original_branch_index]
                
                # 獲取原宮位對象
                original_palace = original_branch_to_palace.get(original_branch)
                if not original_palace:
                    logger.warning(f"未找到地支 {original_branch} 對應的原宮位")
                    continue
                
                # 建立新宮位名稱
                new_palace_name = palace_names[i]
                
                # 創建新的宮位對象，保留原宮位的星曜、天干、地支等屬性
                new_palace = Palace(
                    name=new_palace_name,
                    stars=original_palace.stars.copy(),  # 星曜保持不變
                    element=original_palace.element,     # 五行屬性保持不變
                    stem=original_palace.stem,           # 天干保持不變
                    branch=original_branch,              # 地支保持不變
                    body_palace=original_palace.body_palace  # 身宮標記保持不變
                )
                
                new_palaces[new_palace_name] = new_palace
                new_palace_order.append(new_palace_name)
                
                logger.info(f"太極盤映射：{new_palace_name} ← 原{original_palace.name}（{original_branch}）")
            
            # 替換原盤為太極盤
            self.palaces = new_palaces
            self.palace_order = new_palace_order
            
            logger.info(f"太極盤轉換完成，新宮位順序：{new_palace_order}")
            logger.info(f"太極點命宮地支：{taichi_branch}，現在對應「命宮」")
            
        except Exception as e:
            logger.error(f"太極點旋轉失敗：{e}")
            raise 

    def get_taichi_sihua_explanations(self, taichi_stem: str) -> List[Dict]:
        """
        基於太極盤獲取四化解釋
        
        這個方法會：
        1. 根據太極點天干計算四化星
        2. 在太極盤中找到四化星的宮位
        3. 直接用太極盤的宮位名稱從靜態資料表獲取解釋
        
        Args:
            taichi_stem: 太極點天干
            
        Returns:
            List[Dict]: 四化解釋列表
        """
        try:
            logger.info(f"開始基於太極盤獲取四化解釋，太極點天干：{taichi_stem}")
            
            # 1. 使用 StarCalculator 中的四化星表（包含輔星）
            sihua_stars = self.star_calculator.FOUR_TRANSFORMATIONS.get(taichi_stem, {})
            if not sihua_stars:
                logger.warning(f"未找到天干 {taichi_stem} 的四化星")
                return []
            
            logger.info(f"四化星：{sihua_stars}")
            
            # 2. 在太極盤中找到四化星的宮位並獲取解釋
            results = []
            
            for trans_type, star_name in sihua_stars.items():
                # 清理星曜名稱
                clean_star_name = star_name.replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "").strip()
                
                # 在太極盤中找到星曜所在的宮位
                star_palace = None
                for palace_name, palace in self.palaces.items():
                    for star in palace.stars:
                        clean_palace_star = str(star).replace("化祿", "").replace("化權", "").replace("化科", "").replace("化忌", "")
                        if "（" in clean_palace_star:
                            clean_palace_star = clean_palace_star.split("（")[0]
                        clean_palace_star = clean_palace_star.strip()
                        
                        if clean_palace_star == clean_star_name:
                            star_palace = palace_name
                            break
                    if star_palace:
                        break
                
                if not star_palace:
                    logger.warning(f"未在太極盤中找到星曜 {star_name}")
                    continue
                
                logger.info(f"四化星 {star_name} 在太極盤中位於：{star_palace}")
                
                # 3. 從靜態資料表獲取解釋
                explanation = self._get_explanation_from_data(taichi_stem, trans_type, star_palace)
                
                result = {
                    "type": trans_type,
                    "transformation_type": trans_type,
                    "star": star_name,
                    "star_name": star_name,
                    "palace": star_palace,
                    "taichi_palace": star_palace,
                    "explanation": explanation
                }
                
                results.append(result)
                logger.info(f"✅ {star_name}化{trans_type}在{star_palace}：{explanation.get('現象', '')[:50]}...")
            
            logger.info(f"太極盤四化解釋獲取完成，共 {len(results)} 個")
            return results
            
        except Exception as e:
            logger.error(f"獲取太極盤四化解釋失敗：{e}")
            return []

    def _get_explanation_from_data(self, stem: str, trans_type: str, palace_name: str) -> Dict[str, str]:
        """
        從靜態資料表獲取特定天干、四化類型、宮位的解釋
        
        Args:
            stem: 天干
            trans_type: 四化類型（祿/權/科/忌）
            palace_name: 宮位名稱
            
        Returns:
            Dict[str, str]: 解釋內容
        """
        try:
            # 從四化解釋資料中獲取
            stem_data = four_transformations_explanations.get(stem, {})
            trans_data = stem_data.get(trans_type, {})
            explanations_list = trans_data.get("解釋", [])
            
            # 查找對應宮位的解釋
            for explanation in explanations_list:
                if explanation.get("宮位") == palace_name:
                    return {
                        "現象": explanation.get("現象", ""),
                        "心理傾向": explanation.get("心理傾向", ""),
                        "可能事件": explanation.get("可能事件", ""),
                        "提示": explanation.get("提示", ""),
                        "來意不明建議": explanation.get("來意不明建議", "")
                    }
            
            # 如果沒找到特定宮位的解釋，使用預設內容
            logger.warning(f"未找到天干{stem}、{trans_type}、{palace_name}的特定解釋，使用預設解釋")
            return {
                "現象": f"{trans_type}星在{palace_name}，帶來相關的能量與變化。",
                "心理傾向": "需要特別關注這個領域的發展。",
                "可能事件": "此宮位可能有相關的機會或挑戰。",
                "提示": f"多留意{palace_name}相關的事務。",
                "來意不明建議": f"善用{trans_type}的能量在{palace_name}上。"
            }
            
        except Exception as e:
            logger.error(f"從資料表獲取解釋失敗：{e}")
            return {
                "現象": "今日運勢需要特別留意。",
                "心理傾向": "保持開放心態。", 
                "可能事件": "可能有意外的變化。",
                "提示": "順應時勢，隨機應變。",
                "來意不明建議": "把握當下，隨緣而安。"
            } 