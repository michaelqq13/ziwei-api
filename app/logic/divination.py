"""
紫微斗數占卜邏輯模組 - 重構版
簡化邏輯，確保穩定運行
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.divination import DivinationRecord
from app.models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)

def get_week_start_date(date: datetime) -> datetime:
    """獲取週一的日期（週的開始）"""
    days_since_monday = date.weekday()
    week_start = date - timedelta(days=days_since_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def get_days_until_next_monday() -> int:
    """計算距離下週一的天數"""
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    return days_until_monday if days_until_monday > 0 else 7

def can_divination_this_week(user_id: str, db: Session) -> bool:
    """檢查本週是否可以占卜"""
    today = datetime.now()
    week_start = get_week_start_date(today)
    
    existing_record = db.query(DivinationRecord).filter(
        DivinationRecord.user_id == user_id,
        DivinationRecord.week_start_date == week_start.date()
    ).first()
    
    return existing_record is None

def get_this_week_divination(user_id: str, db: Session) -> Optional[DivinationRecord]:
    """獲取本週的占卜記錄"""
    today = datetime.now()
    week_start = get_week_start_date(today)
    
    return db.query(DivinationRecord).filter(
        DivinationRecord.user_id == user_id,
        DivinationRecord.week_start_date == week_start.date()
    ).first()

def get_user_divination_gender(user_id: str, db: Session) -> Optional[str]:
    """獲取用戶的占卜性別偏好"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == user_id
    ).first()
    
    return preferences.divination_gender if preferences else None

def save_user_divination_gender(user_id: str, gender: str, db: Session):
    """保存用戶的占卜性別偏好"""
    try:
        preferences = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if preferences:
            preferences.divination_gender = gender
        else:
            preferences = UserPreferences(
                user_id=user_id,
                divination_gender=gender
            )
            db.add(preferences)
        
        db.commit()
        logger.info(f"已保存用戶 {user_id} 的性別偏好: {gender}")
    except Exception as e:
        db.rollback()
        logger.error(f"保存性別偏好失敗: {e}")
        raise

def calculate_divination(divination_time: datetime, gender: str, db: Session = None) -> Dict[str, Any]:
    """
    簡化版占卜計算
    返回基本的占卜結果，避免複雜邏輯導致的錯誤
    """
    try:
        logger.info(f"開始計算占卜: {divination_time}, 性別: {gender}")
        
        # 基於時間生成簡單的占卜結果
        hour = divination_time.hour
        minute = divination_time.minute
        day = divination_time.day
        
        logger.info(f"時間參數: hour={hour}, minute={minute}, day={day}")
        
        # 生成基本運勢分析
        fortune_aspects = generate_fortune_aspects(hour, minute, day)
        summary = generate_simple_summary(fortune_aspects)
        
        logger.info(f"基本運勢分析: {fortune_aspects}")
        logger.info(f"運勢摘要: {summary}")
        
        # 計算四化
        from app.logic.purple_star_chart import PurpleStarChart
        from app.db.repository import CalendarRepository
        from app.models.birth_info import BirthInfo
        
        logger.info("開始創建命盤...")
        
        try:
            # 直接使用參數創建命盤，不需要創建 BirthInfo
            logger.info("開始初始化 PurpleStarChart...")
            chart = PurpleStarChart(
                year=divination_time.year,
                month=divination_time.month,
                day=divination_time.day,
                hour=divination_time.hour,
                minute=divination_time.minute,
                gender=gender,
                db=db
            )
            
            # 獲取四化解釋
            logger.info("開始獲取四化解釋...")
            four_transformations = chart.get_four_transformations_explanations()
            logger.info(f"四化解釋: {four_transformations}")
            
        except Exception as e:
            logger.error(f"命盤計算過程出錯: {e}", exc_info=True)
            four_transformations = {}
        
        result = {
            "divination_time": divination_time.isoformat(),
            "gender": gender,
            "fortune_aspects": fortune_aspects,
            "summary": summary,
            "week_focus": get_week_focus(divination_time),
            "advice": get_simple_advice(fortune_aspects),
            "four_transformations": list(four_transformations.values())  # 轉換為列表格式
        }
        
        logger.info(f"占卜計算完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"計算占卜失敗: {e}", exc_info=True)
        # 返回預設結果，確保不會崩潰
        return get_default_divination_result(divination_time, gender)

def generate_fortune_aspects(hour: int, minute: int, day: int) -> Dict[str, str]:
    """根據時間生成運勢面向"""
    aspects = {}
    
    # 事業運
    career_score = (hour + day) % 5
    career_fortunes = ["需要謹慎規劃", "穩步發展", "有新機會", "表現突出", "大展宏圖"]
    aspects["事業"] = career_fortunes[career_score]
    
    # 財運
    wealth_score = (minute + day) % 5
    wealth_fortunes = ["理財保守", "收支平衡", "小有收穫", "財運亨通", "投資有利"]
    aspects["財運"] = wealth_fortunes[wealth_score]
    
    # 感情
    love_score = (hour + minute) % 5
    love_fortunes = ["需要溝通", "關係穩定", "桃花運佳", "感情甜蜜", "情投意合"]
    aspects["感情"] = love_fortunes[love_score]
    
    # 健康
    health_score = (day + minute) % 5
    health_fortunes = ["注意休息", "狀態良好", "精神飽滿", "活力充沛", "身心愉悅"]
    aspects["健康"] = health_fortunes[health_score]
    
    return aspects

def generate_simple_summary(fortune_aspects: Dict[str, str]) -> str:
    """生成簡單的運勢摘要"""
    summaries = [
        "本週整體運勢平穩，適合穩紮穩打。",
        "本週有不錯的發展機會，把握時機。",
        "本週需要多加注意細節，謹慎行事。",
        "本週運勢向好，可以積極進取。",
        "本週適合休整調養，為未來蓄力。"
    ]
    
    # 根據運勢面向選擇摘要
    positive_count = sum(1 for aspect in fortune_aspects.values() 
                        if any(word in aspect for word in ["好", "佳", "利", "通", "滿", "甜", "充"]))
    
    if positive_count >= 3:
        return summaries[3]  # 積極
    elif positive_count >= 2:
        return summaries[1]  # 機會
    elif positive_count >= 1:
        return summaries[0]  # 平穩
    else:
        return summaries[2]  # 謹慎

def get_week_focus(divination_time: datetime) -> str:
    """獲取本週重點關注事項"""
    week_focuses = [
        "人際關係的維護與發展",
        "工作效率的提升",
        "財務規劃與管理",
        "健康生活習慣的建立",
        "學習新技能或知識",
        "家庭關係的和諧",
        "創新思維的培養"
    ]
    
    focus_index = (divination_time.day + divination_time.hour) % len(week_focuses)
    return week_focuses[focus_index]

def get_simple_advice(fortune_aspects: Dict[str, str]) -> str:
    """根據運勢面向給出簡單建議"""
    advice_list = [
        "保持積極心態，機會總是留給有準備的人。",
        "適度休息，勞逸結合才能走得更遠。",
        "多與他人溝通交流，團隊合作創造更大價值。",
        "謹慎決策，三思而後行避免不必要的風險。",
        "持續學習成長，投資自己永遠不會虧本。"
    ]
    
    # 根據運勢特點選擇建議
    aspects_text = " ".join(fortune_aspects.values())
    
    if "謹慎" in aspects_text or "保守" in aspects_text:
        return advice_list[3]  # 謹慎建議
    elif "機會" in aspects_text or "發展" in aspects_text:
        return advice_list[0]  # 積極建議
    elif "溝通" in aspects_text or "關係" in aspects_text:
        return advice_list[2]  # 溝通建議
    elif "休息" in aspects_text or "調養" in aspects_text:
        return advice_list[1]  # 休息建議
    else:
        return advice_list[4]  # 學習建議

def get_default_divination_result(divination_time: datetime, gender: str) -> Dict[str, Any]:
    """獲取預設的占卜結果（錯誤時使用）"""
    return {
        "divination_time": divination_time.isoformat(),
        "gender": gender,
        "fortune_aspects": {
            "事業": "穩步發展",
            "財運": "收支平衡", 
            "感情": "關係穩定",
            "健康": "狀態良好"
        },
        "summary": "本週整體運勢平穩，適合穩紮穩打，保持積極心態面對各項挑戰。",
        "week_focus": "工作效率的提升",
        "advice": "保持積極心態，機會總是留給有準備的人。",
        "four_transformations": [
            {
                "星曜": "廉貞",
                "四化": "祿",
                "宮位": "命宮",
                "現象": "今天格外渴望出頭，競爭力強，敢於展現自我。",
                "提示": "主動出擊就有機會，表現力是今天的優勢。"
            },
            {
                "星曜": "破軍",
                "四化": "權",
                "宮位": "財帛宮",
                "現象": "財務決策能力增強，善於把握投資機會。",
                "提示": "理性分析，不要衝動決策。"
            },
            {
                "星曜": "武曲",
                "四化": "科",
                "宮位": "事業宮",
                "現象": "工作中展現專業能力，容易獲得認可。",
                "提示": "專注於自己的專業領域發展。"
            },
            {
                "星曜": "太陽",
                "四化": "忌",
                "宮位": "疾厄宮",
                "現象": "需要注意身體健康，避免過度勞累。",
                "提示": "及時休息，保持良好作息。"
            }
        ]
    }

def save_divination_record(user_id: str, divination_time: datetime, gender: str, 
                          divination_result: Dict[str, Any], db: Session):
    """保存占卜記錄"""
    try:
        week_start = get_week_start_date(divination_time)
        
        new_record = DivinationRecord(
            user_id=user_id,
            divination_time=divination_time,
            week_start_date=week_start.date(),
            gender=gender,
            divination_result=divination_result
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        logger.info(f"已為用戶 {user_id} 保存占卜記錄")
        return new_record
    except Exception as e:
        db.rollback()
        logger.error(f"保存占卜記錄失敗: {e}")
        raise 