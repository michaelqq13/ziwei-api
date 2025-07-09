"""
駕駛視窗 Rich Menu 處理器
處理分頁切換功能和動態選單更新
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from app.config.linebot_config import LineBotConfig

logger = logging.getLogger(__name__)

class DriverViewRichMenuHandler:
    """駕駛視窗 Rich Menu 處理器"""
    
    def __init__(self):
        # 移除循環導入，改為在需要時才導入
        self.manager = None  # 延遲初始化
        self.base_image_path = "rich_menu_images/driver_view_richmenu.png"
        self.rich_menu_cache = {}  # 緩存不同分頁的 Rich Menu ID
        
        # 載入按鈕圖片配置
        self.button_images_config = self._load_button_images_config()
        
        # 分頁配置 - 移除符號，只保留文字
        self.tab_configs = {
            "basic": {
                "name": "基本功能",
                "buttons": [
                    {"text": "本週占卜", "action": {"type": "message", "text": "本週占卜"}, "image_key": "weekly_divination"},
                    {"text": "會員資訊", "action": {"type": "message", "text": "會員資訊"}, "image_key": "member_info"},
                    {"text": "命盤綁定", "action": {"type": "message", "text": "命盤綁定"}, "image_key": "chart_binding"}
                ]
            },
            "fortune": {
                "name": "運勢",
                "buttons": [
                    {"text": "流年運勢", "action": {"type": "message", "text": "流年運勢"}, "image_key": "yearly_fortune"},
                    {"text": "流月運勢", "action": {"type": "message", "text": "流月運勢"}, "image_key": "monthly_fortune"},
                    {"text": "流日運勢", "action": {"type": "message", "text": "流日運勢"}, "image_key": "daily_fortune"}
                ]
            },
            "advanced": {
                "name": "進階選項",
                "buttons": [
                    {"text": "指定時間占卜", "action": {"type": "message", "text": "指定時間占卜"}, "image_key": "scheduled_divination"},
                    {"text": "詳細分析", "action": {"type": "message", "text": "詳細分析"}, "image_key": None},  # 暫時沒有對應圖片
                    {"text": "管理功能", "action": {"type": "message", "text": "管理功能"}, "image_key": None}   # 暫時沒有對應圖片
                ]
            }
        }
        
        # 螢幕位置配置 - 使用實際的白色螢幕範圍
        self.tab_positions = [
            {"x": 417, "y": 246, "width": 500, "height": 83},   # 左側螢幕 (實際白色範圍)
            {"x": 1000, "y": 50, "width": 500, "height": 279}, # 中間螢幕 (實際白色範圍)
            {"x": 1583, "y": 266, "width": 500, "height": 63}  # 右側螢幕 (實際白色範圍)
        ]
        
        # 重新設計按鈕位置 - 以中間螢幕 (x=1250) 為中心對齊，增大按鈕尺寸
        middle_screen_center_x = 1250  # 中間螢幕的中心點
        button_width = 750  # 保持按鈕寬度
        button_height = 275  # 增加按鈕高度到 275px (250-300 之間)
        button_spacing = 10  # 進一步縮小間距到 10px
        
        # 計算三個按鈕的起始位置，讓它們以中間螢幕為中心對稱分佈
        total_width = button_width * 3 + button_spacing * 2
        start_x = middle_screen_center_x - total_width // 2
        
        # 中間按鈕往上移動更多，左右按鈕保持原位置（模擬螢幕弧度）
        button_y_side = 720    # 左右按鈕位置
        button_y_center = 695  # 中間按鈕往上移動25px
        
        self.button_positions = [
            {"x": start_x, "y": button_y_side, "width": button_width, "height": button_height},  # 左側按鈕
            {"x": start_x + button_width + button_spacing, "y": button_y_center, "width": button_width, "height": button_height},  # 中間按鈕 (往上)
            {"x": start_x + (button_width + button_spacing) * 2, "y": button_y_side, "width": button_width, "height": button_height}  # 右側按鈕
        ]
    
    def _load_button_images_config(self) -> Dict:
        """載入按鈕圖片配置"""
        try:
            config_path = "user_images/button_image_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("✅ 按鈕圖片配置載入成功")
                    return config
            else:
                logger.warning("⚠️ 按鈕圖片配置檔案不存在")
                return {"button_images": {}, "image_settings": {}}
        except Exception as e:
            logger.error(f"❌ 載入按鈕圖片配置失敗: {e}")
            return {"button_images": {}, "image_settings": {}}
    
    def _create_rotated_text(self, text: str, font, color: tuple, angle: float) -> Optional[Image.Image]:
        """
        創建旋轉的文字圖片
        
        Args:
            text: 文字內容
            font: 字體
            color: 文字顏色 (R, G, B)
            angle: 旋轉角度（正數為順時針，負數為逆時針）
            
        Returns:
            Image.Image: 旋轉後的文字圖片
        """
        try:
            # 創建臨時圖片來測量文字大小
            temp_img = Image.new('RGBA', (1000, 200), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 獲取文字範圍
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 創建合適大小的文字圖片
            padding = 20
            text_img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            
            # 繪製文字
            text_draw.text((padding, padding), text, fill=color, font=font)
            
            # 如果需要旋轉
            if angle != 0:
                text_img = text_img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
            
            return text_img
            
        except Exception as e:
            logger.error(f"❌ 創建旋轉文字失敗: {e}")
            return None
    
    def _ensure_manager(self):
        """確保 RichMenuManager 已初始化"""
        if self.manager is None:
            from app.utils.rich_menu_manager import RichMenuManager
            self.manager = RichMenuManager()
    
    def create_tab_image_with_highlight(self, active_tab: str) -> str:
        """
        創建帶有高亮分頁的圖片 - 使用原圖的螢幕區域，不額外繪製方框
        
        Args:
            active_tab: 當前活躍的分頁 ("basic", "fortune", "advanced")
            
        Returns:
            str: 生成的圖片路徑
        """
        try:
            # 延遲導入 RichMenuManager
            self._ensure_manager()

            # 載入基礎圖片
            base_image = Image.open(self.base_image_path).convert('RGBA')
            
            # 嘗試載入支援中文的字體
            font_large = None
            font_medium = None
            font_small = None
            
            # 嘗試多種中文字體路徑
            chinese_font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS 繁體中文字體
                "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS 簡體中文字體
                "/System/Library/Fonts/Arial Unicode MS.ttf",  # Unicode 字體
                "/System/Library/Fonts/STHeiti Light.ttc",  # 黑體
                "/System/Library/Fonts/AppleGothic.ttf"  # Apple Gothic
            ]
            
            for font_path in chinese_font_paths:
                try:
                    if os.path.exists(font_path):
                        font_large = ImageFont.truetype(font_path, 72)  # 再次增大分頁字體
                        font_medium = ImageFont.truetype(font_path, 60)  # 再次增大分頁字體
                        font_small = ImageFont.truetype(font_path, 28)
                        logger.info(f"✅ 成功載入中文字體: {font_path}")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ 無法載入字體 {font_path}: {e}")
                    continue
            
            # 如果都失敗了，使用預設字體
            if font_medium is None:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
                logger.warning("⚠️ 使用預設字體，中文可能無法正常顯示")

            # 定義分頁標籤
            tabs = ["basic", "fortune", "advanced"]
            tab_names = ["基本功能", "運勢", "進階選項"]
            
            # 為螢幕區域添加分頁文字，確保在白色螢幕範圍內
            for i, (tab_key, tab_name) in enumerate(zip(tabs, tab_names)):
                pos = self.tab_positions[i]
                
                # 計算實際白色螢幕中心位置，並根據螢幕位置調整
                if i == 0:  # 左側螢幕 - 往左移動進入螢幕
                    center_x = pos["x"] + pos["width"] // 2 - 30  # 往左移30px
                    center_y = pos["y"] + pos["height"] // 2 + 10  # 往下移10px
                elif i == 1:  # 中間螢幕 - 往下移動進入螢幕
                    center_x = pos["x"] + pos["width"] // 2
                    center_y = pos["y"] + pos["height"] // 2 + 30  # 往下移30px進入螢幕
                else:  # 右側螢幕 - 往右移動進入螢幕
                    center_x = pos["x"] + pos["width"] // 2 + 30  # 往右移30px
                    center_y = pos["y"] + pos["height"] // 2 + 10  # 往下移10px
                
                # 創建文字圖片，以支援旋轉
                if i == 0:  # 左側螢幕 - 向右傾斜（修正方向）
                    text_img = self._create_rotated_text(tab_name, font_large, 
                                                       (50, 50, 50) if tab_key == active_tab else (150, 150, 150),
                                                       15)  # 右傾 15 度
                elif i == 2:  # 右側螢幕 - 向左傾斜（修正方向）
                    text_img = self._create_rotated_text(tab_name, font_large,
                                                       (50, 50, 50) if tab_key == active_tab else (150, 150, 150),
                                                       -15)   # 左傾 15 度
                else:  # 中間螢幕 - 不傾斜
                    text_img = self._create_rotated_text(tab_name, font_large,
                                                       (50, 50, 50) if tab_key == active_tab else (150, 150, 150),
                                                       0)    # 不傾斜
                
                # 將文字圖片貼到基礎圖片上
                if text_img:
                    text_x = center_x - text_img.width // 2
                    text_y = center_y - text_img.height // 2
                    
                    # 確保文字在螢幕範圍內（實際白色範圍），但允許一些彈性
                    text_x = max(pos["x"] - 50, min(text_x, pos["x"] + pos["width"] - text_img.width + 50))
                    text_y = max(pos["y"] - 20, min(text_y, pos["y"] + pos["height"] - text_img.height + 20))
                    
                    if text_img.mode == 'RGBA':
                        base_image.paste(text_img, (text_x, text_y), text_img)
                    else:
                        base_image.paste(text_img, (text_x, text_y))

            # 繪製當前分頁的功能按鈕（在底部按鈕區域）
            if active_tab in self.tab_configs:
                buttons = self.tab_configs[active_tab]["buttons"]
                
                for i, button_config in enumerate(buttons):
                    if i < len(self.button_positions):
                        btn_pos = self.button_positions[i]
                        btn_text = button_config["text"]
                        image_key = button_config.get("image_key")
                        
                        # 檢查是否有對應的圖片
                        if image_key and image_key in self.button_images_config.get("button_images", {}):
                            # 使用圖片按鈕
                            self._draw_image_button(base_image, btn_pos, btn_text, image_key, font_small)
                        else:
                            # 使用文字按鈕 (備用方案)
                            self._draw_text_button(base_image, btn_pos, btn_text, font_small)

            # 保存圖片
            output_path = f"rich_menu_images/driver_view_{active_tab}_tab.png"
            
            # 確保輸出目錄存在
            os.makedirs("rich_menu_images", exist_ok=True)
            
            # 壓縮圖片以符合 LINE Rich Menu 1MB 限制
            quality = 85
            max_size = 1024 * 1024  # 1MB
            
            while quality > 10:
                # 將圖片轉換為 RGB 模式以支援 JPEG 壓縮
                rgb_image = base_image.convert('RGB')
                
                # 先嘗試用 JPEG 格式（壓縮效果更好）
                temp_path = output_path.replace('.png', '.jpg')
                rgb_image.save(temp_path, "JPEG", quality=quality, optimize=True)
                
                if os.path.getsize(temp_path) <= max_size:
                    logger.info(f"✅ 圖片壓縮成功，品質: {quality}%, 大小: {os.path.getsize(temp_path)/1024:.1f} KB")
                    return temp_path
                
                quality -= 5
            
            # 如果 JPEG 仍然太大，嘗試 PNG
            base_image.convert('RGB').save(output_path, "PNG", optimize=True)
            if os.path.getsize(output_path) <= max_size:
                logger.info(f"✅ PNG 圖片生成成功，大小: {os.path.getsize(output_path)/1024:.1f} KB")
                return output_path
            
            logger.error(f"❌ 無法將圖片壓縮到 1MB 以下")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ 創建分頁圖片時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _draw_image_button(self, base_image: Image.Image, btn_pos: Dict, btn_text: str, image_key: str, font_small):
        """繪製圖片按鈕 - 無邊框，純淨風格"""
        try:
            button_config = self.button_images_config["button_images"][image_key]
            image_file = button_config["image_file"]
            image_path = f"user_images/{image_file}"
            
            if not os.path.exists(image_path):
                logger.warning(f"⚠️ 按鈕圖片不存在: {image_path}")
                self._draw_text_button(base_image, btn_pos, btn_text, font_small)
                return
            
            # 載入按鈕圖片
            button_img = Image.open(image_path).convert("RGBA")
            
            # 計算圖片大小 - 調整為更合適的尺寸
            image_settings = self.button_images_config.get("image_settings", {})
            button_size = image_settings.get("button_size", 380)  # 更新到 380px
            
            # 調整圖片大小，保持比例
            button_img.thumbnail((button_size, button_size), Image.Resampling.LANCZOS)
            
            # 計算圖片和文字的佈局 - 為380px大圖片調整間距
            text_height = 50 if font_small else 35  # 增加文字高度空間
            total_height = button_img.height + text_height + 15  # 圖片 + 更大間隔 + 文字
            
            # 計算垂直置中位置
            start_y = btn_pos["y"] + (btn_pos["height"] - total_height) // 2
            
            # 圖片位置 (水平置中，垂直在上方)
            img_x = btn_pos["x"] + (btn_pos["width"] - button_img.width) // 2
            img_y = start_y
            
            # 確保圖片在按鈕範圍內
            img_x = max(btn_pos["x"], min(img_x, btn_pos["x"] + btn_pos["width"] - button_img.width))
            img_y = max(btn_pos["y"], min(img_y, btn_pos["y"] + btn_pos["height"] - button_img.height))
            
            # 直接貼上按鈕圖片，不加任何邊框
            if button_img.mode == 'RGBA':
                base_image.paste(button_img, (img_x, img_y), button_img)
            else:
                base_image.paste(button_img, (img_x, img_y))
            
            # 添加文字標籤 (在圖片下方)
            draw = ImageDraw.Draw(base_image)
            text_x = btn_pos["x"] + btn_pos["width"] // 2
            text_y = img_y + button_img.height + 12  # 增加間距到12px
            
            # 確保文字在按鈕範圍內
            if text_y + text_height > btn_pos["y"] + btn_pos["height"]:
                text_y = btn_pos["y"] + btn_pos["height"] - text_height
            
            # 使用傳入的字體
            if font_small is None:
                try:
                    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)  # 與圖片按鈕保持一致
                except:
                    font_small = ImageFont.load_default()
            
            # 繪製白色文字，確保在駕駛艙背景上清晰可見
            draw.text((text_x, text_y), btn_text, fill=(255, 255, 255), 
                     font=font_small, anchor="mt")
            
            logger.debug(f"✅ 圖片按鈕繪製成功: {image_key} at ({img_x}, {img_y})")
            
        except Exception as e:
            logger.error(f"❌ 繪製圖片按鈕失敗: {e}")
            # 失敗時使用文字按鈕
            self._draw_text_button(base_image, btn_pos, btn_text, font_small)
    
    def _draw_text_button(self, base_image: Image.Image, btn_pos: Dict, btn_text: str, font_small):
        """繪製文字按鈕 - 簡潔風格，適合駕駛艙主題"""
        try:
            draw = ImageDraw.Draw(base_image)
            
            # 計算按鈕中心
            btn_center_x = btn_pos["x"] + btn_pos["width"] // 2
            btn_center_y = btn_pos["y"] + btn_pos["height"] // 2
            
            # 使用傳入的字體或載入預設字體
            if font_small is None:
                try:
                    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)  # 與圖片按鈕保持一致
                except:
                    font_small = ImageFont.load_default()
            
            # 添加半透明背景，突出文字
            overlay = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # 計算文字範圍
            bbox = draw.textbbox((0, 0), btn_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 繪製圓角矩形背景
            padding = 20
            bg_x1 = btn_center_x - text_width // 2 - padding
            bg_y1 = btn_center_y - text_height // 2 - padding
            bg_x2 = btn_center_x + text_width // 2 + padding
            bg_y2 = btn_center_y + text_height // 2 + padding
            
            # 半透明背景
            overlay_draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], 
                                 fill=(50, 50, 50, 150))  # 深灰半透明
            
            # 合併背景
            base_image = Image.alpha_composite(base_image.convert('RGBA'), overlay)
            draw = ImageDraw.Draw(base_image)
            
            # 繪製白色文字
            draw.text((btn_center_x, btn_center_y), btn_text, 
                     fill=(255, 255, 255), font=font_small, anchor="mm")
            
        except Exception as e:
            logger.error(f"❌ 繪製文字按鈕失敗: {e}")
    
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
            # 確保 manager 已初始化
            self._ensure_manager()
            
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
            # 確保 manager 已初始化
            self._ensure_manager()
            
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
    
    def create_tabbed_rich_menu(self, active_tab: str, user_level: str) -> Tuple[str, List[Dict]]:
        """
        創建分頁式 Rich Menu（與 rich_menu_manager 兼容）
        
        Args:
            active_tab: 當前活躍的分頁
            user_level: 用戶等級（保持兼容性，但在駕駛視窗中不使用）
            
        Returns:
            Tuple[str, List[Dict]]: (圖片路徑, 按鈕區域列表)
        """
        try:
            # 創建分頁圖片
            image_path = self.create_tab_image_with_highlight(active_tab)
            
            # 創建按鈕區域
            button_areas = self.create_button_areas(active_tab)
            
            return image_path, button_areas
            
        except Exception as e:
            logger.error(f"❌ 創建分頁式 Rich Menu 失敗: {e}")
            # 返回基本配置作為備用
            default_image = "rich_menu_images/driver_view_richmenu.png"
            default_areas = self.create_button_areas("basic")
            return default_image, default_areas

# 全局實例
driver_view_handler = DriverViewRichMenuHandler() 