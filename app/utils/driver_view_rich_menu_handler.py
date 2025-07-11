"""
駕駛視窗 Rich Menu 處理器
處理分頁切換功能和動態選單更新
"""
import logging
import requests
import tempfile
import os
from typing import Dict, List, Optional

from app.config.linebot_config import LineBotConfig
from app.utils.rich_menu_manager import RichMenuManager

logger = logging.getLogger(__name__)

# --- 圖片 URL ---
PRE_RENDERED_MENUS = {
    "basic": "https://i.imgur.com/uJz4TqY.jpeg",
    "fortune": "https://i.imgur.com/gK9sNGe.jpeg",
    "advanced": "https://i.imgur.com/s6XzV8B.jpeg",
}

# --- 點擊區域配置 ---
TAB_POSITIONS = [{"x": 417, "y": 246, "width": 500, "height": 83}, {"x": 1000, "y": 50, "width": 500, "height": 279}, {"x": 1583, "y": 266, "width": 500, "height": 63}]
BUTTON_POSITIONS = [{"x": 667, "y": 580, "width": 400, "height": 200}, {"x": 1050, "y": 525, "width": 400, "height": 200}, {"x": 1633, "y": 580, "width": 400, "height": 200}]
BUTTON_ACTIONS = {
    "basic": [{"type":"message","text":"本週占卜"},{"type":"message","text":"會員資訊"},{"type":"message","text":"命盤綁定"}],
    "fortune": [{"type":"message","text":"流年運勢"},{"type":"message","text":"流月運勢"},{"type":"message","text":"流日運勢"}],
    "advanced": [{"type":"message","text":"指定時間占卜"},{"type":"message","text":"詳細分析"},{"type":"message","text":"管理功能"}]
}

class DriverViewRichMenuHandler:
    """駕駛視窗 Rich Menu 處理器（終極簡化版）"""
    
    def __init__(self):
        self.manager = RichMenuManager()
        self.rich_menu_cache = {}
        self.menu_version = "v5.0" # 最終版本
        self._sync_menus_from_line()

    def _create_button_areas(self, active_tab: str) -> List[Dict]:
        areas = []
        for i, tab_key in enumerate(["basic", "fortune", "advanced"]):
            pos = TAB_POSITIONS[i]
            areas.append({"bounds": pos, "action": {"type": "postback", "data": f"tab_{tab_key}"}})
        
        actions = BUTTON_ACTIONS.get(active_tab, [])
        for i, action in enumerate(actions):
            pos = BUTTON_POSITIONS[i]
            areas.append({"bounds": pos, "action": action})
        return areas

    def create_tab_rich_menu(self, tab_name: str) -> Optional[str]:
        temp_image_path = None
        try:
            image_url = PRE_RENDERED_MENUS[tab_name]
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(response.content)
                temp_image_path = temp_file.name
            
            rich_menu_config = {
                "size": {"width": 2500, "height": 1686},
                "selected": True,
                "name": f"DriverView_{tab_name}_{self.menu_version}",
                "chatBarText": "駕駛艙模式",
                "areas": self._create_button_areas(tab_name)
            }
            
            rich_menu_id = self.manager.create_rich_menu(rich_menu_config)
            if not rich_menu_id: raise Exception("Create rich menu object failed")

            if not self.manager.upload_rich_menu_image(rich_menu_id, temp_image_path):
                raise Exception("Upload rich menu image failed")
            
            os.unlink(temp_image_path)
            self.rich_menu_cache[f"driver_view_{tab_name}"] = rich_menu_id
            logger.info(f"✅ Created and uploaded new menu for {tab_name}: {rich_menu_id}")
            return rich_menu_id
        except Exception as e:
            logger.error(f"❌ Failed to create tab rich menu for {tab_name}: {e}", exc_info=True)
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            return None

    def _sync_menus_from_line(self):
        try:
            all_menus = self.manager.get_rich_menu_list()
            for menu in all_menus:
                name = menu.get("name", "")
                if name.startswith("DriverView_") and name.endswith(f"_{self.menu_version}"):
                    tab_name = name.split('_')[1]
                    self.rich_menu_cache[f"driver_view_{tab_name}"] = menu.get("richMenuId")
            logger.info(f"🔄 Synced {len(self.rich_menu_cache)} menus from Line.")
        except Exception as e:
            logger.error(f"❌ Failed to sync menus from Line: {e}", exc_info=True)

    def switch_to_tab(self, user_id: str, tab_name: str) -> bool:
        try:
            menu_id = self.rich_menu_cache.get(f"driver_view_{tab_name}")
            if not menu_id:
                menu_id = self.create_tab_rich_menu(tab_name)
            
            if not menu_id: return False

            return self.manager.set_user_rich_menu(user_id, menu_id)
        except Exception as e:
            logger.error(f"❌ Failed to switch tab for {user_id} to {tab_name}: {e}", exc_info=True)
            return False

    def handle_postback_event(self, user_id: str, postback_data: str) -> bool:
        if postback_data.startswith("tab_"):
            tab_name = postback_data.replace("tab_", "")
            if tab_name in PRE_RENDERED_MENUS:
                return self.switch_to_tab(user_id, tab_name)
        return False
    
    def setup_default_tab(self, user_id: str, tab_name: str = "basic", force_refresh: bool = False) -> bool:
        if force_refresh:
            self.rich_menu_cache.clear() # Force recreate
        return self.switch_to_tab(user_id, tab_name)

driver_view_handler = DriverViewRichMenuHandler() 