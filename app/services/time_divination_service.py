"""
統一的指定時間占卜服務
整合所有指定時間占卜相關邏輯
"""
import logging
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from app.models.linebot_models import LineBotUser
from app.logic.divination_logic import get_divination_result
from app.utils.timezone_helper import TimezoneHelper
from app.logic.permission_manager import permission_manager

logger = logging.getLogger(__name__)

class TimeDivinationRequest(BaseModel):
    """指定時間占卜請求模型"""
    gender: str
    target_time: str
    purpose: Optional[str] = "指定時間占卜"
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['M', 'F']:
            raise ValueError('性別必須是 M 或 F')
        return v.upper()  # 統一轉換為大寫
    
    @validator('target_time')
    def validate_target_time(cls, v):
        try:
            # 驗證時間格式是否正確
            parsed_time = TimezoneHelper.parse_datetime_string(v)
            
            # 檢查時間範圍（不能太久遠）
            current_time = TimezoneHelper.get_current_taipei_time()
            time_diff = current_time - parsed_time
            
            # 限制在過去 30 天到未來 7 天內
            if time_diff.days > 30:
                raise ValueError('目標時間不能超過 30 天前')
            if time_diff.days < -7:
                raise ValueError('目標時間不能超過 7 天後')
                
            return v
        except Exception as e:
            raise ValueError(f'時間格式錯誤: {e}')
    
    @validator('purpose')
    def validate_purpose(cls, v):
        if v and len(v) > 100:
            raise ValueError('占卜目的不能超過 100 字符')
        return v or "指定時間占卜"

class TimeDivinationResponse(BaseModel):
    """指定時間占卜回應模型"""
    success: bool
    divination_id: Optional[str] = None
    target_time: str
    current_time: str
    gender: str
    taichi_palace: str
    minute_dizhi: str
    palace_tiangan: str
    sihua_results: list
    purpose: str
    message: str
    error: Optional[str] = None
    
    class Config:
        # 允許任意類型（為了兼容性）
        arbitrary_types_allowed = True
        # JSON 序列化配置
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TimeDivinationService:
    """統一的指定時間占卜服務"""
    
    @staticmethod
    def parse_line_bot_data(data: str) -> Tuple[str, str]:
        """
        解析 LINE Bot 回調數據
        
        Args:
            data: 原始回調數據，格式如 "time_gender=M&time=2025-07-28T19:32"
            
        Returns:
            Tuple[str, str]: (gender, time_value)
            
        Raises:
            ValueError: 解析失敗時拋出
        """
        try:
            logger.info(f"🔍 開始解析 LINE Bot 數據: {data}")
            
            # 移除前綴
            if "time_gender=" in data:
                parts = data.replace("time_gender=", "")
            else:
                # 容錯處理：嘗試其他可能的格式
                parts = data.split("=", 1)[1] if "=" in data else data
            
            logger.info(f"移除前綴後: {parts}")
            
            # 分割性別和時間
            if "&time=" in parts:
                gender_and_time = parts.split("&time=", 1)
                gender = gender_and_time[0].strip()
                time_value = gender_and_time[1].strip() if len(gender_and_time) > 1 else "now"
            else:
                # 如果沒有時間部分，默認使用當前時間
                gender = parts.strip()
                time_value = "now"
            
            logger.info(f"✅ 解析結果 - 性別: {gender}, 時間: {time_value}")
            
            # 驗證性別
            if gender not in ['M', 'F']:
                raise ValueError(f"無效的性別值: {gender}")
            
            return gender, time_value
            
        except Exception as e:
            logger.error(f"❌ LINE Bot 數據解析失敗: {e}")
            raise ValueError(f"數據格式錯誤: {e}")
    
    @staticmethod
    def validate_user_permission(user: LineBotUser, db: Session) -> bool:
        """
        驗證用戶是否有權限使用指定時間占卜
        
        Args:
            user: 用戶對象
            db: 數據庫會話
            
        Returns:
            bool: 是否有權限
        """
        try:
            user_stats = permission_manager.get_user_stats(db, user)
            is_admin = user_stats["user_info"]["is_admin"]
            
            logger.info(f"用戶權限檢查 - 管理員: {is_admin}")
            return is_admin
            
        except Exception as e:
            logger.error(f"權限檢查失敗: {e}")
            return False
    
    @staticmethod
    def execute_time_divination(
        user: LineBotUser,
        gender: str,
        target_time: str,
        db: Session,
        purpose: str = "指定時間占卜"
    ) -> TimeDivinationResponse:
        """
        執行指定時間占卜
        
        Args:
            user: 用戶對象
            gender: 性別 (M/F)
            target_time: 目標時間字符串
            db: 數據庫會話
            purpose: 占卜目的
            
        Returns:
            TimeDivinationResponse: 占卜結果
        """
        try:
            logger.info(f"🎯 開始執行指定時間占卜 - 用戶: {user.line_user_id}, 性別: {gender}, 時間: {target_time}")
            
            # 1. 驗證權限
            if not TimeDivinationService.validate_user_permission(user, db):
                return TimeDivinationResponse(
                    success=False,
                    target_time=target_time,
                    current_time=TimezoneHelper.get_current_taipei_time().isoformat(),
                    gender=gender,
                    taichi_palace="",
                    minute_dizhi="",
                    palace_tiangan="",
                    sihua_results=[],
                    purpose=purpose,
                    message="權限不足",
                    error="指定時間占卜功能僅限管理員使用"
                )
            
            # 2. 解析目標時間
            if target_time.lower() == "now":
                parsed_time = TimezoneHelper.get_current_taipei_time()
                logger.info(f"使用當前時間: {parsed_time}")
            else:
                parsed_time = TimezoneHelper.to_taipei_time(target_time)
                logger.info(f"✅ 解析指定時間成功: {parsed_time}")
            
            # 3. 執行占卜
            divination_result = get_divination_result(db, user, gender, parsed_time)
            
            if not divination_result.get('success'):
                error_msg = divination_result.get('error', '占卜失敗')
                logger.error(f"占卜執行失敗: {error_msg}")
                
                return TimeDivinationResponse(
                    success=False,
                    target_time=target_time,
                    current_time=TimezoneHelper.get_current_taipei_time().isoformat(),
                    gender=gender,
                    taichi_palace="",
                    minute_dizhi="",
                    palace_tiangan="",
                    sihua_results=[],
                    purpose=purpose,
                    message="占卜失敗",
                    error=error_msg
                )
            
            # 4. 構建成功回應
            response = TimeDivinationResponse(
                success=True,
                divination_id=str(divination_result.get("divination_id", "")),
                target_time=parsed_time.isoformat(),
                current_time=TimezoneHelper.get_current_taipei_time().isoformat(),
                gender=gender,
                taichi_palace=divination_result["taichi_palace"],
                minute_dizhi=divination_result["minute_dizhi"],
                palace_tiangan=divination_result["palace_tiangan"],
                sihua_results=divination_result["sihua_results"],
                purpose=purpose,
                message="指定時間占卜完成"
            )
            
            logger.info(f"✅ 指定時間占卜完成 - ID: {response.divination_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ 執行指定時間占卜失敗: {e}", exc_info=True)
            
            return TimeDivinationResponse(
                success=False,
                target_time=target_time,
                current_time=TimezoneHelper.get_current_taipei_time().isoformat(),
                gender=gender,
                taichi_palace="",
                minute_dizhi="",
                palace_tiangan="",
                sihua_results=[],
                purpose=purpose,
                message="占卜過程發生錯誤",
                error=str(e)
            )

# 導出
__all__ = [
    "TimeDivinationService", 
    "TimeDivinationRequest", 
    "TimeDivinationResponse"
] 