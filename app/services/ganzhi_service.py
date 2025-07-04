"""
干支服務集成模塊
負責與干支查詢微服務的通信
"""
import httpx
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from app.utils.chinese_calendar import ChineseCalendar

logger = logging.getLogger(__name__)

class GanzhiService:
    """干支服務客戶端"""
    
    def __init__(self, service_url: str = None):
        """
        初始化干支服務客戶端
        
        Args:
            service_url: 干支服務的URL，如果為 None 則從環境變數讀取
        """
        if service_url is None:
            # 從環境變數讀取，支援 Railway 部署
            service_url = os.getenv('GANZHI_SERVICE_URL', 'http://127.0.0.1:8001')
        
        self.service_url = service_url.rstrip('/')
        self.timeout = 10.0  # 增加到10秒超時（Railway 部署時可能需要更長時間）
        
        logger.info(f"干支服務配置: {self.service_url}")
        
    async def get_ganzhi_info(
        self, 
        timestamp: str, 
        timezone_offset: int = 8
    ) -> Dict[str, Any]:
        """
        從微服務獲取干支信息
        
        Args:
            timestamp: 時間戳字符串
            timezone_offset: 時區偏移（小時）
            
        Returns:
            包含干支信息的字典
            
        Raises:
            Exception: 當服務調用失敗時
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.service_url}/ganzhi",
                    params={
                        "ts": timestamp,
                        "timezone_offset": timezone_offset
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("success"):
                    return result
                else:
                    raise Exception(f"服務返回錯誤: {result}")
                    
        except httpx.TimeoutException:
            logger.error(f"調用干支服務超時: {timestamp}")
            raise Exception("干支服務響應超時")
        except httpx.RequestError as e:
            logger.error(f"調用干支服務網絡錯誤: {e}")
            raise Exception(f"干支服務網絡錯誤: {str(e)}")
        except Exception as e:
            logger.error(f"調用干支服務失敗: {e}")
            raise
    
    async def get_ganzhi_with_fallback(
        self, 
        year: int, 
        month: int, 
        day: int, 
        hour: int, 
        minute: int = 0
    ) -> Dict[str, str]:
        """
        獲取干支信息，帶回退機制
        
        先嘗試調用微服務，失敗時回退到本地計算
        
        Args:
            year: 年
            month: 月
            day: 日
            hour: 時
            minute: 分（可選）
            
        Returns:
            包含年月日時分干支的字典
        """
        try:
            # 構建時間戳
            timestamp = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"
            
            # 嘗試調用微服務
            logger.info(f"調用干支微服務: {timestamp}")
            result = await self.get_ganzhi_info(timestamp)
            
            return {
                "year_ganzhi": result.get("year_ganzhi", ""),
                "month_ganzhi": result.get("month_ganzhi", ""),
                "day_ganzhi": result.get("day_ganzhi", ""),
                "hour_ganzhi": result.get("hour_ganzhi", ""),
                "minute_ganzhi": result.get("minute_ganzhi", ""),
                "data_source": result.get("data_source", "microservice")
            }
            
        except Exception as e:
            logger.warning(f"微服務調用失敗，回退到本地計算: {e}")
            return await self._fallback_calculate(year, month, day, hour, minute)
    
    async def _fallback_calculate(
        self, 
        year: int, 
        month: int, 
        day: int, 
        hour: int, 
        minute: int = 0
    ) -> Dict[str, str]:
        """
        回退到本地計算干支
        
        當微服務不可用時使用
        """
        try:
            # 使用現有的本地計算方法
            year_ganzhi = ChineseCalendar.get_year_ganzhi(year)
            month_ganzhi = ChineseCalendar.get_month_ganzhi(year, month)
            day_ganzhi = ChineseCalendar.get_day_ganzhi(year, month, day)
            
            # 獲取日干用於時干計算
            day_stem = day_ganzhi[0] if day_ganzhi else "甲"
            hour_ganzhi = ChineseCalendar.get_hour_ganzhi(hour, day_stem)
            
            # 計算分干支（簡化版）
            minute_branch = ChineseCalendar.get_minute_branch(hour, minute)
            minute_stem = ChineseCalendar.get_hour_stem(hour, day_stem)
            minute_ganzhi = minute_stem + minute_branch
            
            return {
                "year_ganzhi": year_ganzhi,
                "month_ganzhi": month_ganzhi,
                "day_ganzhi": day_ganzhi,
                "hour_ganzhi": hour_ganzhi,
                "minute_ganzhi": minute_ganzhi,
                "data_source": "local_fallback"
            }
            
        except Exception as e:
            logger.error(f"本地計算也失敗: {e}")
            # 返回預設值避免系統崩潰
            return {
                "year_ganzhi": "甲子",
                "month_ganzhi": "甲子", 
                "day_ganzhi": "甲子",
                "hour_ganzhi": "甲子",
                "minute_ganzhi": "甲子",
                "data_source": "default"
            }
    
    async def check_service_health(self) -> bool:
        """
        檢查微服務健康狀態
        
        Returns:
            True 如果服務正常，False 如果服務不可用
        """
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.service_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    async def get_service_info(self) -> Optional[Dict[str, Any]]:
        """
        獲取微服務信息
        
        Returns:
            服務信息字典，如果服務不可用則返回 None
        """
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.service_url}/")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"無法獲取服務信息: {e}")
            return None

# 全局實例
ganzhi_service = GanzhiService() 