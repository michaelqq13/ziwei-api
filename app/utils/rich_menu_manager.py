"""
Rich Menu 管理器
處理 LINE Bot Rich Menu 的 API 操作
"""
import os
import json
import requests
from typing import Optional, Dict, List, Any
import logging
from io import BytesIO

from app.config.linebot_config import LineBotConfig
from app.utils.image_based_rich_menu_generator import generate_image_based_rich_menu
# 移除此處的全域導入以解決循環依賴問題
# from app.utils.driver_view_rich_menu_handler import DriverViewRichMenuHandler

logger = logging.getLogger(__name__)

class RichMenuManager:
    """用於管理 LINE Rich Menu 的實用工具類"""

    def __init__(self):
        self.line_bot_api = LineBotConfig.get_line_bot_api()

    def create_rich_menu(self, rich_menu_config: Dict[str, Any]) -> Optional[str]:
        """
        根據提供的配置創建 Rich Menu
        
        Args:
            rich_menu_config: 包含 Rich Menu 屬性的字典
        
        Returns:
            str: 新創建的 Rich Menu ID，如果失敗則返回 None
        """
        try:
            areas = [
                RichMenuArea(
                    bounds=RichMenuBounds(
                        x=area['bounds']['x'],
                        y=area['bounds']['y'],
                        width=area['bounds']['width'],
                        height=area['bounds']['height']
                    ),
                    action=self._create_action(area['action'])
                ) for area in rich_menu_config['areas']
            ]
            
            rich_menu_to_create = RichMenuRequest(
                size=RichMenuSize(width=rich_menu_config['size']['width'], height=rich_menu_config['size']['height']),
                selected=rich_menu_config['selected'],
                name=rich_menu_config['name'],
                chat_bar_text=rich_menu_config['chatBarText'],
                areas=areas
            )
            
            rich_menu_id_response = self.line_bot_api.create_rich_menu(rich_menu_request=rich_menu_to_create)
            logger.info(f"✅ 成功創建 Rich Menu, ID: {rich_menu_id_response.rich_menu_id}")
            return rich_menu_id_response.rich_menu_id
        except LineBotApiError as e:
            logger.error(f"❌ 創建 Rich Menu 失敗: {e.status_code} {e.error.message}")
            return None

    def _create_action(self, action_config: Dict[str, str]) -> Any:
        """根據配置創建動作對象"""
        action_type = action_config.get('type')
        if action_type == 'postback':
            return PostbackAction(data=action_config['data'])
        elif action_type == 'uri':
            return URIAction(uri=action_config['uri'])
        elif action_type == 'message':
            return MessageAction(text=action_config['text'])
        # 可以根據需要添加更多動作類型
        return None

    def delete_rich_menu(self, rich_menu_id: str) -> bool:
        """刪除指定的 Rich Menu"""
        try:
            self.line_bot_api.delete_rich_menu(rich_menu_id)
            logger.info(f"✅ 成功刪除 Rich Menu, ID: {rich_menu_id}")
            return True
        except LineBotApiError as e:
            logger.error(f"❌ 刪除 Rich Menu 失敗, ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            return False

    def get_rich_menu_list(self) -> List[Dict]:
        """獲取所有 Rich Menu 的列表"""
        try:
            rich_menu_list_response = self.line_bot_api.get_rich_menu_list()
            menus = [{
                "richMenuId": menu.rich_menu_id,
                "name": menu.name,
                "chatBarText": menu.chat_bar_text,
                "selected": menu.selected,
                "size": {"width": menu.size.width, "height": menu.size.height},
                "areas": len(menu.areas)
            } for menu in rich_menu_list_response]
            logger.info(f"✅ 成功獲取 Rich Menu 列表，共 {len(menus)} 個")
            return menus
        except LineBotApiError as e:
            logger.error(f"❌ 獲取 Rich Menu 列表失敗: {e.status_code} {e.error.message}")
            return []

    def upload_rich_menu_image(self, rich_menu_id: str, image_path: str) -> bool:
        """上傳 Rich Menu 圖片"""
        try:
            with open(image_path, 'rb') as f:
                self.line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)
            logger.info(f"✅ 成功上傳 Rich Menu 圖片: {rich_menu_id}")
            return True
        except LineBotApiError as e:
            logger.error(f"❌ 上傳 Rich Menu 圖片失敗, ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            return False
        except IOError as e:
            logger.error(f"❌ 讀取圖片檔案失敗: {image_path}, 錯誤: {e}")
            return False

    def set_user_rich_menu(self, user_id: str, rich_menu_id: str) -> bool:
        """為用戶設定 Rich Menu"""
        try:
            self.line_bot_api.link_rich_menu_id_to_user(user_id, rich_menu_id)
            logger.info(f"✅ 成功為用戶 {user_id} 設定 Rich Menu: {rich_menu_id}")
            return True
        except LineBotApiError as e:
            logger.error(f"❌ 為用戶設定 Rich Menu 失敗, 用戶ID: {user_id}, 選單ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            return False

    def set_default_rich_menu(self, rich_menu_id: str) -> bool:
        """設定預設的 Rich Menu"""
        try:
            self.line_bot_api.set_default_rich_menu(rich_menu_id)
            logger.info(f"✅ 成功設定預設 Rich Menu: {rich_menu_id}")
            return True
        except LineBotApiError as e:
            logger.error(f"❌ 設定預設 Rich Menu 失敗, ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            return False
    
    def get_rich_menu(self, rich_menu_id: str):
        """獲取指定的 Rich Menu"""
        try:
            return self.line_bot_api.get_rich_menu(rich_menu_id)
        except LineBotApiError as e:
            logger.error(f"獲取 Rich Menu 失敗, ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            raise

    def get_rich_menu_image(self, rich_menu_id: str):
        """下載 Rich Menu 圖片"""
        try:
            # 這只會檢查圖片是否存在，不會下載整個圖片內容
            content = self.line_bot_api.get_rich_menu_image(rich_menu_id)
            # 檢查 content 是否有 iter_content 方法，確認是有效的響應對象
            if hasattr(content, 'iter_content'):
                # 讀取一小部分來確認流是有效的，但不消耗整個流
                next(content.iter_content(1))
                return True
            return False
        except StopIteration:
            # 流是空的，但請求成功，代表圖片存在但可能為0字節
            return True
        except LineBotApiError as e:
            logger.warning(f"下載 Rich Menu 圖片失敗, ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            # 將 SDK 的異常轉化為 False，而不是讓它冒泡
            return False

def can_access_tab(tab_name: str, user_level: str) -> bool:
    """
    檢查用戶是否有權限訪問特定分頁
    
    Args:
        tab_name: 分頁名稱 ("basic", "fortune", "admin")
        user_level: 用戶等級 ("free", "premium", "admin")
        
    Returns:
        bool: 是否有權限訪問
    """
    if tab_name == "basic":
        # 基本功能分頁所有用戶都可以訪問
        return True
    elif tab_name == "fortune":
        # 運勢分頁所有用戶都可以訪問（功能內部會控制權限）
        return True
    elif tab_name == "admin":
        # 進階選項分頁只有管理員可以訪問
        return user_level == "admin"
    else:
        return False

def determine_user_level(user_permissions: Dict[str, Any]) -> str:
    """
    根據用戶權限確定用戶等級
    
    Args:
        user_permissions: 用戶權限資訊
        
    Returns:
        str: 用戶等級 ("free", "premium", "admin")
    """
    try:
        user_info = user_permissions.get("user_info", {})
        
        if user_info.get("is_admin", False):
            return "admin"
        
        membership_info = user_permissions.get("membership_info", {})
        is_premium = membership_info.get("is_premium", False)
        
        if is_premium:
            return "premium"
        else:
            return "free"
            
    except Exception as e:
        logger.error(f"確定用戶等級時發生錯誤: {e}")
        return "free"  # 預設為免費會員

def get_default_tab_for_user_level(user_level: str) -> str:
    """
    根據用戶等級獲取預設分頁
    
    Args:
        user_level: 用戶等級 ("free", "premium", "admin")
        
    Returns:
        str: 預設分頁名稱
    """
    if user_level == "admin":
        return "advanced"
    elif user_level == "premium":
        return "fortune"
    else:
        return "basic"

# 創建全局實例
rich_menu_manager = RichMenuManager()

def setup_rich_menu() -> Optional[str]:
    """
    設置預設的 Rich Menu
    
    Returns:
        str: Rich Menu ID (如果成功)
    """
    return rich_menu_manager.ensure_default_rich_menu()

def get_rich_menu_status() -> Dict[str, Any]:
    """
    獲取 Rich Menu 狀態資訊
    
    Returns:
        Dict: Rich Menu 狀態
    """
    try:
        default_id = rich_menu_manager.get_default_rich_menu_id()
        all_menus = rich_menu_manager.get_rich_menu_list()
        
        return {
            "default_menu_id": default_id,
            "total_menus": len(all_menus) if all_menus else 0,
            "menu_list": all_menus or []
        }
    except Exception as e:
        logger.error(f"獲取 Rich Menu 狀態失敗: {e}")
        return {"error": str(e)}

def update_user_rich_menu(user_id: str, is_admin: bool = False) -> bool:
    """
    更新用戶的 Rich Menu
    
    Args:
        user_id: LINE 用戶 ID
        is_admin: 是否為管理員
        
    Returns:
        bool: 是否成功更新
    """
    return rich_menu_manager.set_user_menu_by_role(user_id, is_admin)

# 導出
__all__ = [
    "RichMenuManager",
    "rich_menu_manager",
    "setup_rich_menu", 
    "setup_tabbed_rich_menu",
    "set_user_tabbed_menu",
    "get_user_current_tab",
    "get_rich_menu_status",
    "update_user_rich_menu",
    "determine_user_level",
    "get_default_tab_for_user_level",
    "switch_user_tab",
    "can_access_tab"
] 