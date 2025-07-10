"""
動態 Rich Menu 管理器
根據用戶狀態和權限動態設置合適的 Rich Menu
"""
import logging
from typing import Optional, Dict, Any
from app.utils.rich_menu_manager import (
    rich_menu_manager, 
    determine_user_level, 
    get_default_tab_for_user_level
)
from app.utils.driver_view_rich_menu_handler import DriverViewRichMenuHandler
from app.logic.permission_manager import permission_manager
from app.db.database import get_db

logger = logging.getLogger(__name__)

class DynamicRichMenuManager:
    """動態 Rich Menu 管理器"""
    
    def __init__(self):
        self.use_driver_view_menu = True  # 使用駕駛視窗選單
        self.driver_handler = DriverViewRichMenuHandler()
    
    def initialize_user_menu(self, user_id: str, user_permissions: Optional[Dict[str, Any]] = None) -> bool:
        """
        初始化用戶的 Rich Menu
        
        Args:
            user_id: LINE 用戶 ID
            user_permissions: 用戶權限資訊（可選，如果未提供會自動獲取）
            
        Returns:
            bool: 是否成功初始化
        """
        try:
            # 獲取用戶權限
            if user_permissions is None:
                with get_db() as db:
                    from app.models.linebot_user import LineBotUser
                    user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
                    if user:
                        user_permissions = permission_manager.get_user_stats(db, user)
                    else:
                        logger.warning(f"用戶 {user_id} 不存在於數據庫中")
                        return False
            
            if self.use_driver_view_menu:
                return self._initialize_driver_view_menu(user_id, user_permissions)
            else:
                return self._initialize_legacy_menu(user_id, user_permissions)
                
        except Exception as e:
            logger.error(f"初始化用戶 {user_id} 選單失敗: {e}")
            return False
    
    def _initialize_driver_view_menu(self, user_id: str, user_permissions: Dict[str, Any]) -> bool:
        """初始化駕駛視窗選單"""
        try:
            # 確定用戶等級
            user_level = determine_user_level(user_permissions)
            
            # 根據用戶等級選擇預設分頁
            if user_level == "admin":
                default_tab = "advanced"
            elif user_level == "premium":
                default_tab = "fortune"
            else:
                default_tab = "basic"
            
            # 設置駕駛視窗選單
            success = self.driver_handler.setup_default_tab(user_id, default_tab)
            
            if success:
                logger.info(f"✅ 用戶 {user_id} 駕駛視窗選單初始化成功 - 等級: {user_level}, 分頁: {default_tab}")
            else:
                logger.error(f"❌ 用戶 {user_id} 駕駛視窗選單初始化失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"初始化用戶 {user_id} 駕駛視窗選單失敗: {e}")
            return False
    
    def _initialize_legacy_menu(self, user_id: str, user_permissions: Dict[str, Any]) -> bool:
        """初始化傳統選單"""
        try:
            is_admin = user_permissions.get("is_admin", False)
            success = rich_menu_manager.set_user_menu_by_role(user_id, is_admin)
            
            if success:
                menu_type = "管理員" if is_admin else "一般用戶"
                logger.info(f"✅ 用戶 {user_id} 傳統選單初始化成功 - 類型: {menu_type}")
            else:
                logger.error(f"❌ 用戶 {user_id} 傳統選單初始化失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"初始化用戶 {user_id} 傳統選單失敗: {e}")
            return False
    
    def handle_tab_switch_request(self, user_id: str, target_tab: str) -> bool:
        """
        處理分頁切換請求
        
        Args:
            user_id: LINE 用戶 ID
            target_tab: 目標分頁 ("basic", "fortune", "advanced")
            
        Returns:
            bool: 是否成功切換
        """
        try:
            # 獲取用戶權限
            db = None
            try:
                from app.db.database import get_db
                from app.models.linebot_models import LineBotUser
                from sqlalchemy.orm import sessionmaker
                from sqlalchemy import create_engine
                from app.config.database_config import DatabaseConfig
                
                # 創建數據庫會話
                database_url = DatabaseConfig.get_database_url()
                engine = create_engine(database_url)
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                db = SessionLocal()
                
                user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
                if not user:
                    logger.warning(f"用戶 {user_id} 不存在於數據庫中")
                    return False
                
                user_permissions = permission_manager.get_user_stats(db, user)
                user_level = determine_user_level(user_permissions)
                
            except Exception as db_error:
                logger.warning(f"數據庫連接失敗，使用預設權限: {db_error}")
                # 如果數據庫連接失敗，使用預設權限
                user_level = "free"
            finally:
                if db:
                    db.close()
            
            # 檢查權限 - 駕駛視窗的分頁權限檢查
            available_tabs = self.driver_handler.list_available_tabs()
            if target_tab not in available_tabs:
                logger.warning(f"無效的分頁: {target_tab}")
                return False
            
            # 簡單的權限檢查
            if target_tab == "advanced" and user_level != "admin":
                logger.warning(f"用戶 {user_id} (等級: {user_level}) 無權限訪問進階分頁")
                return False
            
            # 執行切換 - 使用駕駛視窗處理器
            success = self.driver_handler.switch_to_tab(user_id, target_tab)
            
            if success:
                logger.info(f"✅ 用戶 {user_id} 成功切換到分頁: {target_tab}")
            else:
                logger.error(f"❌ 用戶 {user_id} 切換到分頁 {target_tab} 失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"處理用戶 {user_id} 分頁切換請求失敗: {e}")
            return False
    
    def get_user_menu_info(self, user_id: str) -> Dict[str, Any]:
        """
        獲取用戶選單資訊
        
        Args:
            user_id: LINE 用戶 ID
            
        Returns:
            Dict: 用戶選單資訊
        """
        try:
            # 獲取用戶權限
            with get_db() as db:
                from app.models.linebot_models import LineBotUser
                user = db.query(LineBotUser).filter(LineBotUser.line_user_id == user_id).first()
                if not user:
                    return {"error": "用戶不存在"}
                
                user_permissions = permission_manager.get_user_stats(db, user)
                user_level = determine_user_level(user_permissions)
            
            # 獲取當前分頁
            current_tab = rich_menu_manager.get_user_current_tab(user_id)
            
            # 獲取可訪問的分頁
            available_tabs = []
            for tab in ["basic", "fortune", "admin"]:
                if rich_menu_manager.can_access_tab(tab, user_level):
                    available_tabs.append(tab)
            
            return {
                "user_level": user_level,
                "current_tab": current_tab,
                "available_tabs": available_tabs,
                "is_tabbed_menu": self.use_driver_view_menu
            }
            
        except Exception as e:
            logger.error(f"獲取用戶 {user_id} 選單資訊失敗: {e}")
            return {"error": str(e)}
    
    def refresh_user_menu(self, user_id: str) -> bool:
        """
        刷新用戶選單（當用戶權限變更時使用）
        
        Args:
            user_id: LINE 用戶 ID
            
        Returns:
            bool: 是否成功刷新
        """
        try:
            # 重新初始化選單
            return self.initialize_user_menu(user_id)
            
        except Exception as e:
            logger.error(f"刷新用戶 {user_id} 選單失敗: {e}")
            return False
    
    def handle_follow_event(self, user_id: str) -> bool:
        """
        處理用戶關注事件
        
        Args:
            user_id: LINE 用戶 ID
            
        Returns:
            bool: 是否成功處理
        """
        try:
            logger.info(f"處理用戶 {user_id} 關注事件")
            
            # 初始化用戶選單
            success = self.initialize_user_menu(user_id)
            
            if success:
                logger.info(f"✅ 用戶 {user_id} 關注事件處理成功")
            else:
                logger.error(f"❌ 用戶 {user_id} 關注事件處理失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"處理用戶 {user_id} 關注事件失敗: {e}")
            return False
    
    def set_use_tabbed_menu(self, use_tabbed: bool):
        """
        設置是否使用分頁式選單
        
        Args:
            use_tabbed: 是否使用分頁式選單
        """
        self.use_driver_view_menu = use_tabbed
        logger.info(f"設置選單模式: {'駕駛視窗' if use_tabbed else '傳統'}")

# 全局實例
dynamic_rich_menu_manager = DynamicRichMenuManager()

def initialize_user_menu(user_id: str, user_permissions: Optional[Dict[str, Any]] = None) -> bool:
    """
    初始化用戶選單的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        user_permissions: 用戶權限資訊（可選）
        
    Returns:
        bool: 是否成功初始化
    """
    return dynamic_rich_menu_manager.initialize_user_menu(user_id, user_permissions)

def handle_tab_switch_request(user_id: str, target_tab: str) -> bool:
    """
    處理分頁切換請求的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        target_tab: 目標分頁 ("basic", "fortune", "admin")
        
    Returns:
        bool: 是否成功切換
    """
    return dynamic_rich_menu_manager.handle_tab_switch_request(user_id, target_tab)

def refresh_user_menu(user_id: str) -> bool:
    """
    刷新用戶選單的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        
    Returns:
        bool: 是否成功刷新
    """
    return dynamic_rich_menu_manager.refresh_user_menu(user_id)

def handle_follow_event(user_id: str) -> bool:
    """
    處理用戶關注事件的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        
    Returns:
        bool: 是否成功處理
    """
    return dynamic_rich_menu_manager.handle_follow_event(user_id)

def get_user_menu_info(user_id: str) -> Dict[str, Any]:
    """
    獲取用戶選單資訊的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        
    Returns:
        Dict: 用戶選單資訊
    """
    return dynamic_rich_menu_manager.get_user_menu_info(user_id)

# 導出
__all__ = [
    "DynamicRichMenuManager",
    "dynamic_rich_menu_manager",
    "initialize_user_menu",
    "handle_tab_switch_request",
    "refresh_user_menu",
    "handle_follow_event",
    "get_user_menu_info"
] 