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
from app.utils.rich_menu_image_generator import generate_starry_rich_menu, generate_admin_starry_rich_menu
from app.utils.tabbed_rich_menu_generator import generate_tabbed_rich_menu
from app.utils.image_based_rich_menu_generator import generate_image_based_rich_menu

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
    
    def create_starry_sky_menu_config(self) -> Dict:
        """
        創建星空主題的 Rich Menu 配置
        
        Returns:
            Dict: Rich Menu 配置
        """
        # 根據設定選擇生成方式
        if self.use_image_based:
            # 使用圖片資源型生成器
            _, button_areas = generate_image_based_rich_menu("member")
        else:
            # 使用程式生成器
            _, button_areas = generate_starry_rich_menu()
        
        menu_config = {
            "size": {
                "width": LineBotConfig.RICH_MENU_WIDTH,
                "height": LineBotConfig.RICH_MENU_HEIGHT
            },
            "selected": True,
            "name": "StarrySkyMenu",
            "chatBarText": "✨ 星空紫微",
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
        _, button_areas = generate_tabbed_rich_menu(active_tab, user_level)
        
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
            from app.utils.tabbed_rich_menu_generator import generate_tabbed_rich_menu
            image_path, button_areas = generate_tabbed_rich_menu(active_tab, user_level)
            
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
        完整設定 Rich Menu（創建、上傳圖片、設為預設）
        
        Args:
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 檢查是否已有預設 Rich Menu
            if not force_recreate:
                existing_menu_id = self.get_default_rich_menu_id()
                if existing_menu_id:
                    logger.info(f"已存在預設 Rich Menu: {existing_menu_id}")
                    return existing_menu_id
            
            # 1. 生成圖片
            logger.info("正在生成 Rich Menu 圖片...")
            if self.use_image_based:
                # 使用圖片資源型生成器
                image_path, button_areas = generate_image_based_rich_menu("member")
                logger.info("使用圖片資源型生成器生成選單")
            else:
                # 使用程式生成器
                image_path, button_areas = generate_starry_rich_menu()
                logger.info("使用程式生成器生成選單")
            
            if not os.path.exists(image_path):
                logger.error(f"圖片生成失敗: {image_path}")
                return None
            
            # 2. 創建 Rich Menu 配置
            menu_config = self.create_starry_sky_menu_config()
            
            # 3. 創建 Rich Menu
            logger.info("正在創建 Rich Menu...")
            rich_menu_id = self.create_rich_menu(menu_config)
            
            if not rich_menu_id:
                logger.error("Rich Menu 創建失敗")
                return None
            
            # 4. 上傳圖片
            logger.info("正在上傳 Rich Menu 圖片...")
            if not self.upload_rich_menu_image(rich_menu_id, image_path):
                logger.error("圖片上傳失敗，嘗試刪除 Rich Menu")
                self.delete_rich_menu(rich_menu_id)
                return None
            
            # 5. 設為預設
            logger.info("正在設定為預設 Rich Menu...")
            if not self.set_default_rich_menu(rich_menu_id):
                logger.error("設定預設失敗")
                return None
            
            logger.info(f"✅ Rich Menu 設定完成: {rich_menu_id}")
            return rich_menu_id
            
        except Exception as e:
            logger.error(f"設定 Rich Menu 過程中發生錯誤: {e}")
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
                    
                    # 找到星空主題的 Rich Menu
                    if "StarrySky" in menu_name or "starry" in menu_name.lower():
                        logger.info(f"找到既存的星空 Rich Menu: {menu_id}")
                        
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
        為特定用戶設置 Rich Menu
        
        Args:
            user_id: LINE 用戶 ID
            rich_menu_id: Rich Menu ID
            
        Returns:
            bool: 是否成功設置
        """
        url = f"{self.base_url}/user/{user_id}/richmenu/{rich_menu_id}"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"成功為用戶 {user_id} 設置 Rich Menu: {rich_menu_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"為用戶 {user_id} 設置 Rich Menu 失敗: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"回應內容: {e.response.text}")
            return False
    
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
        創建管理員 Rich Menu 配置
        
        Returns:
            Dict: Rich Menu 配置
        """
        # 根據設定選擇生成方式
        if self.use_image_based:
            # 使用圖片資源型生成器
            _, button_areas = generate_image_based_rich_menu("admin")
        else:
            # 使用程式生成器
            _, button_areas = generate_admin_starry_rich_menu()
        
        menu_config = {
            "size": {
                "width": LineBotConfig.RICH_MENU_WIDTH,
                "height": LineBotConfig.RICH_MENU_HEIGHT
            },
            "selected": True,
            "name": "AdminStarrySkyMenu",
            "chatBarText": "🔧 管理員選單",
            "areas": button_areas
        }
        
        return menu_config
    
    def setup_admin_rich_menu(self, force_recreate: bool = False) -> Optional[str]:
        """
        設定管理員 Rich Menu
        
        Args:
            force_recreate: 是否強制重新創建
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 檢查是否已有管理員 Rich Menu
            if not force_recreate:
                existing_menu_id = self.get_or_create_admin_menu_id()
                if existing_menu_id:
                    logger.info(f"已存在管理員 Rich Menu: {existing_menu_id}")
                    return existing_menu_id
            
            # 1. 生成圖片
            logger.info("正在生成管理員 Rich Menu 圖片...")
            if self.use_image_based:
                # 使用圖片資源型生成器
                image_path, button_areas = generate_image_based_rich_menu("admin")
                logger.info("使用圖片資源型生成器生成管理員選單")
            else:
                # 使用程式生成器
                image_path, button_areas = generate_admin_starry_rich_menu()
                logger.info("使用程式生成器生成管理員選單")
            
            if not os.path.exists(image_path):
                logger.error(f"管理員圖片生成失敗: {image_path}")
                return None
            
            # 2. 創建 Rich Menu 配置
            menu_config = self.create_admin_menu_config()
            
            # 3. 創建 Rich Menu
            logger.info("正在創建管理員 Rich Menu...")
            rich_menu_id = self.create_rich_menu(menu_config)
            
            if not rich_menu_id:
                logger.error("管理員 Rich Menu 創建失敗")
                return None
            
            # 4. 上傳圖片
            logger.info("正在上傳管理員 Rich Menu 圖片...")
            if not self.upload_rich_menu_image(rich_menu_id, image_path):
                logger.error("管理員圖片上傳失敗，嘗試刪除 Rich Menu")
                self.delete_rich_menu(rich_menu_id)
                return None
            
            logger.info(f"✅ 管理員 Rich Menu 設定完成: {rich_menu_id}")
            return rich_menu_id
            
        except Exception as e:
            logger.error(f"設定管理員 Rich Menu 過程中發生錯誤: {e}")
            return None
    
    def set_user_menu_by_role(self, user_id: str, is_admin: bool = False) -> bool:
        """
        根據用戶角色設置對應的 Rich Menu
        
        Args:
            user_id: LINE 用戶 ID
            is_admin: 是否為管理員
            
        Returns:
            bool: 是否成功設置
        """
        try:
            if is_admin:
                # 管理員使用專用 Rich Menu
                admin_menu_id = self.setup_admin_rich_menu()
                if admin_menu_id:
                    return self.set_user_rich_menu(user_id, admin_menu_id)
                else:
                    logger.error("無法獲取管理員 Rich Menu ID")
                    return False
            else:
                # 一般用戶使用預設 Rich Menu
                default_menu_id = self.ensure_default_rich_menu()
                if default_menu_id:
                    return self.set_user_rich_menu(user_id, default_menu_id)
                else:
                    logger.error("無法獲取預設 Rich Menu ID")
                    return False
                    
        except Exception as e:
            logger.error(f"為用戶 {user_id} 設置 Rich Menu 失敗: {e}")
            return False
    
    def get_or_create_admin_menu_id(self) -> Optional[str]:
        """
        獲取或創建管理員 Rich Menu ID
        
        Returns:
            str: 管理員 Rich Menu ID
        """
        try:
            # 先檢查是否已存在
            existing_menus = self.get_rich_menu_list()
            if existing_menus:
                for menu in existing_menus:
                    menu_name = menu.get("name", "")
                    if "AdminStarrySky" in menu_name:
                        menu_id = menu.get("richMenuId")
                        logger.info(f"找到既存的管理員 Rich Menu: {menu_id}")
                        return menu_id
            
            # 不存在則創建
            return self.setup_admin_rich_menu(force_recreate=True)
            
        except Exception as e:
            logger.error(f"獲取或創建管理員 Rich Menu 失敗: {e}")
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
    
    def switch_user_tab(self, user_id: str, user_level: str, new_tab: str) -> bool:
        """
        切換用戶的分頁
        
        Args:
            user_id: LINE 用戶 ID
            user_level: 用戶等級
            new_tab: 新分頁 ("basic", "fortune", "admin")
            
        Returns:
            bool: 是否成功切換
        """
        try:
            # 檢查分頁權限
            from app.utils.tabbed_rich_menu_generator import TabbedRichMenuGenerator
            generator = TabbedRichMenuGenerator()
            
            if not generator._check_tab_permission(
                generator._get_tab_configs(user_level)[0]["required_level"] if generator._get_tab_configs(user_level) else "admin",
                user_level
            ):
                logger.warning(f"用戶 {user_id} 沒有權限訪問分頁 {new_tab}")
                return False
            
            # 設定新分頁選單
            rich_menu_id = self.setup_user_tabbed_rich_menu(user_id, user_level, new_tab)
            
            if rich_menu_id:
                logger.info(f"✅ 成功切換用戶 {user_id} 到分頁 {new_tab}")
                return True
            else:
                logger.error(f"切換用戶 {user_id} 到分頁 {new_tab} 失敗")
                return False
                
        except Exception as e:
            logger.error(f"切換用戶 {user_id} 分頁時發生錯誤: {e}")
            return False

# 全局實例
rich_menu_manager = RichMenuManager()

def setup_rich_menu(force_recreate: bool = False, use_image_based: bool = False) -> Optional[str]:
    """
    設定 Rich Menu（全域函數）
    
    Args:
        force_recreate: 是否強制重新創建
        use_image_based: 是否使用圖片資源型生成器
        
    Returns:
        str: Rich Menu ID (如果成功)
    """
    manager = RichMenuManager(use_image_based=use_image_based)
    return manager.setup_complete_rich_menu(force_recreate)

def setup_tabbed_rich_menu(active_tab: str, user_level: str, force_recreate: bool = False) -> Optional[str]:
    """
    設定分頁式 Rich Menu 的便捷函數
    
    Args:
        active_tab: 當前活躍分頁 ("basic", "fortune", "admin")
        user_level: 用戶等級 ("free", "premium", "admin")
        force_recreate: 是否強制重新創建
        
    Returns:
        str: Rich Menu ID (如果成功)
    """
    return rich_menu_manager.setup_tabbed_rich_menu(active_tab, user_level, force_recreate)

def set_user_tabbed_menu(user_id: str, active_tab: str, user_level: str) -> bool:
    """
    為用戶設置分頁式選單的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        active_tab: 當前活躍分頁 ("basic", "fortune", "admin")
        user_level: 用戶等級 ("free", "premium", "admin")
        
    Returns:
        bool: 是否成功設置
    """
    return rich_menu_manager.set_user_tabbed_menu(user_id, active_tab, user_level)

def get_user_current_tab(user_id: str) -> Optional[str]:
    """
    獲取用戶當前分頁的便捷函數
    
    Args:
        user_id: LINE 用戶 ID
        
    Returns:
        str: 當前分頁名稱，如果無法確定則返回 None
    """
    return rich_menu_manager.get_user_current_tab(user_id)

def get_rich_menu_status() -> Dict[str, Any]:
    """
    獲取 Rich Menu 狀態的便捷函數
    
    Returns:
        Dict: Rich Menu 狀態資訊
    """
    current_default = rich_menu_manager.get_default_rich_menu_id()
    all_menus = rich_menu_manager.get_rich_menu_list()
    
    return {
        "current_default": current_default,
        "total_menus": len(all_menus) if all_menus else 0,
        "all_menus": all_menus or []
    }

def update_user_rich_menu(user_id: str, is_admin: bool = False, use_image_based: bool = False) -> bool:
    """
    更新用戶的 Rich Menu
    
    Args:
        user_id: 用戶 ID
        is_admin: 是否為管理員
        use_image_based: 是否使用圖片資源型生成器
        
    Returns:
        bool: 是否成功
    """
    try:
        manager = RichMenuManager(use_image_based=use_image_based)
        return manager.set_user_menu_by_role(user_id, is_admin)
    except Exception as e:
        logger.error(f"更新用戶 Rich Menu 失敗: {e}")
        return False

def determine_user_level(user_permissions: Dict[str, Any]) -> str:
    """
    根據用戶權限確定用戶等級
    
    Args:
        user_permissions: 用戶權限資訊
        
    Returns:
        str: 用戶等級 ("free", "premium", "admin")
    """
    if user_permissions.get("is_admin", False):
        return "admin"
    elif user_permissions.get("is_premium", False):
        return "premium"
    else:
        return "free"

def get_default_tab_for_user_level(user_level: str) -> str:
    """
    根據用戶等級獲取預設分頁
    
    Args:
        user_level: 用戶等級 ("free", "premium", "admin")
        
    Returns:
        str: 預設分頁名稱
    """
    # 所有用戶都從基本功能分頁開始
    return "basic"

def switch_user_tab(user_id: str, target_tab: str, user_level: str) -> bool:
    """
    切換用戶的分頁
    
    Args:
        user_id: LINE 用戶 ID
        target_tab: 目標分頁 ("basic", "fortune", "admin")
        user_level: 用戶等級 ("free", "premium", "admin")
        
    Returns:
        bool: 是否成功切換
    """
    # 檢查用戶是否有權限訪問目標分頁
    if not can_access_tab(target_tab, user_level):
        logger.warning(f"用戶 {user_id} (等級: {user_level}) 無權限訪問分頁: {target_tab}")
        return False
    
    # 切換到目標分頁
    return set_user_tabbed_menu(user_id, target_tab, user_level)

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
        # 運勢分頁只有付費會員和管理員可以訪問
        return user_level in ["premium", "admin"]
    elif tab_name == "admin":
        # 進階選項分頁只有管理員可以訪問
        return user_level == "admin"
    else:
        return False

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