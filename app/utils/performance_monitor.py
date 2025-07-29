"""
性能監控工具
監控占卜服務的性能指標
"""
import time
import logging
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """性能指標數據"""
    function_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        """執行時間（毫秒）"""
        return self.duration * 1000

class PerformanceMonitor:
    """性能監控器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.function_stats: Dict[str, List[float]] = defaultdict(list)
    
    def record_metric(self, metric: PerformanceMetric):
        """記錄性能指標"""
        self.metrics.append(metric)
        if metric.success:
            self.function_stats[metric.function_name].append(metric.duration)
        
        # 記錄到日誌（如果執行時間過長）
        if metric.duration > 2.0:  # 超過 2 秒
            logger.warning(f"慢查詢警告 - {metric.function_name}: {metric.duration_ms:.2f}ms")
        elif metric.duration > 5.0:  # 超過 5 秒
            logger.error(f"超慢查詢 - {metric.function_name}: {metric.duration_ms:.2f}ms")
    
    def get_function_stats(self, function_name: str) -> Dict[str, float]:
        """獲取函數統計信息"""
        durations = self.function_stats.get(function_name, [])
        if not durations:
            return {}
        
        return {
            "count": len(durations),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """獲取所有函數的統計信息"""
        return {
            func_name: self.get_function_stats(func_name)
            for func_name in self.function_stats.keys()
        }
    
    def clear_metrics(self):
        """清空指標數據"""
        self.metrics.clear()
        self.function_stats.clear()
        logger.info("性能指標已清空")

# 全局監控器實例
performance_monitor = PerformanceMonitor()

def monitor_performance(function_name: Optional[str] = None):
    """性能監控裝飾器"""
    def decorator(func):
        func_name = function_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                metric = PerformanceMetric(
                    function_name=func_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    success=success,
                    error=error
                )
                
                performance_monitor.record_metric(metric)
                
                # 記錄執行時間
                logger.info(f"⏱️ {func_name} 執行時間: {duration * 1000:.2f}ms")
        
        return wrapper
    return decorator

def monitor_async_performance(function_name: Optional[str] = None):
    """異步函數性能監控裝飾器"""
    def decorator(func):
        func_name = function_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                metric = PerformanceMetric(
                    function_name=func_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    success=success,
                    error=error
                )
                
                performance_monitor.record_metric(metric)
                
                # 記錄執行時間
                logger.info(f"⏱️ {func_name} 執行時間: {duration * 1000:.2f}ms")
        
        return wrapper
    return decorator

# 便捷的上下文管理器
class PerformanceTimer:
    """性能計時器上下文管理器"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"🚀 開始 {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        
        metric = PerformanceMetric(
            function_name=self.operation_name,
            start_time=self.start_time,
            end_time=self.end_time,
            duration=duration,
            success=success,
            error=error
        )
        
        performance_monitor.record_metric(metric)
        
        if success:
            logger.info(f"✅ {self.operation_name} 完成，耗時: {duration * 1000:.2f}ms")
        else:
            logger.error(f"❌ {self.operation_name} 失敗，耗時: {duration * 1000:.2f}ms, 錯誤: {error}")

# 導出
__all__ = [
    "PerformanceMetric",
    "PerformanceMonitor", 
    "performance_monitor",
    "monitor_performance",
    "monitor_async_performance",
    "PerformanceTimer"
] 