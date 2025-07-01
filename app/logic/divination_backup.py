from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.birth_info import BirthInfo
from app.models.divination import DivinationRecord
from app.models.user_preferences import UserPreferences
from app.db.repository import CalendarRepository
from app.logic.purple_star_chart import PurpleStarChart
from app.utils.chinese_calendar import ChineseCalendar
import logging

logger = logging.getLogger(__name__)

def get_minute_branch(minute: int) -> str:
    """
    計算分鐘對應的地支（觸機用）
    一個時辰（120分鐘）完成一次六十甲子循環
    每2分鐘一個地支組合
    """
    gan_zhi_index = (minute // 2) % 60
    branch_index = gan_zhi_index % 12
    return ChineseCalendar.EARTHLY_BRANCHES[branch_index]

def get_minute_stem(minute: int) -> str:
    """
    計算分鐘對應的天干（觸機用）
    一個時辰（120分鐘）完成一次六十甲子循環
    每2分鐘一個天干組合
    """
    gan_zhi_index = (minute // 2) % 60
    stem_index = gan_zhi_index % 10
    return ChineseCalendar.HEAVENLY_STEMS[stem_index]

def get_week_start_date(date: datetime) -> datetime:
    """獲取該日期所在週的週一日期"""
    days_since_monday = date.weekday()
    monday = date - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)

def get_next_monday() -> datetime:
    """獲取下一個週一的日期"""
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:  # 如果今天是週一
        days_until_monday = 7
    next_monday = today + timedelta(days=days_until_monday)
    return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)

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

def get_trigger_ming_stem(year_stem: str, minute_branch: str) -> str:
    """根據年干和分鐘地支計算觸機命宮天干"""
    palace_stems = ChineseCalendar.get_palace_stems(year_stem)
    return palace_stems.get(minute_branch, "")

def calculate_divination(divination_time: datetime, gender: str, longitude: float = 121.5654, latitude: float = 25.0330, db: Session = None) -> Dict[str, Any]:
    """
    根據時間、性別和地點計算觸機占卜（修正版）
    使用 PurpleStarChart 的 apply_custom_stem_transformations 方法
    """
    try:
        logger.info(f"開始計算觸機占卜 (修正版): {divination_time}, 性別: {gender}")

        # 1. 創建一個以當前時間為基準的命盤，但不計算其自身的四化
        chart = PurpleStarChart(
            year=divination_time.year,
            month=divination_time.month,
            day=divination_time.day,
            hour=divination_time.hour,
            minute=divination_time.minute,
            gender=gender,
            db=db
        )
        # 此時 chart.palaces 已經包含了所有星曜的位置

        # 2. 確定觸機宮位和天干
        minute_branch = get_minute_branch(divination_time.minute)
        year_stem = chart.calendar_data.year_gan_zhi[0]
        trigger_ming_stem = get_trigger_ming_stem(year_stem, minute_branch)
        
        logger.info(f"占卜時間 {divination_time.minute}分 -> 分鐘地支: {minute_branch}")
        logger.info(f"觸機命宮天干: {trigger_ming_stem}")

        if not trigger_ming_stem:
            raise ValueError("無法計算觸機命宮天干")

        # 3. 應用觸機天干來計算四化
        four_transformations = chart.apply_custom_stem_transformations(trigger_ming_stem)
        
        # 4. 生成占卜摘要
        summary = generate_divination_summary(four_transformations)
        
        return {
            "divination_time": divination_time.isoformat(),
            "gender": gender,
            "location": f"經度:{longitude}, 緯度:{latitude}",
            "ming_gong_branch": minute_branch,
            "trigger_ming_stem": trigger_ming_stem,
            "four_transformations": four_transformations,
            "summary": summary,
            "trigger_mode": True
        }
        
    except Exception as e:
        logger.error(f"計算觸機占卜失敗: {e}", exc_info=True)
        raise

def generate_divination_summary(four_transformations: list) -> str:
    """根據四化解釋列表生成占卜摘要"""
    if not four_transformations:
        return "本週運勢平穩，建議保持積極心態面對各項挑戰。"
    
    summary_parts = []
    
    # 分析祿權科忌的影響
    for explanation in four_transformations:
        trans_type = explanation.get('四化', '')
        palace = explanation.get('宮位', '')
        
        if not palace:
            continue

        if trans_type == '祿':
            summary_parts.append(f"在{palace}方面可能有新的機遇或收穫")
        elif trans_type == '權':
            summary_parts.append(f"在{palace}方面可能掌握主導權或展現能力")
        elif trans_type == '科':
            summary_parts.append(f"在{palace}方面可能獲得好名聲或有學習機會")
        elif trans_type == '忌':
            summary_parts.append(f"在{palace}方面需要特別謹慎，可能遇到挑戰")
    
    if summary_parts:
        base_summary = f"本週重點：{', '.join(summary_parts[:2])}。"
    else:
        base_summary = "本週運勢平穩。"
    
    return base_summary + " 請結合自身情況，靈活應對。"

def save_divination_record(user_id: str, divination_time: datetime, gender: str, divination_result: Dict[str, Any], db: Session):
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

def get_days_until_next_monday() -> int:
    """獲取距離下個週一的天數"""
    today = datetime.now().date()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    return (next_monday - today).days 