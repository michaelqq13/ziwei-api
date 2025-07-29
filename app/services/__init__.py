"""
服務層模組
包含所有業務邏輯服務
"""

from .time_divination_service import (
    TimeDivinationService,
    TimeDivinationRequest,
    TimeDivinationResponse
)

# 導入 sixtail_service
try:
    from .sixtail_service import sixtail_service
    __all__ = [
        "TimeDivinationService",
        "TimeDivinationRequest", 
        "TimeDivinationResponse",
        "sixtail_service"
    ]
except ImportError as e:
    # 如果 sixtail_service 導入失敗，不包含在 __all__ 中
    print(f"Warning: Cannot import sixtail_service: {e}")
    __all__ = [
        "TimeDivinationService",
        "TimeDivinationRequest", 
        "TimeDivinationResponse"
    ] 