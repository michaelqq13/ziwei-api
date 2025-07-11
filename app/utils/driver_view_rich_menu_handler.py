"""
駕駛視窗 Rich Menu 處理器
處理分頁切換功能和動態選單更新
"""
import logging
import json
import tempfile
import os
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from importlib import resources

from app.config.linebot_config import LineBotConfig

logger = logging.getLogger(__name__)

def get_asset_stream(filename: str) -> Optional[BytesIO]:
    """從 app/assets 套件資源安全地獲取資產的二進位流"""
    try:
        # 'app.assets' 是包含資源的套件
        with resources.files('app.assets').joinpath(filename).open('rb') as f:
            return BytesIO(f.read())
    except FileNotFoundError:
        logger.error(f"❌ 在套件資源 'app.assets' 中找不到檔案: '{filename}'")
        return None
    except Exception as e:
        logger.error(f"❌ 從套件資源讀取 '{filename}' 時發生錯誤: {e}", exc_info=True)
        return None

class DriverViewRichMenuHandler:
    """駕駛視窗 Rich Menu 處理器 (最終簡化版)"""

    def __init__(self):
        self.manager = None
        self.rich_menu_cache = {}
        self.menu_version = "v2.8" # 更新版本號以觸發最終刷新

        # 分頁配置（只用於定義按鈕點擊區域，不再用於繪圖）
        self.tab_configs = {
            "basic": {"name": "基本功能"},
            "fortune": {"name": "運勢"},
            "advanced": {"name": "進階選項"}
        }
        
        # 按鈕行為配置
        self.button_actions = {
            "basic": [
                {"type": "message", "text": "本週占卜"},
                {"type": "message", "text": "會員資訊"},
                {"type": "message", "text": "命盤綁定"},
            ],
            "fortune": [
                {"type": "message", "text": "流年運勢"},
                {"type": "message", "text": "流月運勢"},
                {"type": "message", "text": "流日運勢"},
            ],
            "advanced": [
                {"type": "message", "text": "指定時間占卜"},
                {"type": "message", "text": "詳細分析"},
                {"type": "message", "text": "管理功能"},
            ]
        }
        
        # 點擊區域
        self.tab_positions = [{"x": 417, "y": 246, "width": 500, "height": 83}, {"x": 1000, "y": 50, "width": 500, "height": 279}, {"x": 1583, "y": 266, "width": 500, "height": 63}]
        self.button_positions = [{"x": 667, "y": 580, "width": 400, "height": 200}, {"x": 1050, "y": 525, "width": 400, "height": 200}, {"x": 1633, "y": 580, "width": 400, "height": 200}]
        
        # 啟動時從 LINE 同步 Rich Menu
        self._sync_menus_from_line()

    def _ensure_manager(self):
        """確保 RichMenuManager 已初始化"""
        if self.manager is None:
            from app.utils.rich_menu_manager import RichMenuManager
            self.manager = RichMenuManager()
    
    def create_button_areas(self, active_tab: str) -> List[Dict]:
        """創建按鈕區域配置"""
        button_areas = []
        
        # 1. 創建分頁點擊區域
        for i, tab_key in enumerate(self.tab_configs.keys()):
            pos = self.tab_positions[i]
            button_areas.append({
                "bounds": {"x": pos["x"], "y": pos["y"], "width": pos["width"], "height": pos["height"]},
                "action": {"type": "postback", "data": f"tab_{tab_key}"}
            })
        
        # 2. 創建功能按鈕點擊區域
        actions = self.button_actions.get(active_tab, [])
        for i, action in enumerate(actions):
            if i < len(self.button_positions):
                pos = self.button_positions[i]
                button_areas.append({
                    "bounds": {"x": pos["x"], "y": pos["y"], "width": pos["width"], "height": pos["height"]},
                    "action": action
                })
                
        return button_areas

    def create_tab_rich_menu(self, tab_name: str) -> Optional[str]:
        """創建指定分頁的 Rich Menu（使用臨時檔案上傳）"""
        temp_image_path = None
        try:
            self._ensure_manager()
            
            image_filename = f"rich_menu_{tab_name}.jpg"
            image_stream = get_asset_stream(image_filename)
            if not image_stream: return None

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(image_stream.getvalue())
                temp_image_path = temp_file.name
            
            button_areas = self.create_button_areas(tab_name)
            
            rich_menu_config = {
                "size": {"width": LineBotConfig.RICH_MENU_WIDTH, "height": LineBotConfig.RICH_MENU_HEIGHT},
                "selected": True,
                "name": f"DriverView_{tab_name}_{self.menu_version}",
                "chatBarText": f"🚗 {self.tab_configs.get(tab_name, {}).get('name', '選單')}",
                "areas": button_areas
            }
            
            rich_menu_id = self.manager.create_rich_menu(rich_menu_config)
            if not rich_menu_id:
                logger.error("❌ Rich Menu 創建失敗 (無法獲取 ID)")
                if temp_image_path: os.unlink(temp_image_path)
                return None
            
            if not self.manager.upload_rich_menu_image(rich_menu_id, temp_image_path):
                logger.error(f"❌ 從 '{temp_image_path}' 上傳圖片失敗")
                self.manager.delete_rich_menu(rich_menu_id)
                if temp_image_path: os.unlink(temp_image_path)
                return None
            
            if temp_image_path: os.unlink(temp_image_path)
            
            self.rich_menu_cache[f"driver_view_{tab_name}"] = rich_menu_id
            logger.info(f"✅ 分頁 Rich Menu 創建成功: {tab_name} -> {rich_menu_id}")
            return rich_menu_id
            
        except Exception as e:
            logger.error(f"❌ 創建分頁 Rich Menu 時發生嚴重錯誤: {e}", exc_info=True)
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            return None

    def _sync_menus_from_line(self):
        """從 LINE 平台同步符合當前版本的 Rich Menu 到本地快取"""
        try:
            self._ensure_manager()
            logger.info("🔄 正在從 LINE 平台同步 Rich Menu...")
            all_menus = self.manager.get_rich_menu_list()
            if not all_menus: return

            synced_count = 0
            for menu in all_menus:
                menu_name = menu.get("name", "")
                if menu_name.startswith("DriverView_") and menu_name.endswith(f"_{self.menu_version}"):
                    parts = menu_name.split('_')
                    if len(parts) == 3:
                        tab_name = parts[1]
                        self.rich_menu_cache[f"driver_view_{tab_name}"] = menu.get("richMenuId")
                        synced_count += 1
            
            logger.info(f"🏁 同步完成，找到 {synced_count} 個符合目前版本的選單。")

        except Exception as e:
            logger.error(f"❌ 從 LINE 同步 Rich Menu 時發生錯誤: {e}", exc_info=True)

    def validate_cached_menu(self, menu_id: str) -> bool:
        """驗證一個 Rich Menu ID 是否在 LINE 平台上真實存在"""
        self._ensure_manager()
        try:
            self.manager.get_rich_menu(menu_id)
            return True
        except Exception:
            return False

    def cleanup_old_driver_menus(self):
        """清理所有不符合當前版本的駕駛視窗選單"""
        self._ensure_manager()
        try:
            all_menus = self.manager.get_rich_menu_list()
            if not all_menus: return
            
            deleted_count = 0
            for menu in all_menus:
                menu_name = menu.get("name", "")
                if "DriverView" in menu_name and not menu_name.endswith(f"_{self.menu_version}"):
                    if self.manager.delete_rich_menu(menu.get("richMenuId")):
                        deleted_count += 1
                        logger.info(f"🗑️ 已刪除舊選單: {menu_name}")
            
            if deleted_count > 0:
                logger.info(f"🧹 清理完成！刪除了 {deleted_count} 個舊選單。")

        except Exception as e:
            logger.error(f"❌ 清理舊選單時發生錯誤: {e}", exc_info=True)

    def switch_to_tab(self, user_id: str, tab_name: str) -> bool:
        """切換到指定分頁"""
        try:
            self._ensure_manager()
            cache_key = f"driver_view_{tab_name}"
            rich_menu_id = self.rich_menu_cache.get(cache_key)

            if not rich_menu_id or not self.validate_cached_menu(rich_menu_id):
                logger.info(f"'{tab_name}' 選單不在快取中或已失效，將重新創建...")
                rich_menu_id = self.create_tab_rich_menu(tab_name)
                if not rich_menu_id: return False
            
            success = self.manager.set_user_rich_menu(user_id, rich_menu_id)
            if success:
                logger.info(f"✅ 用戶 {user_id} 成功切換到分頁: {tab_name}")
            else:
                logger.error(f"❌ 用戶 {user_id} 切換分頁失敗: {tab_name}")
            return success
        except Exception as e:
            logger.error(f"❌ 切換分頁時發生錯誤: {e}", exc_info=True)
            return False

    def handle_postback_event(self, user_id: str, postback_data: str) -> bool:
        """處理 PostBack 事件（分頁切換）"""
        if postback_data.startswith("tab_"):
            tab_name = postback_data.replace("tab_", "")
            if tab_name in self.tab_configs:
                return self.switch_to_tab(user_id, tab_name)
        return False
    
    def setup_default_tab(self, user_id: str, tab_name: str = "basic", force_refresh: bool = False) -> bool:
        """為用戶設定預設分頁"""
        if force_refresh:
            logger.info("⚡ 強制刷新觸發！將清理所有舊版本選單...")
            self.cleanup_old_driver_menus()
        return self.switch_to_tab(user_id, tab_name)


# 全局實例
driver_view_handler = DriverViewRichMenuHandler() 