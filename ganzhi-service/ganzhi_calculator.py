#!/usr/bin/env python3
"""
干支計算微服務 - 檔案模式
專門用於干支計算的獨立微服務，使用預先準備的完整干支資料檔案
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class GanzhiCalculator:
    """干支計算器 - 使用檔案資料模式"""
    
    def __init__(self):
        """初始化計算器"""
        self.data_file_path = Path("data/complete_ganzhi_data.json")
        self.ganzhi_data = None
        self._load_data()
    
    def _load_data(self):
        """載入干支資料檔案"""
        try:
            if self.data_file_path.exists():
                logger.info(f"載入干支資料檔案: {self.data_file_path}")
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    self.ganzhi_data = json.load(f)
                logger.info(f"成功載入 {len(self.ganzhi_data)} 筆干支資料")
            else:
                logger.error(f"干支資料檔案不存在: {self.data_file_path}")
                self.ganzhi_data = {}
        except Exception as e:
            logger.error(f"載入干支資料檔案失敗: {e}")
            self.ganzhi_data = {}
    
    def calculate_ganzhi(self, timestamp: int, timezone_offset: int = 8) -> Dict:
        """
        計算指定時間的干支信息
        
        Args:
            timestamp: Unix 時間戳
            timezone_offset: 時區偏移（小時），預設為 UTC+8
            
        Returns:
            包含干支信息的字典
        """
        try:
            # 創建時區對象
            local_tz = timezone(timedelta(hours=timezone_offset))
            
            # 將 UTC 時間戳轉換為本地時間
            utc_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            local_dt = utc_dt.astimezone(local_tz)
            
            # 格式化為查詢鍵（精確到小時）
            datetime_key = f"{local_dt.year}-{local_dt.month:02d}-{local_dt.day:02d} {local_dt.hour:02d}:00:00"
            
            logger.info(f"時間戳 {timestamp} -> UTC: {utc_dt} -> 本地時間: {local_dt} -> 查詢鍵: {datetime_key}")
            
            # 從檔案資料中查詢
            if self.ganzhi_data and datetime_key in self.ganzhi_data:
                result = self.ganzhi_data[datetime_key].copy()
                result["data_source"] = "file"
                logger.info(f"檔案查詢成功: {result}")
                return result
            else:
                logger.warning(f"檔案中未找到時間 {datetime_key} 的干支資料")
                
                # 返回錯誤信息
                return {
                    "year_ganzhi": "未知",
                    "month_ganzhi": "未知",
                    "day_ganzhi": "未知",
                    "hour_ganzhi": "未知",
                    "lunar_month": "未知",
                    "lunar_day": "未知",
                    "data_source": "error",
                    "error": f"未找到時間 {datetime_key} 的干支資料"
                }
                
        except Exception as e:
            logger.error(f"計算干支時發生錯誤: {e}")
            return {
                "year_ganzhi": "錯誤",
                "month_ganzhi": "錯誤", 
                "day_ganzhi": "錯誤",
                "hour_ganzhi": "錯誤",
                "lunar_month": "錯誤",
                "lunar_day": "錯誤",
                "data_source": "error",
                "error": str(e)
            }
    
    def get_service_info(self) -> Dict:
        """獲取服務信息"""
        return {
            "status": "healthy",
            "data_source": "file",
            "file_connected": self.data_file_path.exists(),
            "records_count": len(self.ganzhi_data) if self.ganzhi_data else 0,
            "data_file_path": str(self.data_file_path)
        } 