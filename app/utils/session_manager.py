from typing import Dict, Optional
from app.models.linebot_models import UserSession, UserBirthInfo

class SessionManager:
    """用戶會話管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
    
    def get_session(self, user_id: str) -> UserSession:
        """獲取或創建用戶會話"""
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(
                user_id=user_id,
                state="waiting_birth_info",
                current_step="start"
            )
        return self.sessions[user_id]
    
    def update_session(self, user_id: str, **updates) -> UserSession:
        """更新會話資訊"""
        session = self.get_session(user_id)
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        return session
    
    def clear_session(self, user_id: str) -> None:
        """清除用戶會話"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def set_birth_info_field(self, user_id: str, field: str, value) -> UserSession:
        """設置生辰資訊的特定欄位"""
        session = self.get_session(user_id)
        if session.birth_info is None:
            session.birth_info = UserBirthInfo()
        
        # 使用Pydantic的方式更新字段
        current_data = session.birth_info.dict()
        current_data[field] = value
        session.birth_info = UserBirthInfo(**current_data)
        
        return session
    
    def is_birth_info_complete(self, user_id: str) -> bool:
        """檢查生辰資訊是否完整"""
        session = self.get_session(user_id)
        if session.birth_info is None:
            return False
        
        required_fields = ['year', 'month', 'day', 'hour', 'gender']
        for field in required_fields:
            if getattr(session.birth_info, field, None) is None:
                return False
        return True

# 全局會話管理器實例
session_manager = SessionManager() 