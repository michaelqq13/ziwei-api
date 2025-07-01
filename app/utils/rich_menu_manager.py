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
from app.utils.rich_menu_image_generator import generate_starry_rich_menu

logger = logging.getLogger(__name__)

class RichMenuManager:
    """Rich Menu 管理器"""
    
    def __init__(self):
        self.channel_access_token = LineBotConfig.CHANNEL_ACCESS_TOKEN
        self.base_url = "https://api.line.me/v2/bot"
        self.headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
    
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
        # 生成圖片和按鈕區域
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
            image_path, button_areas = generate_starry_rich_menu()
            
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

# 全局實例
rich_menu_manager = RichMenuManager()

def setup_rich_menu(force_recreate: bool = False) -> Optional[str]:
    """
    設定 Rich Menu 的便捷函數
    
    Args:
        force_recreate: 是否強制重新創建
        
    Returns:
        str: Rich Menu ID (如果成功)
    """
    if force_recreate:
        return rich_menu_manager.setup_complete_rich_menu(force_recreate=True)
    else:
        return rich_menu_manager.ensure_default_rich_menu()

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

# 導出
__all__ = [
    "RichMenuManager",
    "rich_menu_manager",
    "setup_rich_menu", 
    "get_rich_menu_status"
] 