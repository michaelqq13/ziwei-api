"""
簡化占卜系統
提供基本的占卜功能，避免複雜邏輯導致的錯誤
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

def can_divination_this_week(user_id: str, db: Session) -> bool:
    """檢查本週是否可以占卜"""
    try:
        # 使用台北時間獲取當前時間
        today = get_current_taipei_time()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        from app.models.divination import DivinationRecord
        record = db.query(DivinationRecord).filter(
            DivinationRecord.user_id == user_id,
            DivinationRecord.created_at >= week_start
        ).first()
        
        return record is None
    except Exception as e:
        logger.error(f"檢查週占卜狀態失敗: {e}")
        return False

def get_this_week_divination(user_id: str, db: Session) -> Optional['DivinationRecord']:
    """獲取本週的占卜記錄"""
    try:
        from app.models.divination import DivinationRecord
        
        # 使用台北時間獲取當前時間
        today = get_current_taipei_time()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        record = db.query(DivinationRecord).filter(
            DivinationRecord.user_id == user_id,
            DivinationRecord.created_at >= week_start
        ).first()
        
        return record
    except Exception as e:
        logger.error(f"獲取週占卜記錄失敗: {e}")
        return None

def get_user_divination_gender(user_id: str, db: Session) -> Optional[str]:
    """獲取用戶占卜的性別偏好"""
    try:
        from app.models.user_preferences import UserPreference
        
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if preference and preference.preferred_gender:
            return preference.preferred_gender
        
        # 如果沒有偏好設定，檢查最近的占卜記錄
        from app.models.divination import DivinationRecord
        recent_record = db.query(DivinationRecord).filter(
            DivinationRecord.user_id == user_id
        ).order_by(DivinationRecord.created_at.desc()).first()
        
        if recent_record:
            return recent_record.gender
            
        return None
    except Exception as e:
        logger.error(f"獲取用戶性別偏好失敗: {e}")
        return None

def save_user_divination_gender(user_id: str, gender: str, db: Session) -> bool:
    """保存用戶占卜的性別偏好"""
    try:
        from app.models.user_preferences import UserPreference
        
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if preference:
            preference.preferred_gender = gender
        else:
            preference = UserPreference(
                user_id=user_id,
                preferred_gender=gender
            )
            db.add(preference)
        
        db.commit()
        return True
    except Exception as e:
        logger.error(f"保存用戶性別偏好失敗: {e}")
        db.rollback()
        return False

def calculate_divination(birth_info: Dict[str, Any], divination_time: str, db: Session = None) -> Dict[str, Any]:
    """
    執行占卜計算（簡化版本）
    
    Args:
        birth_info: 生辰八字資訊
        divination_time: 占卜時間
        db: 數據庫會話（可選）
    
    Returns:
        占卜結果字典
    """
    try:
        from app.logic.divination_logic import perform_detailed_divination
        
        # 調用詳細的占卜邏輯
        result = perform_detailed_divination(birth_info, divination_time, db)
        
        return result
        
    except Exception as e:
        logger.error(f"計算占卜失敗: {e}")
        return {
            "success": False,
            "error": f"占卜計算失敗: {str(e)}",
            "divination_time": divination_time
        }

def save_divination_result(user_id: str, result: Dict[str, Any], db: Session) -> bool:
    """
    保存占卜結果到數據庫
    
    Args:
        user_id: 用戶ID
        result: 占卜結果
        db: 數據庫會話
    
    Returns:
        是否保存成功
    """
    try:
        from app.models.divination import DivinationRecord
        import json
        
        # 提取關鍵資訊
        birth_info = result.get('birth_info', {})
        taichi_chart = result.get('taichi_chart', {})
        
        # 創建占卜記錄
        record = DivinationRecord(
            user_id=user_id,
            gender=birth_info.get('gender', 'M'),
            birth_year=birth_info.get('year'),
            birth_month=birth_info.get('month'),
            birth_day=birth_info.get('day'),
            birth_hour=birth_info.get('hour'),
            birth_minute=birth_info.get('minute'),
            birth_location=f"{birth_info.get('longitude', 0)},{birth_info.get('latitude', 0)}",
            divination_time=result.get('divination_time'),
            
            # 太極宮資訊
            taichi_palace=taichi_chart.get('taichi_palace', ''),
            palace_tiangan=taichi_chart.get('palace_tiangan', ''),
            palace_element=taichi_chart.get('palace_element', ''),
            
            # 結果資訊
            result_summary=result.get('interpretation_summary', ''),
            full_result=json.dumps(result, ensure_ascii=False),
            week_start_date=get_current_taipei_time().date(),
            created_at=get_current_taipei_time()
        )
        
        db.add(record)
        db.commit()
        
        logger.info(f"成功保存占卜結果，用戶: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"保存占卜結果失敗: {e}")
        db.rollback()
        return False 