"""
駕駛視窗 Rich Menu 處理器
處理分頁切換功能和動態選單更新
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from app.utils.rich_menu_manager import RichMenuManager
from app.config.linebot_config import LineBotConfig

logger = logging.getLogger(__name__)

class DriverViewRichMenuHandler:
    """駕駛視窗 Rich Menu 處理器"""
    
    def __init__(self):
        self.manager = RichMenuManager()
        self.base_image_path = "rich_menu_images/driver_view_richmenu.png"
        self.rich_menu_cache = {}  # 緩存不同分頁的 Rich Menu ID
        
        # 分頁配置
        self.tab_configs = {
            "basic": {
                "name": "基本功能",
                "buttons": [
                    {"text": "🔮 本週占卜", "action": {"type": "message", "text": "本週占卜"}},
                    {"text": "📊 會員資訊", "action": {"type": "message", "text": "會員資訊"}},
                    {"text": "⚙️ 設定", "action": {"type": "message", "text": "設定"}}
                ]
            },
            "fortune": {
                "name": "運勢",
                "buttons": [
                    {"text": "🎯 流年運勢", "action": {"type": "message", "text": "流年運勢"}},
                    {"text": "🌙 流月運勢", "action": {"type": "message", "text": "流月運勢"}},
                    {"text": "☀️ 流日運勢", "action": {"type": "message", "text": "流日運勢"}}
                ]
            },
            "advanced": {
                "name": "進階選項",
                "buttons": [
                    {"text": "🎲 指定時間占卜", "action": {"type": "message", "text": "指定時間占卜"}},
                    {"text": "📈 詳細分析", "action": {"type": "message", "text": "詳細分析"}},
                    {"text": "🔧 管理功能", "action": {"type": "message", "text": "管理功能"}}
                ]
            }
        }
        
        # 按鈕位置配置
        self.tab_positions = [
            {"x": 417, "y": 50, "width": 500, "height": 280},   # 左側螢幕
            {"x": 1000, "y": 50, "width": 500, "height": 280}, # 中間螢幕
            {"x": 1583, "y": 50, "width": 500, "height": 280}  # 右側螢幕
        ]
        
        self.button_positions = [
            {"x": 208, "y": 800, "width": 625, "height": 800},  # 左側按鈕
            {"x": 833, "y": 800, "width": 634, "height": 800},  # 中間按鈕
            {"x": 1467, "y": 800, "width": 625, "height": 800}  # 右側按鈕
        ]
    
    def create_tab_image_with_highlight(self, active_tab: str) -> str:
        """
        創建帶有高亮分頁的圖片
        
        Args:
            active_tab: 當前活躍的分頁 ("basic", "fortune", "advanced")
            
        Returns:
            str: 生成的圖片路徑
        """
        try:
            # 載入基礎圖片
            base_image = Image.open(self.base_image_path)
            draw = ImageDraw.Draw(base_image)
            
            # 嘗試載入字體
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # 定義分頁標籤
            tabs = ["basic", "fortune", "advanced"]
            tab_names = ["基本功能", "運勢", "進階選項"]
            
            # 為每個分頁添加視覺效果
            for i, (tab_key, tab_name) in enumerate(zip(tabs, tab_names)):
                pos = self.tab_positions[i]
                
                if tab_key == active_tab:
                    # 活躍分頁：螢幕亮起效果
                    # 1. 添加亮綠色高亮邊框（模擬螢幕發光）
                    for width in range(1, 8):  # 多層邊框創造發光效果
                        alpha = max(50, 200 - width * 20)  # 漸變透明度
                        draw.rectangle([
                            pos["x"] - width, pos["y"] - width, 
                            pos["x"] + pos["width"] + width, pos["y"] + pos["height"] + width
                        ], outline=(0, 255, 100, alpha), width=2)
                    
                    # 2. 螢幕內部亮度增強（白色半透明層）
                    overlay = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.rectangle([
                        pos["x"] + 10, pos["y"] + 10,
                        pos["x"] + pos["width"] - 10, pos["y"] + pos["height"] - 10
                    ], fill=(255, 255, 255, 80))  # 白色半透明層
                    base_image = Image.alpha_composite(base_image.convert('RGBA'), overlay).convert('RGB')
                    draw = ImageDraw.Draw(base_image)
                    
                    # 3. 添加活躍指示圖標（亮綠色圓點）
                    center_x = pos["x"] + pos["width"] // 2
                    center_y = pos["y"] + pos["height"] // 2
                    circle_radius = 25
                    
                    # 發光圓點效果
                    for r in range(circle_radius, 0, -3):
                        alpha = min(255, r * 8)
                        draw.ellipse([
                            center_x - r, center_y - r,
                            center_x + r, center_y + r
                        ], fill=(0, 255, 100, alpha))
                    
                    # 4. 分頁名稱（在螢幕上方）
                    text_y = pos["y"] - 30
                    draw.text((center_x, text_y), tab_name, fill=(0, 255, 100), 
                             font=font_medium, anchor="mm")
                    
                else:
                    # 非活躍分頁：螢幕暗淡效果
                    # 1. 暗灰色邊框
                    draw.rectangle([
                        pos["x"], pos["y"], 
                        pos["x"] + pos["width"], pos["y"] + pos["height"]
                    ], outline=(80, 80, 80), width=2)
                    
                    # 2. 螢幕暗化效果（深色半透明層）
                    overlay = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.rectangle([
                        pos["x"] + 5, pos["y"] + 5,
                        pos["x"] + pos["width"] - 5, pos["y"] + pos["height"] - 5
                    ], fill=(0, 0, 0, 60))  # 黑色半透明層（螢幕關閉效果）
                    base_image = Image.alpha_composite(base_image.convert('RGBA'), overlay).convert('RGB')
                    draw = ImageDraw.Draw(base_image)
                    
                    # 3. 暗淡的指示圖標
                    center_x = pos["x"] + pos["width"] // 2
                    center_y = pos["y"] + pos["height"] // 2
                    draw.ellipse([
                        center_x - 15, center_y - 15,
                        center_x + 15, center_y + 15
                    ], fill=(100, 100, 100), outline=(60, 60, 60))
                    
                    # 4. 分頁名稱（暗色）
                    text_y = pos["y"] - 30
                    draw.text((center_x, text_y), tab_name, fill=(120, 120, 120), 
                             font=font_medium, anchor="mm")
            
            # 5. 在底部添加當前分頁的功能提示
            if active_tab in self.tab_configs:
                buttons = self.tab_configs[active_tab]["buttons"]
                button_texts = [btn["text"] for btn in buttons]
                
                # 底部功能預覽文字
                preview_text = " | ".join(button_texts)
                preview_y = base_image.height - 50
                draw.text((base_image.width // 2, preview_y), preview_text, 
                         fill=(0, 255, 100), font=font_medium, anchor="mm")
            
            # 保存圖片
            output_path = f"rich_menu_images/driver_view_{active_tab}_tab.png"
            base_image.save(output_path)
            
            logger.info(f"✅ 創建高亮分頁圖片成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ 創建分頁圖片失敗: {e}")
            return self.base_image_path
    
    def create_button_areas(self, active_tab: str) -> List[Dict]:
        """
        創建指定分頁的按鈕區域配置
        
        Args:
            active_tab: 當前活躍的分頁
            
        Returns:
            List[Dict]: 按鈕區域配置
        """
        button_areas = []
        
        # 添加分頁標籤按鈕（用於切換）
        tabs = ["basic", "fortune", "advanced"]
        for i, tab_key in enumerate(tabs):
            button_areas.append({
                "bounds": {
                    "x": self.tab_positions[i]["x"],
                    "y": self.tab_positions[i]["y"],
                    "width": self.tab_positions[i]["width"],
                    "height": self.tab_positions[i]["height"]
                },
                "action": {
                    "type": "postback",
                    "data": f"tab_{tab_key}"
                }
            })
        
        # 添加當前分頁的功能按鈕
        if active_tab in self.tab_configs:
            buttons = self.tab_configs[active_tab]["buttons"]
            for i, button_config in enumerate(buttons):
                if i < len(self.button_positions):
                    button_areas.append({
                        "bounds": {
                            "x": self.button_positions[i]["x"],
                            "y": self.button_positions[i]["y"],
                            "width": self.button_positions[i]["width"],
                            "height": self.button_positions[i]["height"]
                        },
                        "action": button_config["action"]
                    })
        
        return button_areas
    
    def switch_to_tab(self, user_id: str, tab_name: str) -> bool:
        """
        切換到指定分頁
        
        Args:
            user_id: 用戶 ID
            tab_name: 分頁名稱 ("basic", "fortune", "advanced")
            
        Returns:
            bool: 是否成功切換
        """
        try:
            # 檢查緩存
            cache_key = f"driver_view_{tab_name}"
            if cache_key in self.rich_menu_cache:
                rich_menu_id = self.rich_menu_cache[cache_key]
                logger.info(f"✅ 使用緩存的 Rich Menu: {rich_menu_id}")
            else:
                # 創建新的 Rich Menu
                rich_menu_id = self.create_tab_rich_menu(tab_name)
                if not rich_menu_id:
                    logger.error(f"❌ 創建分頁 Rich Menu 失敗: {tab_name}")
                    return False
                self.rich_menu_cache[cache_key] = rich_menu_id
            
            # 為用戶設定 Rich Menu
            success = self.manager.set_user_rich_menu(user_id, rich_menu_id)
            if success:
                logger.info(f"✅ 用戶 {user_id} 成功切換到分頁: {tab_name}")
            else:
                logger.error(f"❌ 用戶 {user_id} 切換分頁失敗: {tab_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 切換分頁時發生錯誤: {e}")
            return False
    
    def create_tab_rich_menu(self, tab_name: str) -> Optional[str]:
        """
        創建指定分頁的 Rich Menu
        
        Args:
            tab_name: 分頁名稱
            
        Returns:
            str: Rich Menu ID (如果成功)
        """
        try:
            # 創建分頁圖片
            image_path = self.create_tab_image_with_highlight(tab_name)
            
            # 創建按鈕區域
            button_areas = self.create_button_areas(tab_name)
            
            # 創建 Rich Menu 配置
            tab_display_name = self.tab_configs.get(tab_name, {}).get("name", tab_name)
            rich_menu_config = {
                "size": {
                    "width": LineBotConfig.RICH_MENU_WIDTH,
                    "height": LineBotConfig.RICH_MENU_HEIGHT
                },
                "selected": True,
                "name": f"DriverView_{tab_name}",
                "chatBarText": f"🚗 {tab_display_name}",
                "areas": button_areas
            }
            
            # 創建 Rich Menu
            rich_menu_id = self.manager.create_rich_menu(rich_menu_config)
            if not rich_menu_id:
                logger.error("❌ Rich Menu 創建失敗")
                return None
            
            # 上傳圖片
            if not self.manager.upload_rich_menu_image(rich_menu_id, image_path):
                logger.error("❌ 圖片上傳失敗")
                self.manager.delete_rich_menu(rich_menu_id)
                return None
            
            logger.info(f"✅ 分頁 Rich Menu 創建成功: {tab_name} -> {rich_menu_id}")
            return rich_menu_id
            
        except Exception as e:
            logger.error(f"❌ 創建分頁 Rich Menu 失敗: {e}")
            return None
    
    def handle_postback_event(self, user_id: str, postback_data: str) -> bool:
        """
        處理 PostBack 事件（分頁切換）
        
        Args:
            user_id: 用戶 ID
            postback_data: PostBack 數據
            
        Returns:
            bool: 是否成功處理
        """
        try:
            if postback_data.startswith("tab_"):
                tab_name = postback_data.replace("tab_", "")
                if tab_name in self.tab_configs:
                    return self.switch_to_tab(user_id, tab_name)
                else:
                    logger.warning(f"⚠️ 未知的分頁名稱: {tab_name}")
                    return False
            else:
                logger.info(f"📥 非分頁切換的 PostBack: {postback_data}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 處理 PostBack 事件失敗: {e}")
            return False
    
    def setup_default_tab(self, user_id: str, tab_name: str = "basic") -> bool:
        """
        為用戶設定預設分頁
        
        Args:
            user_id: 用戶 ID
            tab_name: 預設分頁名稱
            
        Returns:
            bool: 是否成功設定
        """
        return self.switch_to_tab(user_id, tab_name)
    
    def get_tab_info(self, tab_name: str) -> Dict:
        """
        獲取分頁資訊
        
        Args:
            tab_name: 分頁名稱
            
        Returns:
            Dict: 分頁資訊
        """
        return self.tab_configs.get(tab_name, {})
    
    def list_available_tabs(self) -> List[str]:
        """
        列出所有可用的分頁
        
        Returns:
            List[str]: 分頁名稱列表
        """
        return list(self.tab_configs.keys())

# 全局實例
driver_view_handler = DriverViewRichMenuHandler() 