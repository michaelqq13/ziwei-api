"""
原始的占卜邏輯 - 備份版本
包含完整的觸機占卜算法
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

def get_current_taipei_time() -> datetime:
    """獲取當前台北時間"""
    return datetime.now(TAIPEI_TZ)

def get_week_start_date(date: datetime) -> datetime:
    """獲取週一的日期（週的開始）"""
    days_to_monday = date.weekday()  # 0=Monday, 6=Sunday
    week_start = date - timedelta(days=days_to_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def get_days_until_next_monday() -> int:
    """計算距離下週一的天數"""
    today = get_current_taipei_time()
    days_until_monday = (7 - today.weekday()) % 7
    return days_until_monday if days_until_monday > 0 else 7

def can_divination_this_week(user_id: str, db: Session) -> bool:
    """檢查本週是否可以占卜"""
    today = get_current_taipei_time()
    week_start = get_week_start_date(today)
    
    from app.models.divination import DivinationRecord
    existing_record = db.query(DivinationRecord).filter(
        DivinationRecord.user_id == user_id,
        DivinationRecord.week_start_date == week_start.date()
    ).first()
    
    return existing_record is None

def get_this_week_divination(user_id: str, db: Session):
    """獲取本週的占卜記錄"""
    today = get_current_taipei_time()
    week_start = get_week_start_date(today)
    
    from app.models.divination import DivinationRecord
    record = db.query(DivinationRecord).filter(
        DivinationRecord.user_id == user_id,
        DivinationRecord.week_start_date == week_start.date()
    ).first()
    
    return record

def get_user_divination_gender(user_id: str, db: Session) -> Optional[str]:
    """獲取用戶的占卜性別偏好"""
    from app.models.user_preferences import UserPreference
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == user_id
    ).first()
    
    if preferences and preferences.divination_gender:
        return preferences.divination_gender
    return None

def save_user_divination_gender(user_id: str, gender: str, db: Session):
    """保存用戶的占卜性別偏好"""
    try:
        from app.models.user_preferences import UserPreference
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if preferences:
            preferences.divination_gender = gender
        else:
            preferences = UserPreference(user_id=user_id, divination_gender=gender)
            db.add(preferences)
        
        db.commit()
        logger.info(f"已為用戶 {user_id} 保存性別偏好: {gender}")
    except Exception as e:
        db.rollback()
        logger.error(f"保存性別偏好失敗: {e}")
        raise

def save_divination_record(user_id: str, divination_time: datetime, gender: str, 
                          divination_result: Dict[str, Any], db: Session):
    """保存占卜記錄"""
    try:
        week_start = get_week_start_date(divination_time)
        
        from app.models.divination import DivinationRecord
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