"""
占卜狀態管理
使用狀態機模式管理複雜的多步驟占卜流程
"""
import logging
from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class DivinationState(Enum):
    """占卜流程狀態枚舉"""
    IDLE = "idle"                           # 空閒狀態
    SELECTING_TIME = "selecting_time"       # 選擇時間
    SELECTING_GENDER = "selecting_gender"   # 選擇性別
    EXECUTING = "executing"                 # 執行占卜
    COMPLETED = "completed"                 # 完成
    ERROR = "error"                         # 錯誤狀態

class DivinationType(Enum):
    """占卜類型枚舉"""
    WEEKLY = "weekly"                       # 本週占卜
    TIME_SPECIFIED = "time_specified"       # 指定時間占卜
    FORTUNE = "fortune"                     # 運勢占卜

@dataclass
class DivinationSession:
    """占卜會話數據"""
    user_id: str
    state: DivinationState = DivinationState.IDLE
    divination_type: Optional[DivinationType] = None
    selected_time: Optional[str] = None
    selected_gender: Optional[str] = None
    context: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """初始化後處理"""
        if self.context is None:
            self.context = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

class DivinationStateMachine:
    """占卜狀態機"""
    
    # 狀態轉換規則
    TRANSITIONS = {
        DivinationState.IDLE: [
            DivinationState.SELECTING_TIME,
            DivinationState.SELECTING_GENDER,
            DivinationState.EXECUTING
        ],
        DivinationState.SELECTING_TIME: [
            DivinationState.SELECTING_GENDER,
            DivinationState.ERROR,
            DivinationState.IDLE
        ],
        DivinationState.SELECTING_GENDER: [
            DivinationState.EXECUTING,
            DivinationState.ERROR,
            DivinationState.IDLE
        ],
        DivinationState.EXECUTING: [
            DivinationState.COMPLETED,
            DivinationState.ERROR
        ],
        DivinationState.COMPLETED: [
            DivinationState.IDLE
        ],
        DivinationState.ERROR: [
            DivinationState.IDLE
        ]
    }
    
    def __init__(self):
        self.sessions: Dict[str, DivinationSession] = {}
    
    def get_session(self, user_id: str) -> DivinationSession:
        """獲取或創建用戶會話"""
        if user_id not in self.sessions:
            self.sessions[user_id] = DivinationSession(user_id=user_id)
            logger.info(f"創建新的占卜會話: {user_id}")
        
        session = self.sessions[user_id]
        session.updated_at = datetime.now()
        return session
    
    def can_transition(self, user_id: str, new_state: DivinationState) -> bool:
        """檢查是否可以轉換到新狀態"""
        session = self.get_session(user_id)
        current_state = session.state
        
        allowed_states = self.TRANSITIONS.get(current_state, [])
        can_change = new_state in allowed_states
        
        logger.info(f"狀態轉換檢查 - 用戶: {user_id}, 當前: {current_state.value}, 目標: {new_state.value}, 允許: {can_change}")
        return can_change
    
    def transition_to(self, user_id: str, new_state: DivinationState, context: Dict[str, Any] = None) -> bool:
        """轉換到新狀態"""
        if not self.can_transition(user_id, new_state):
            logger.warning(f"無效的狀態轉換 - 用戶: {user_id}, 目標狀態: {new_state.value}")
            return False
        
        session = self.get_session(user_id)
        old_state = session.state
        session.state = new_state
        session.updated_at = datetime.now()
        
        # 更新上下文
        if context:
            session.context.update(context)
        
        logger.info(f"✅ 狀態轉換成功 - 用戶: {user_id}, {old_state.value} → {new_state.value}")
        return True
    
    def start_time_divination(self, user_id: str) -> bool:
        """開始指定時間占卜流程"""
        session = self.get_session(user_id)
        session.divination_type = DivinationType.TIME_SPECIFIED
        
        return self.transition_to(
            user_id, 
            DivinationState.SELECTING_TIME,
            {"divination_type": DivinationType.TIME_SPECIFIED.value}
        )
    
    def start_weekly_divination(self, user_id: str) -> bool:
        """開始本週占卜流程"""
        session = self.get_session(user_id)
        session.divination_type = DivinationType.WEEKLY
        
        return self.transition_to(
            user_id,
            DivinationState.SELECTING_GENDER,
            {"divination_type": DivinationType.WEEKLY.value}
        )
    
    def set_time(self, user_id: str, time_value: str) -> bool:
        """設置選擇的時間"""
        session = self.get_session(user_id)
        
        if session.state != DivinationState.SELECTING_TIME:
            logger.warning(f"用戶 {user_id} 不在選擇時間狀態")
            return False
        
        session.selected_time = time_value
        
        return self.transition_to(
            user_id,
            DivinationState.SELECTING_GENDER,
            {"selected_time": time_value}
        )
    
    def set_gender(self, user_id: str, gender: str) -> bool:
        """設置選擇的性別"""
        session = self.get_session(user_id)
        
        if session.state != DivinationState.SELECTING_GENDER:
            logger.warning(f"用戶 {user_id} 不在選擇性別狀態")
            return False
        
        session.selected_gender = gender
        
        return self.transition_to(
            user_id,
            DivinationState.EXECUTING,
            {"selected_gender": gender}
        )
    
    def complete_divination(self, user_id: str, result: Dict[str, Any]) -> bool:
        """完成占卜"""
        session = self.get_session(user_id)
        
        if session.state != DivinationState.EXECUTING:
            logger.warning(f"用戶 {user_id} 不在執行占卜狀態")
            return False
        
        return self.transition_to(
            user_id,
            DivinationState.COMPLETED,
            {"divination_result": result}
        )
    
    def handle_error(self, user_id: str, error: str) -> bool:
        """處理錯誤"""
        return self.transition_to(
            user_id,
            DivinationState.ERROR,
            {"error": error, "error_time": datetime.now().isoformat()}
        )
    
    def reset_session(self, user_id: str) -> bool:
        """重置會話到空閒狀態"""
        session = self.get_session(user_id)
        session.state = DivinationState.IDLE
        session.divination_type = None
        session.selected_time = None
        session.selected_gender = None
        session.context.clear()
        session.updated_at = datetime.now()
        
        logger.info(f"重置占卜會話: {user_id}")
        return True
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理過期會話"""
        current_time = datetime.now()
        to_remove = []
        
        for user_id, session in self.sessions.items():
            age = current_time - session.updated_at
            if age.total_seconds() > max_age_hours * 3600:
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.sessions[user_id]
            logger.info(f"清理過期會話: {user_id}")
        
        return len(to_remove)

# 全局狀態機實例
divination_state_machine = DivinationStateMachine()

# 導出
__all__ = [
    "DivinationState",
    "DivinationType", 
    "DivinationSession",
    "DivinationStateMachine",
    "divination_state_machine"
] 