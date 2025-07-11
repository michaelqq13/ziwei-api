"""
Rich Menu 管理器
處理 LINE Bot Rich Menu 的 API 操作
"""
import os
import json
import requests
from typing import Optional, Dict, List, Any
import logging

from app.config.linebot_config import LineBotConfig
from app.utils.image_based_rich_menu_generator import generate_image_based_rich_menu
# 移除此處的全域導入以解決循環依賴問題
# from app.utils.driver_view_rich_menu_handler import DriverViewRichMenuHandler

logger = logging.getLogger(__name__)

class RichMenuManager:
    """Rich Menu 管理器"""
    
    def __init__(self, use_image_based: bool = False):
        """
        初始化 Rich Menu 管理器
        
        Args:
            use_image_based: 是否使用圖片資源型生成器（True）或程式生成器（False）
        """
        self.channel_access_token = LineBotConfig.CHANNEL_ACCESS_TOKEN
        self.base_url = "https://api.line.me/v2/bot"
        self.headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        # 分頁選單 ID 緩存
        self.rich_menu_cache = {}
        
        # 圖片生成方式設定
        self.use_image_based = use_image_based
    
    def create_rich_menu(self, menu_config: Dict) -> Optional[str]:
        """
        創建 Rich Menu
        
        Returns:
            str: Rich Menu ID (如果成功)
        """
        url = f"{self.base_url}/richmenu"
        
        try:
            response = requests.post(url, headers=self.headers, json=menu_config)
            response.raise_for_status()
            
            result = response.json()
            rich_menu_id = result.get("richMenuId")
            
            logger.info(f"成功創建 Rich Menu: {rich_menu_id}")
            return rich_menu_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"創建 Rich Menu 失敗: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"回應內容: {e.response.text}")
            return None
    
    def upload_rich_menu_image(self, rich_menu_id: str, image_path: str) -> bool:
        """
        上傳 Rich Menu 圖片
        
        Args:
            rich_menu_id: Rich Menu ID
            image_path: 圖片檔案路徑
            
        Returns:
            bool: 是否成功上傳
        """
        # 使用正確的圖片上傳API域名
        url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
        
        # 使用正確的headers，包含授權信息
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "image/png"
        }
        
        try:
            with open(image_path, 'rb') as image_file:
                response = requests.post(url, headers=headers, data=image_file)
                response.raise_for_status()
            
            logger.info(f"成功上傳 Rich Menu 圖片: {rich_menu_id}")
            return True
            
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            logger.error(f"上傳 Rich Menu 圖片失敗: {e}")
            return False
    
    def set_default_rich_menu(self, rich_menu_id: str) -> bool:
        """
        設定預設 Rich Menu
        
        Args:
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 是否成功設定
        """
        url = f"{self.base_url}/user/all/richmenu/{rich_menu_id}"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"成功設定預設 Rich Menu: {rich_menu_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"設定預設 Rich Menu 失敗: {e}")
            return False
    
    def get_rich_menu_list(self) -> Optional[List[Dict]]:
        """
        獲取 Rich Menu 列表
        
        Returns:
            List[Dict]: Rich Menu 列表
        """
        url = f"{self.base_url}/richmenu/list"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            rich_menus = result.get("richmenus", [])
            
            logger.info(f"成功獲取 Rich Menu 列表，共 {len(rich_menus)} 個")
            return rich_menus
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取 Rich Menu 列表失敗: {e}")
            return None
    
    def get_default_rich_menu_id(self) -> Optional[str]:
        """
        獲取目前預設的 Rich Menu ID
        
        Returns:
            str: 預設 Rich Menu ID
        """
        url = f"{self.base_url}/user/all/richmenu"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            return result.get("richMenuId")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取預設 Rich Menu 失敗: {e}")
            return None
    
    def delete_rich_menu(self, rich_menu_id: str) -> bool:
        """
        刪除 Rich Menu
        
        Args:
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 是否成功刪除
        """
        url = f"{self.base_url}/richmenu/{rich_menu_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"成功刪除 Rich Menu: {rich_menu_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"刪除 Rich Menu 失敗: {e}")
            return False
    
    def create_driver_view_menu_config(self) -> Dict:
        """
        創建駕駛視窗主題的 Rich Menu 配置
        
        Returns:
            Dict: Rich Menu 配置
        """
        # 使用延遲導入來避免循環依賴
        from app.utils.driver_view_rich_menu_handler import DriverViewRichMenuHandler
        
        # 使用駕駛視窗處理器
        handler = DriverViewRichMenuHandler()
        
        # 創建默認分頁的配置
        button_areas = handler.create_button_areas("basic")
        
        menu_config = {
            "size": {
                "width": LineBotConfig.RICH_MENU_WIDTH,
                "height": LineBotConfig.RICH_MENU_HEIGHT
            },
            "selected": True,
            "name": "DriverViewMenu",
            "chatBarText": "🚗 駕駛視窗紫微",
            "areas": button_areas
        }
        
        return menu_config
    
    def create_tabbed_menu_config(self, active_tab: str, user_level: str) -> Dict:
        """
        創建分頁式選單配置
        
        Args:
            active_tab: 當前活躍分頁 ("basic", "fortune", "admin")
            user_level: 用戶等級 ("free", "premium", "admin")
            
        Returns:
            Dict: 分頁式選單配置
        """
        # 生成圖片和按鈕區域
        # 替換starry相關的引用為driver_view
        handler = DriverViewRichMenuHandler()
        image_path, button_areas = handler.create_tabbed_rich_menu(active_tab, user_level)
        
        menu_config = {
            "size": {
                "width": LineBotConfig.RICH_MENU_WIDTH,
                "height": LineBotConfig.RICH_MENU_HEIGHT
            },
            "selected": True,
            "name": f"TabbedMenu_{active_tab}_{user_level}",
            "chatBarText": f"✨ 星空紫微 - {self._get_tab_display_name(active_tab)}",
            "areas": button_areas
        }
        
        return menu_config
    
    def _get_tab_display_name(self, tab_name: str) -> str:
        """獲取分頁顯示名稱"""
        tab_names = {
            "basic": "基本功能",
            "fortune": "運勢",
            "admin": "進階選項"
        }
        return tab_names.get(tab_name, tab_name)
    
    def setup_tabbed_rich_menu(self, active_tab: str, user_level: str, force_recreate: bool = False) -> Optional[str]:
        """
        設定分頁式 Rich Menu
        
        Args:
            active_tab: 當前活躍分頁 ("basic", "fortune", "admin")
            user_level: 用戶等級 ("free", "premium", "admin")
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 檢查是否需要重新創建
            cache_key = f"tabbed_{active_tab}_{user_level}"
            
            if not force_recreate and cache_key in self.rich_menu_cache:
                existing_id = self.rich_menu_cache[cache_key]
                # 檢查選單是否仍存在
                existing_menus = self.get_rich_menu_list()
                if existing_menus:
                    for menu in existing_menus:
                        if menu.get("richMenuId") == existing_id:
                            logger.info(f"使用現有分頁選單: {existing_id}")
                            return existing_id
                # 選單不存在，清除緩存
                del self.rich_menu_cache[cache_key]
            
            # 生成分頁選單
            # 替換starry相關的引用為driver_view
            handler = DriverViewRichMenuHandler()
            image_path, button_areas = handler.create_tabbed_rich_menu(active_tab, user_level)
            
            if not image_path or not os.path.exists(image_path):
                logger.error(f"分頁選單圖片生成失敗: {image_path}")
                return None
            
            # 創建 Rich Menu 配置
            rich_menu_config = {
                "size": {
                    "width": LineBotConfig.RICH_MENU_WIDTH,
                    "height": LineBotConfig.RICH_MENU_HEIGHT
                },
                "selected": True,
                "name": f"分頁選單-{active_tab}-{user_level}",
                "chatBarText": f"選單 ({active_tab})",
                "areas": button_areas
            }
            
            # 創建 Rich Menu
            rich_menu_id = self.create_rich_menu(rich_menu_config)
            if not rich_menu_id:
                logger.error("創建分頁選單失敗")
                return None
            
            # 上傳圖片
            if not self.upload_rich_menu_image(rich_menu_id, image_path):
                logger.error("上傳分頁選單圖片失敗")
                self.delete_rich_menu(rich_menu_id)
                return None
            
            # 更新緩存
            self.rich_menu_cache[cache_key] = rich_menu_id
            logger.info(f"✅ 分頁選單創建成功: {rich_menu_id}")
            return rich_menu_id
                
        except Exception as e:
            logger.error(f"設定分頁選單時發生錯誤: {e}")
            return None
    
    def setup_default_tabbed_rich_menu(self, user_level: str = "free", force_recreate: bool = False) -> Optional[str]:
        """
        設定默認分頁式 Rich Menu（基本功能分頁）
        
        Args:
            user_level: 用戶等級 ("free", "premium", "admin")
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        return self.setup_tabbed_rich_menu("basic", user_level, force_recreate)
    
    def set_user_tabbed_menu(self, user_id: str, active_tab: str, user_level: str) -> bool:
        """
        為用戶設置分頁式選單
        
        Args:
            user_id: LINE 用戶 ID
            active_tab: 當前活躍分頁 ("basic", "fortune", "admin")
            user_level: 用戶等級 ("free", "premium", "admin")
            
        Returns:
            bool: 是否成功設置
        """
        try:
            # 獲取或創建分頁選單
            menu_id = self.setup_tabbed_rich_menu(active_tab, user_level)
            if not menu_id:
                logger.error(f"無法獲取分頁選單 ID: {active_tab}_{user_level}")
                return False
            
            # 為用戶設置選單
            return self.set_user_rich_menu(user_id, menu_id)
            
        except Exception as e:
            logger.error(f"為用戶 {user_id} 設置分頁選單失敗: {e}")
            return False
    
    def get_user_current_tab(self, user_id: str) -> Optional[str]:
        """
        獲取用戶當前的分頁
        
        Args:
            user_id: LINE 用戶 ID
            
        Returns:
            str: 當前分頁名稱，如果無法確定則返回 None
        """
        try:
            # 獲取用戶當前的 Rich Menu ID
            current_menu_id = self.get_user_rich_menu_id(user_id)
            if not current_menu_id:
                return None
            
            # 檢查緩存中是否有對應的分頁
            for cache_key, menu_id in self.rich_menu_cache.items():
                if menu_id == current_menu_id:
                    active_tab, user_level = cache_key.split('_', 1)
                    return active_tab
            
            # 如果緩存中沒有，查詢 Rich Menu 列表
            existing_menus = self.get_rich_menu_list()
            if existing_menus:
                for menu in existing_menus:
                    if menu.get("richMenuId") == current_menu_id:
                        menu_name = menu.get("name", "")
                        if menu_name.startswith("TabbedMenu_"):
                            parts = menu_name.split('_')
                            if len(parts) >= 3:
                                return parts[1]  # active_tab
            
            return None
            
        except Exception as e:
            logger.error(f"獲取用戶 {user_id} 當前分頁失敗: {e}")
            return None
    
    def setup_complete_rich_menu(self, force_recreate: bool = False) -> Optional[str]:
        """
        設定完整的 Rich Menu 系統（自動選擇最佳類型）
        
        Args:
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 檢查是否已有緩存的選單
            if not force_recreate and hasattr(self, '_default_menu_id') and self._default_menu_id:
                # 檢查選單是否仍存在
                existing_menus = self.get_rich_menu_list()
                if existing_menus:
                    for menu in existing_menus:
                        if menu.get("richMenuId") == self._default_menu_id:
                            logger.info(f"使用現有默認選單: {self._default_menu_id}")
                            return self._default_menu_id
                # 選單不存在，清除緩存
                self._default_menu_id = None
            
            # 優先使用駕駛視窗選單
            logger.info("🚗 創建駕駛視窗選單...")
            handler = DriverViewRichMenuHandler()
            
            # 創建基本分頁的駕駛視窗選單
            menu_id = handler.create_tab_rich_menu("basic")
            if menu_id:
                # 設為默認選單
                if self.set_default_rich_menu(menu_id):
                    self._default_menu_id = menu_id
                    logger.info(f"✅ 駕駛視窗選單設定成功: {menu_id}")
                    return menu_id
                else:
                    logger.warning("駕駛視窗選單創建成功但設為默認失敗")
                    return menu_id
            
            # 備用方案：使用圖片基礎選單
            logger.info("🖼️ 駕駛視窗選單創建失敗，使用圖片基礎選單...")
            if self.use_image_based:
                image_path, button_areas = generate_image_based_rich_menu("member")
            else:
                # 如果所有方案都失敗，創建基本配置
                logger.warning("所有選單類型都失敗，創建基本配置")
                button_areas = [
                    {
                        "bounds": {"x": 0, "y": 0, "width": 833, "height": 1000},
                        "action": {"type": "message", "text": "本週占卜"}
                    },
                    {
                        "bounds": {"x": 833, "y": 0, "width": 833, "height": 500},
                        "action": {"type": "message", "text": "會員資訊"}
                    },
                    {
                        "bounds": {"x": 833, "y": 500, "width": 833, "height": 500},
                        "action": {"type": "message", "text": "命盤綁定"}
                    }
                ]
                image_path = "rich_menu_images/drive_view.jpg"  # 使用壓縮後的駕駛視窗圖片
            
            if not image_path or not os.path.exists(image_path):
                logger.error(f"選單圖片不存在: {image_path}")
                return None
            
            # 創建 Rich Menu 配置
            rich_menu_config = {
                "size": {
                    "width": LineBotConfig.RICH_MENU_WIDTH,
                    "height": LineBotConfig.RICH_MENU_HEIGHT
                },
                "selected": True,
                "name": "駕駛視窗紫微選單",
                "chatBarText": "🚗 駕駛視窗紫微",
                "areas": button_areas
            }
            
            # 創建 Rich Menu
            rich_menu_id = self.create_rich_menu(rich_menu_config)
            if not rich_menu_id:
                logger.error("創建選單失敗")
                return None
            
            # 上傳圖片
            if not self.upload_rich_menu_image(rich_menu_id, image_path):
                logger.error("上傳選單圖片失敗")
                self.delete_rich_menu(rich_menu_id)
                return None
            
            # 設為默認選單
            if self.set_default_rich_menu(rich_menu_id):
                self._default_menu_id = rich_menu_id
                logger.info(f"✅ 備用選單設定成功: {rich_menu_id}")
            else:
                logger.warning("備用選單創建成功但設為默認失敗")
            
            return rich_menu_id
                
        except Exception as e:
            logger.error(f"設定完整選單時發生錯誤: {e}")
            return None
    
    def ensure_default_rich_menu(self) -> Optional[str]:
        """
        確保有預設的 Rich Menu，如果沒有則創建
        這個方法會重複使用現有的 Rich Menu，避免重複創建
        
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 1. 檢查是否已有預設 Rich Menu
            current_default = self.get_default_rich_menu_id()
            if current_default:
                logger.info(f"已存在預設 Rich Menu: {current_default}")
                return current_default
            
            # 2. 檢查是否有既存的 Rich Menu 可以重複使用
            existing_menus = self.get_rich_menu_list()
            if existing_menus:
                for menu in existing_menus:
                    menu_id = menu.get("richMenuId")
                    menu_name = menu.get("name", "")
                    
                    # 找到駕駛視窗主題的 Rich Menu
                    if "DriverView" in menu_name or "driver" in menu_name.lower():
                        logger.info(f"找到既存的駕駛視窗 Rich Menu: {menu_id}")
                        
                        # 設為預設
                        if self.set_default_rich_menu(menu_id):
                            logger.info(f"✅ 重複使用既存 Rich Menu: {menu_id}")
                            return menu_id
            
            # 3. 如果沒有合適的既存 Rich Menu，創建新的
            logger.info("沒有找到合適的既存 Rich Menu，創建新的...")
            return self.setup_complete_rich_menu(force_recreate=True)
            
        except Exception as e:
            logger.error(f"確保預設 Rich Menu 過程中發生錯誤: {e}")
            return None
    
    def cleanup_old_rich_menus(self, keep_menu_id: str = None) -> int:
        """
        清理舊的 Rich Menu（保留指定的）
        
        Args:
            keep_menu_id: 要保留的 Rich Menu ID
            
        Returns:
            int: 刪除的數量
        """
        try:
            menus = self.get_rich_menu_list()
            if not menus:
                return 0
            
            deleted_count = 0
            
            for menu in menus:
                menu_id = menu.get("richMenuId")
                
                # 跳過要保留的 Rich Menu
                if keep_menu_id and menu_id == keep_menu_id:
                    continue
                
                # 刪除其他 Rich Menu
                if self.delete_rich_menu(menu_id):
                    deleted_count += 1
                    logger.info(f"已刪除 Rich Menu: {menu_id}")
            
            logger.info(f"共清理了 {deleted_count} 個舊的 Rich Menu")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理舊 Rich Menu 過程中發生錯誤: {e}")
            return 0
    
    def set_user_rich_menu(self, user_id: str, rich_menu_id: str) -> bool:
        """
        設定用戶的 Rich Menu
        
        Args:
            user_id: 用戶 ID
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 是否成功設定
        """
        try:
            url = f"https://api.line.me/v2/bot/user/{user_id}/richmenu/{rich_menu_id}"
            headers = {
                "Authorization": f"Bearer {LineBotConfig.CHANNEL_ACCESS_TOKEN}"
            }
            
            response = requests.post(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ 用戶 {user_id} Rich Menu 設定成功")
                return True
            else:
                logger.error(f"❌ 用戶 {user_id} Rich Menu 設定失敗: {response.status_code}")
                logger.error(f"響應內容: {response.text}")
                logger.error(f"使用的 Rich Menu ID: {rich_menu_id}")
                logger.error(f"請求 URL: {url}")
                return False
                
        except Exception as e:
            logger.error(f"設定用戶 Rich Menu 時發生錯誤: {e}")
            return False
    
    def link_user_rich_menu(self, user_id: str, rich_menu_id: str) -> bool:
        """
        連結用戶的 Rich Menu（set_user_rich_menu 的別名）
        
        Args:
            user_id: 用戶 ID
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 是否成功連結
        """
        return self.set_user_rich_menu(user_id, rich_menu_id)
    
    def get_user_rich_menu_id(self, user_id: str) -> Optional[str]:
        """
        獲取特定用戶的 Rich Menu ID
        
        Args:
            user_id: LINE 用戶 ID
            
        Returns:
            str: 用戶的 Rich Menu ID（如果有）
        """
        url = f"{self.base_url}/user/{user_id}/richmenu"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            rich_menu_id = result.get("richMenuId")
            
            logger.info(f"用戶 {user_id} 的 Rich Menu ID: {rich_menu_id}")
            return rich_menu_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取用戶 {user_id} Rich Menu 失敗: {e}")
            return None
    
    def unlink_user_rich_menu(self, user_id: str) -> bool:
        """
        取消用戶的 Rich Menu 連結
        
        Args:
            user_id: LINE 用戶 ID
            
        Returns:
            bool: 是否成功取消連結
        """
        url = f"{self.base_url}/user/{user_id}/richmenu"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"成功取消用戶 {user_id} 的 Rich Menu 連結")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"取消用戶 {user_id} Rich Menu 連結失敗: {e}")
            return False
    
    def create_admin_menu_config(self) -> Dict:
        """
        創建管理員專用的 Rich Menu 配置
        
        Returns:
            Dict: Rich Menu 配置
        """
        # 使用駕駛視窗處理器創建管理員選單
        handler = DriverViewRichMenuHandler()
        
        # 創建進階分頁的配置（管理員專用）
        button_areas = handler.create_button_areas("advanced")
        
        menu_config = {
            "size": {
                "width": LineBotConfig.RICH_MENU_WIDTH,
                "height": LineBotConfig.RICH_MENU_HEIGHT
            },
            "selected": True,
            "name": "AdminDriverViewMenu",
            "chatBarText": "🚗 管理員駕駛視窗",
            "areas": button_areas
        }
        
        return menu_config

    def setup_admin_rich_menu(self, force_recreate: bool = False) -> Optional[str]:
        """
        設定管理員專用的 Rich Menu
        
        Args:
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 檢查是否需要重新創建
            cache_key = "admin_driver_view"
            
            if not force_recreate and cache_key in self.rich_menu_cache:
                existing_id = self.rich_menu_cache[cache_key]
                # 檢查選單是否仍存在
                existing_menus = self.get_rich_menu_list()
                if existing_menus:
                    for menu in existing_menus:
                        if menu.get("richMenuId") == existing_id:
                            logger.info(f"使用現有管理員選單: {existing_id}")
                            return existing_id
                # 選單不存在，清除緩存
                del self.rich_menu_cache[cache_key]
            
            # 使用駕駛視窗處理器創建管理員選單
            handler = DriverViewRichMenuHandler()
            menu_id = handler.create_tab_rich_menu("advanced")
            
            if not menu_id:
                logger.error("創建管理員駕駛視窗選單失敗")
                return None
            
            # 更新緩存
            self.rich_menu_cache[cache_key] = menu_id
            logger.info(f"✅ 管理員駕駛視窗選單創建成功: {menu_id}")
            return menu_id
                
        except Exception as e:
            logger.error(f"設定管理員選單時發生錯誤: {e}")
            return None

    def set_user_menu_by_role(self, user_id: str, is_admin: bool = False) -> bool:
        """
        根據用戶角色設置 Rich Menu
        
        Args:
            user_id: LINE 用戶 ID
            is_admin: 是否為管理員
            
        Returns:
            bool: 是否成功設置
        """
        try:
            if is_admin:
                # 管理員使用進階駕駛視窗選單
                menu_id = self.get_or_create_admin_menu_id()
                menu_type = "管理員駕駛視窗"
            else:
                # 一般用戶使用基本駕駛視窗選單
                menu_id = self.ensure_default_rich_menu()
                menu_type = "駕駛視窗"
            
            if not menu_id:
                logger.error(f"無法獲取{menu_type}選單 ID")
                return False
            
            # 為用戶設置選單
            success = self.set_user_rich_menu(user_id, menu_id)
            if success:
                logger.info(f"✅ 用戶 {user_id} 已設置{menu_type}選單")
            else:
                logger.error(f"❌ 用戶 {user_id} 設置{menu_type}選單失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"根據角色設置選單失敗: {e}")
            return False

    def get_or_create_admin_menu_id(self) -> Optional[str]:
        """
        獲取或創建管理員選單 ID
        
        Returns:
            str: 管理員選單 ID
        """
        try:
            # 檢查緩存
            cache_key = "admin_driver_view"
            if cache_key in self.rich_menu_cache:
                menu_id = self.rich_menu_cache[cache_key]
                # 驗證選單是否存在
                existing_menus = self.get_rich_menu_list()
                if existing_menus:
                    for menu in existing_menus:
                        if menu.get("richMenuId") == menu_id:
                            return menu_id
                # 選單不存在，清除緩存
                del self.rich_menu_cache[cache_key]
            
            # 創建新的管理員選單
            return self.setup_admin_rich_menu(force_recreate=True)
            
        except Exception as e:
            logger.error(f"獲取管理員選單 ID 失敗: {e}")
            return None
    
    def switch_generation_mode(self, use_image_based: bool):
        """
        切換圖片生成模式
        
        Args:
            use_image_based: True 使用圖片資源型，False 使用程式生成型
        """
        self.use_image_based = use_image_based
        logger.info(f"已切換圖片生成模式: {'圖片資源型' if use_image_based else '程式生成型'}")
    
    def setup_user_tabbed_rich_menu(self, user_id: str, user_level: str, active_tab: str = "basic", force_recreate: bool = False) -> Optional[str]:
        """
        為特定用戶設定分頁式 Rich Menu
        
        Args:
            user_id: LINE 用戶 ID
            user_level: 用戶等級 ("free", "premium", "admin")
            active_tab: 當前活躍分頁 ("basic", "fortune", "admin")
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 設定分頁選單
            rich_menu_id = self.setup_tabbed_rich_menu(active_tab, user_level, force_recreate)
            
            if not rich_menu_id:
                logger.error(f"設定用戶 {user_id} 的分頁選單失敗")
                return None
            
            # 連結到用戶
            if self.link_user_rich_menu(user_id, rich_menu_id):
                logger.info(f"✅ 成功為用戶 {user_id} 設定分頁選單: {rich_menu_id}")
                return rich_menu_id
            else:
                logger.error(f"連結用戶 {user_id} 分頁選單失敗")
                return None
                
        except Exception as e:
            logger.error(f"設定用戶 {user_id} 分頁選單過程中發生錯誤: {e}")
            return None
    
    def switch_user_tab(self, user_id: str, target_tab: str, user_level: str) -> bool:
        """
        切換用戶的分頁
        
        Args:
            user_id: LINE 用戶 ID
            target_tab: 目標分頁 ("basic", "fortune", "admin")
            user_level: 用戶等級 ("free", "premium", "admin")
            
        Returns:
            bool: 是否成功切換
        """
        try:
            # 檢查用戶是否有權限訪問目標分頁
            if not can_access_tab(target_tab, user_level):
                logger.warning(f"用戶 {user_id} (等級: {user_level}) 無權限訪問分頁: {target_tab}")
                return False
            
            # 設定新分頁選單
            rich_menu_id = self.setup_user_tabbed_rich_menu(user_id, user_level, target_tab)
            
            if rich_menu_id:
                logger.info(f"✅ 成功切換用戶 {user_id} 到分頁 {target_tab}")
                return True
            else:
                logger.error(f"切換用戶 {user_id} 到分頁 {target_tab} 失敗")
                return False
                
        except Exception as e:
            logger.error(f"切換用戶 {user_id} 分頁時發生錯誤: {e}")
            return False

    def get_rich_menu(self, rich_menu_id):
        """獲取指定的 Rich Menu"""
        try:
            return self.line_bot_api.get_rich_menu(rich_menu_id)
        except LineBotApiError as e:
            logger.error(f"獲取 Rich Menu 失敗, ID: {rich_menu_id}, 錯誤: {e.status_code} {e.error.message}")
            raise
    
    def get_rich_menu_image(self, rich_menu_id):
        """下載指定 Rich Menu 的圖片"""
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

    def get_rich_menu_list(self):
        """獲取所有 Rich Menu 的列表"""
        url = f"{self.base_url}/richmenu/list"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            rich_menus = result.get("richmenus", [])
            
            logger.info(f"成功獲取 Rich Menu 列表，共 {len(rich_menus)} 個")
            return rich_menus
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取 Rich Menu 列表失敗: {e}")
            return None

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