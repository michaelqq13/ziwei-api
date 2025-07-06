"""
安全中間件模組
"""
import os
import logging
from fastapi import Request, HTTPException
from typing import List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """安全中間件類"""
    
    def __init__(self):
        # IP 白名單（LINE 官方 IP 範圍）
        self.line_ip_whitelist = [
            "147.92.150.0/24",
            "147.92.151.0/24", 
            "147.92.152.0/24",
            "147.92.153.0/24",
            "147.92.154.0/24",
            "147.92.155.0/24"
        ]
        
        # 管理員 IP 白名單
        admin_ips = os.getenv("ADMIN_IP_WHITELIST", "127.0.0.1,localhost").split(",")
        self.admin_ip_whitelist = [ip.strip() for ip in admin_ips if ip.strip()]
        
        # 可疑請求檢測
        self.suspicious_patterns = [
            "sql", "union", "select", "drop", "delete", "insert", "update",
            "script", "javascript", "onload", "onerror", "eval", "alert",
            "../", "..\\", "/etc/passwd", "/proc/", "cmd.exe", "powershell"
        ]
    
    def check_line_ip(self, client_ip: str) -> bool:
        """檢查是否為 LINE 官方 IP"""
        try:
            import ipaddress
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            for ip_range in self.line_ip_whitelist:
                if client_ip_obj in ipaddress.ip_network(ip_range):
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"IP 檢查失敗: {e}")
            return False
    
    def check_admin_ip(self, client_ip: str) -> bool:
        """檢查是否為管理員 IP"""
        return client_ip in self.admin_ip_whitelist or client_ip == "127.0.0.1"
    
    def detect_suspicious_request(self, request: Request) -> Optional[str]:
        """檢測可疑請求"""
        try:
            # 檢查 URL 路徑
            path = str(request.url.path).lower()
            for pattern in self.suspicious_patterns:
                if pattern in path:
                    return f"可疑路徑模式: {pattern}"
            
            # 檢查查詢參數
            query_params = str(request.url.query).lower()
            for pattern in self.suspicious_patterns:
                if pattern in query_params:
                    return f"可疑查詢參數: {pattern}"
            
            # 檢查 User-Agent
            user_agent = request.headers.get("user-agent", "").lower()
            suspicious_agents = ["bot", "crawler", "spider", "scan", "hack"]
            for agent in suspicious_agents:
                if agent in user_agent and "linebot" not in user_agent:
                    return f"可疑 User-Agent: {agent}"
            
            return None
            
        except Exception as e:
            logger.error(f"可疑請求檢測失敗: {e}")
            return None
    
    def log_request(self, request: Request, response_status: int = None):
        """記錄請求日誌"""
        try:
            client_ip = self.get_client_ip(request)
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "referer": request.headers.get("referer", ""),
                "response_status": response_status
            }
            
            # 記錄到日誌
            logger.info(f"API 請求: {json.dumps(log_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"請求日誌記錄失敗: {e}")
    
    def get_client_ip(self, request: Request) -> str:
        """獲取客戶端真實 IP"""
        # 檢查代理標頭
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 回退到直接連接 IP
        return request.client.host if request.client else "unknown"

# 全域安全中間件實例
security_middleware = SecurityMiddleware()

async def security_check_middleware(request: Request, call_next):
    """安全檢查中間件"""
    try:
        client_ip = security_middleware.get_client_ip(request)
        
        # 1. 檢測可疑請求
        suspicious_reason = security_middleware.detect_suspicious_request(request)
        if suspicious_reason:
            logger.warning(f"可疑請求被攔截 - IP: {client_ip}, 原因: {suspicious_reason}")
            raise HTTPException(status_code=403, detail="請求被拒絕")
        
        # 2. LINE Webhook 特殊檢查
        if request.url.path == "/webhook":
            # 生產環境應啟用 IP 白名單檢查
            if os.getenv("ENABLE_LINE_IP_CHECK", "false").lower() == "true":
                if not security_middleware.check_line_ip(client_ip):
                    logger.warning(f"非 LINE 官方 IP 嘗試訪問 webhook: {client_ip}")
                    raise HTTPException(status_code=403, detail="IP 不在白名單中")
        
        # 3. 管理員功能檢查
        if "/admin/" in request.url.path or "admin" in request.url.query:
            if not security_middleware.check_admin_ip(client_ip):
                logger.warning(f"非管理員 IP 嘗試訪問管理功能: {client_ip}")
                raise HTTPException(status_code=403, detail="管理員功能僅限特定 IP 訪問")
        
        # 處理請求
        response = await call_next(request)
        
        # 記錄請求日誌
        security_middleware.log_request(request, response.status_code)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"安全檢查中間件錯誤: {e}")
        # 不阻止請求，但記錄錯誤
        response = await call_next(request)
        return response 