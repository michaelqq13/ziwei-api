"""
駕駛視窗 Rich Menu 管理器
整合駕駛視窗選單到 LINE Bot 系統
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple

from app.utils.driver_view_rich_menu_handler import driver_view_handler
from app.utils.rich_menu_manager import RichMenuManager

logger = logging.getLogger(__name__)

class DriveViewRichMenuManager:
    """駕駛視窗 Rich Menu 管理器"""
    
    def __init__(self):
        self.handler = driver_view_handler  # 使用全局處理器實例
        self.rich_menu_manager = RichMenuManager()
        self.menu_cache = {}  # 緩存 Rich Menu ID
        
        # 分頁權限設定
        self.tab_permissions = {
            "basic": ["user", "premium", "admin"],  # 基本功能 - 所有人
            "fortune": ["premium", "admin"],        # 運勢 - 付費會員和管理員
            "advanced": ["admin"]                   # 進階功能 - 僅管理員
        }
    
    def get_user_available_tabs(self, user_level: str) -> List[str]:
        """
        根據用戶等級獲取可用的分頁
        
        Args:
            user_level: 用戶等級 ("user", "premium", "admin")
            
        Returns:
            List[str]: 可用的分頁列表
        """
        available_tabs = []
        for tab, allowed_levels in self.tab_permissions.items():
            if user_level in allowed_levels:
                available_tabs.append(tab)
        return available_tabs
    
    def create_and_upload_menu(self, tab: str) -> Optional[str]:
        """
        創建並上傳駕駛視窗選單
        
        Args:
            tab: 分頁名稱 ("basic", "fortune", "advanced")
            
        Returns:
            Optional[str]: Rich Menu ID，失敗時返回 None
        """
        try:
            # 檢查緩存
            cache_key = f"drive_view_{tab}"
            if cache_key in self.menu_cache:
                logger.info(f"✅ 使用緩存的 Rich Menu: {cache_key}")
                return self.menu_cache[cache_key]
            
            # 生成選單圖片和配置
            image_path, button_areas = self.handler.create_tabbed_rich_menu(tab, "user")
            if not image_path or not os.path.exists(image_path):
                logger.error(f"❌ 選單圖片生成失敗: {tab}")
                return None
            
            # 創建 Rich Menu 配置
            tab_display_names = {
                "basic": "基本功能",
                "fortune": "運勢",
                "advanced": "進階功能"
            }
            
            rich_menu_config = {
                "size": {
                    "width": 2500,   # LINE Rich Menu 標準寬度
                    "height": 1686   # LINE Rich Menu 標準高度
                },
                "selected": True,
                "name": f"DriveView_{tab}",
                "chatBarText": f"🚗 {tab_display_names.get(tab, tab)}",
                "areas": button_areas
            }
            
            # 轉換按鈕區域格式
            for area in button_areas:
                bounds = area["bounds"]
                action = area["action"]
                rich_menu_config["areas"].append({
                    "bounds": {
                        "x": bounds["x"],
                        "y": bounds["y"],
                        "width": bounds["width"],
                        "height": bounds["height"]
                    },
                    "action": action
                })
            
            # 上傳到 LINE
            rich_menu_id = self.rich_menu_manager.create_rich_menu(rich_menu_config)
            if not rich_menu_id:
                logger.error(f"❌ 創建 Rich Menu 失敗: {tab}")
                return None
            
            # 上傳圖片
            upload_success = self.rich_menu_manager.upload_rich_menu_image(rich_menu_id, image_path)
            if not upload_success:
                logger.error(f"❌ 上傳 Rich Menu 圖片失敗: {tab}")
                # 刪除創建的 Rich Menu
                self.rich_menu_manager.delete_rich_menu(rich_menu_id)
                return None
            
            # 緩存 Rich Menu ID
            self.menu_cache[cache_key] = rich_menu_id
            logger.info(f"✅ 駕駛視窗選單創建成功: {tab} -> {rich_menu_id}")
            
            return rich_menu_id
            
        except Exception as e:
            logger.error(f"❌ 創建駕駛視窗選單失敗: {e}")
            return None
    
    def set_user_menu(self, user_id: str, user_level: str, preferred_tab: str = "basic") -> bool:
        """
        為用戶設定駕駛視窗選單
        
        Args:
            user_id: 用戶 ID
            user_level: 用戶等級
            preferred_tab: 偏好的分頁
            
        Returns:
            bool: 是否設定成功
        """
        try:
            # 檢查用戶權限
            available_tabs = self.get_user_available_tabs(user_level)
            if not available_tabs:
                logger.warning(f"⚠️ 用戶無可用分頁: {user_id} ({user_level})")
                return False
            
            # 選擇分頁
            if preferred_tab in available_tabs:
                selected_tab = preferred_tab
            else:
                selected_tab = available_tabs[0]  # 預設使用第一個可用分頁
            
            # 創建選單
            rich_menu_id = self.create_and_upload_menu(selected_tab)
            if not rich_menu_id:
                return False
            
            # 設定到用戶
            success = self.rich_menu_manager.set_user_rich_menu(user_id, rich_menu_id)
            if success:
                logger.info(f"✅ 用戶選單設定成功: {user_id} -> {selected_tab}")
            else:
                logger.error(f"❌ 用戶選單設定失敗: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 設定用戶選單失敗: {e}")
            return False
    
    def switch_user_tab(self, user_id: str, user_level: str, target_tab: str) -> bool:
        """
        切換用戶的分頁
        
        Args:
            user_id: 用戶 ID
            user_level: 用戶等級
            target_tab: 目標分頁
            
        Returns:
            bool: 是否切換成功
        """
        try:
            # 檢查權限
            available_tabs = self.get_user_available_tabs(user_level)
            if target_tab not in available_tabs:
                logger.warning(f"⚠️ 用戶無權限訪問分頁: {user_id} -> {target_tab}")
                return False
            
            # 創建選單
            rich_menu_id = self.create_and_upload_menu(target_tab)
            if not rich_menu_id:
                return False
            
            # 切換選單
            success = self.rich_menu_manager.set_user_rich_menu(user_id, rich_menu_id)
            if success:
                logger.info(f"✅ 分頁切換成功: {user_id} -> {target_tab}")
            else:
                logger.error(f"❌ 分頁切換失敗: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 切換分頁失敗: {e}")
            return False
    
    def cleanup_old_menus(self):
        """清理舊的駕駛視窗選單"""
        try:
            all_menus = self.rich_menu_manager.get_rich_menu_list()
            if not all_menus:
                logger.info("🧹 沒有找到任何 Rich Menu")
                return
                
            drive_view_menus = [menu for menu in all_menus if menu.get('name', '').startswith('DriveView_')]
            
            logger.info(f"🧹 找到 {len(drive_view_menus)} 個駕駛視窗選單，開始清理...")
            
            for menu in drive_view_menus:
                menu_id = menu.get('richMenuId')
                if menu_id and menu_id not in self.menu_cache.values():
                    success = self.rich_menu_manager.delete_rich_menu(menu_id)
                    if success:
                        logger.info(f"✅ 刪除舊選單: {menu_id}")
                    else:
                        logger.warning(f"⚠️ 刪除選單失敗: {menu_id}")
            
        except Exception as e:
            logger.error(f"❌ 清理舊選單失敗: {e}")
    
    def setup_all_menus(self) -> Dict[str, str]:
        """
        預先創建所有駕駛視窗選單
        
        Returns:
            Dict[str, str]: {分頁名稱: Rich Menu ID}
        """
        tabs = ["basic", "fortune", "advanced"]
        menu_ids = {}
        
        for tab in tabs:
            menu_id = self.create_and_upload_menu(tab)
            if menu_id:
                menu_ids[tab] = menu_id
            else:
                logger.error(f"❌ 創建選單失敗: {tab}")
        
        return menu_ids
    
    def get_tab_info(self, tab: str) -> Dict:
        """
        獲取分頁資訊
        
        Args:
            tab: 分頁名稱 ("basic", "fortune", "advanced")
            
        Returns:
            Dict: 分頁資訊
        """
        return self.handler.get_tab_info(tab)
    
    def get_rich_menu_config(self, active_tab: str = "basic") -> Tuple[Dict, str]:
        """
        獲取 Rich Menu 配置和圖片路徑
        
        Args:
            active_tab: 活躍的分頁
            
        Returns:
            Tuple[Dict, str]: (Rich Menu 配置, 圖片路徑)
        """
        image_path, button_areas = self.handler.create_tabbed_rich_menu(active_tab, "user")
        
        if not image_path:
            logger.error(f"❌ 獲取選單配置失敗: {active_tab}")
            return {}, ""
        
        rich_menu_config = {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": True,
            "name": f"DriveView_{active_tab}",
            "chatBarText": f"🚗 駕駛視窗",
            "areas": button_areas
        }
        
        return rich_menu_config, image_path

# 創建實例
drive_view_manager = DriveViewRichMenuManager()

def setup_drive_view_menus():
    """設定駕駛視窗選單"""
    return drive_view_manager.setup_all_menus()

def set_user_drive_view_menu(user_id: str, user_level: str, preferred_tab: str = "basic"):
    """為用戶設定駕駛視窗選單"""
    return drive_view_manager.set_user_menu(user_id, user_level, preferred_tab)

def switch_drive_view_tab(user_id: str, user_level: str, target_tab: str):
    """切換駕駛視窗分頁"""
    return drive_view_manager.switch_user_tab(user_id, user_level, target_tab) 