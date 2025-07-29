"""
時區處理工具
統一處理時間解析和時區轉換
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Union

logger = logging.getLogger(__name__)

# 台北時區
TAIPEI_TZ = timezone(timedelta(hours=8))

class TimezoneHelper:
    """統一的時區處理工具"""
    
    @staticmethod
    def to_taipei_time(dt: Union[datetime, str]) -> datetime:
        """
        將任意時間轉換為台北時間
        
        Args:
            dt: 可以是 datetime 對象或 ISO 格式字符串
            
        Returns:
            datetime: 台北時區的 datetime 對象
        """
        try:
            # 如果是字符串，先解析
            if isinstance(dt, str):
                dt = TimezoneHelper.parse_datetime_string(dt)
            
            # 如果沒有時區信息，假設為台北時間（LINE Datetime Picker 默認使用用戶本地時間）
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TAIPEI_TZ)
                logger.info(f"無時區信息的時間，假設為台北時間：{dt}")
            else:
                # 如果有時區信息，轉換為台北時間
                taipei_time = dt.astimezone(TAIPEI_TZ)
                logger.info(f"時區轉換：{dt} → {taipei_time}")
                dt = taipei_time
            
            return dt
            
        except Exception as e:
            logger.error(f"時區轉換失敗: {e}")
            raise ValueError(f"無法轉換時間到台北時區: {e}")
    
    @staticmethod
    def parse_datetime_string(time_str: str) -> datetime:
        """
        統一的時間字符串解析
        支持多種格式
        
        Args:
            time_str: 時間字符串
            
        Returns:
            datetime: 解析後的 datetime 對象
        """
        try:
            # 移除可能的空白字符
            time_str = time_str.strip()
            logger.info(f"開始解析時間字符串: {time_str}")
            
            # 支持的格式列表（按優先級排序）
            formats = [
                "%Y-%m-%dT%H:%M",           # ISO 8601 基本格式: 2025-07-28T19:32
                "%Y-%m-%dT%H:%M:%S",        # ISO 8601 含秒: 2025-07-28T19:32:00
                "%Y-%m-%d %H:%M",           # 標準格式: 2025-07-28 19:32
                "%Y-%m-%d %H:%M:%S",        # 標準格式含秒: 2025-07-28 19:32:00
                "%Y/%m/%d %H:%M",           # 斜線格式: 2025/07/28 19:32
                "%Y/%m/%d %H:%M:%S",        # 斜線格式含秒: 2025/07/28 19:32:00
            ]
            
            # 嘗試各種格式
            for fmt in formats:
                try:
                    parsed_time = datetime.strptime(time_str, fmt)
                    logger.info(f"✅ 成功解析時間: {time_str} → {parsed_time} (格式: {fmt})")
                    return parsed_time
                except ValueError:
                    continue
            
            # 嘗試 ISO format 方法
            try:
                # 處理 Z 結尾的 UTC 時間
                if time_str.endswith('Z'):
                    time_str = time_str.replace('Z', '+00:00')
                
                parsed_time = datetime.fromisoformat(time_str)
                logger.info(f"✅ 使用 fromisoformat 解析成功: {parsed_time}")
                return parsed_time
                
            except ValueError:
                pass
            
            # 如果所有格式都失敗
            raise ValueError(f"不支持的時間格式: {time_str}")
            
        except Exception as e:
            logger.error(f"時間字符串解析失敗: {time_str}, 錯誤: {e}")
            raise ValueError(f"時間格式錯誤: {e}")
    
    @staticmethod
    def get_current_taipei_time() -> datetime:
        """獲取當前台北時間"""
        return datetime.now(TAIPEI_TZ)
    
    @staticmethod
    def format_taipei_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        格式化台北時間為字符串
        
        Args:
            dt: datetime 對象
            format_str: 格式字符串
            
        Returns:
            str: 格式化後的時間字符串
        """
        try:
            taipei_time = TimezoneHelper.to_taipei_time(dt)
            return taipei_time.strftime(format_str)
        except Exception as e:
            logger.error(f"時間格式化失敗: {e}")
            return str(dt)

# 導出
__all__ = ["TimezoneHelper", "TAIPEI_TZ"] 