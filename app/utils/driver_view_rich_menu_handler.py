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
        self.base_image_path = "rich_menu_images/drive_view.jpg"  # 使用壓縮後的駕駛視窗圖片
        self.rich_menu_cache = {}  # 緩存不同分頁的 Rich Menu ID
        
        # 載入按鈕圖片配置
        self.button_images_config = self._load_button_images_config()
        
        # 設置版本號，用於緩存管理
        self.menu_version = "v2.1"  # 每次重大修改時增加版本號
        
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
        
        # 重新設計按鈕位置 - 移到白色螢幕下方區域，而不是儀表板位置
        # 使用三個白色螢幕的下方區域
        left_screen_center_x = 417 + 250   # 左側螢幕中心
        middle_screen_center_x = 1000 + 250  # 中間螢幕中心
        right_screen_center_x = 1583 + 250   # 右側螢幕中心
        
        button_width = 400  # 縮小按鈕寬度以適應螢幕
        button_height = 200  # 縮小按鈕高度
        left_buttons_y = 490  # 左側按鈕往下移動10px，確保不壓到螢幕 (原480 + 10)
        middle_buttons_y = 465  # 中間按鈕往下移動5px，確保不壓到螢幕 (原460 + 5)
        right_buttons_y = 490  # 右側按鈕往下移動10px，確保不壓到螢幕 (原480 + 10)
        
        self.button_positions = [
            {"x": left_screen_center_x - button_width // 2, "y": left_buttons_y, "width": button_width, "height": button_height},  # 左側按鈕
            {"x": middle_screen_center_x - button_width // 2, "y": middle_buttons_y, "width": button_width, "height": button_height},  # 中間按鈕
            {"x": right_screen_center_x - button_width // 2, "y": right_buttons_y, "width": button_width, "height": button_height}  # 右側按鈕
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
                        font_large = ImageFont.truetype(font_path, 45)  # 分頁字體改回原來大小 45px
                        font_medium = ImageFont.truetype(font_path, 40)  # 分頁字體改回原來大小 40px
                        font_small = ImageFont.truetype(font_path, 48)  # 按鈕字體保持48px
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
                
                # 重新計算分頁文字位置，確保完全在白色螢幕內
                if i == 0:  # 左側螢幕 (x=417, y=246, w=500, h=83) - 最小螢幕
                    # 文字位置稍微往右下移動，確保在螢幕內
                    center_x = pos["x"] + pos["width"] // 2  # 417 + 250 = 667
                    center_y = pos["y"] + pos["height"] // 2 + 10  # 246 + 41 + 10 = 297，往下移10px
                elif i == 1:  # 中間螢幕 (x=1000, y=50, w=500, h=279) - 最大螢幕
                    center_x = pos["x"] + pos["width"] // 2  # 1000 + 250 = 1250
                    center_y = pos["y"] + pos["height"] // 2  # 50 + 139 = 189，中心位置
                else:  # 右側螢幕 (x=1583, y=266, w=500, h=63) - 最小螢幕
                    # 文字位置稍微往左下移動，確保在螢幕內
                    center_x = pos["x"] + pos["width"] // 2  # 1583 + 250 = 1833
                    center_y = pos["y"] + pos["height"] // 2 + 5  # 266 + 31 + 5 = 302，往下移5px
                
                # 創建文字圖片，以支援旋轉
                if i == 0:  # 左側螢幕 - 基本功能，向右傾斜15度
                    text_img = self._create_rotated_text(tab_name, font_large, 
                                                       (50, 50, 50) if tab_key == active_tab else (150, 150, 150),
                                                       15)   # 右傾 15 度
                elif i == 2:  # 右側螢幕 - 進階選項，向左傾斜15度
                    text_img = self._create_rotated_text(tab_name, font_large,
                                                       (50, 50, 50) if tab_key == active_tab else (150, 150, 150),
                                                       -15)  # 左傾 15 度
                else:  # 中間螢幕 - 不傾斜
                    text_img = self._create_rotated_text(tab_name, font_large,
                                                       (50, 50, 50) if tab_key == active_tab else (150, 150, 150),
                                                       0)    # 不傾斜
                
                # 將文字圖片貼到基礎圖片上
                if text_img:
                    text_x = center_x - text_img.width // 2
                    text_y = center_y - text_img.height // 2
                    
                    # 根據螢幕大小調整文字位置限制
                    if i == 0:  # 左側螢幕 - 最小螢幕，限制更嚴格
                        text_x = max(pos["x"] + 10, min(text_x, pos["x"] + pos["width"] - text_img.width - 10))
                        text_y = max(pos["y"] + 5, min(text_y, pos["y"] + pos["height"] - text_img.height - 5))
                    elif i == 1:  # 中間螢幕 - 最大螢幕，限制較寬鬆
                        text_x = max(pos["x"] + 20, min(text_x, pos["x"] + pos["width"] - text_img.width - 20))
                        text_y = max(pos["y"] + 10, min(text_y, pos["y"] + pos["height"] - text_img.height - 10))
                    else:  # 右側螢幕 - 最小螢幕，限制更嚴格
                        text_x = max(pos["x"] + 10, min(text_x, pos["x"] + pos["width"] - text_img.width - 10))
                        text_y = max(pos["y"] + 5, min(text_y, pos["y"] + pos["height"] - text_img.height - 5))
                    
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
            max_size = 800 * 1024  # 設定為800KB以確保不超過1MB
            attempt = 0
            max_attempts = 10
            
            while quality > 20 and attempt < max_attempts:
                attempt += 1
                
                # 將圖片轉換為 RGB 模式以支援 JPEG 壓縮
                rgb_image = base_image.convert('RGB')
                
                # 使用 JPEG 格式（壓縮效果更好）
                temp_path = output_path.replace('.png', '.jpg')
                rgb_image.save(temp_path, "JPEG", quality=quality, optimize=True)
                
                file_size = os.path.getsize(temp_path)
                logger.info(f"🔄 嘗試 {attempt}: 品質 {quality}%, 大小: {file_size/1024:.1f} KB")
                
                if file_size <= max_size:
                    logger.info(f"✅ 圖片壓縮成功，品質: {quality}%, 大小: {file_size/1024:.1f} KB")
                    return temp_path
                
                # 如果還是太大，降低品質或縮小圖片
                if quality > 50:
                    quality -= 10
                elif quality > 30:
                    quality -= 5
                else:
                    # 縮小圖片尺寸
                    base_image = base_image.resize((int(base_image.width * 0.9), int(base_image.height * 0.9)), Image.Resampling.LANCZOS)
                    quality = 85  # 重設品質
                    logger.info(f"🔄 縮小圖片尺寸到: {base_image.width}x{base_image.height}")
            
            logger.error(f"❌ 無法將圖片壓縮到 {max_size/1024:.0f}KB 以下")
            return temp_path if 'temp_path' in locals() else None
            
        except Exception as e:
            logger.error(f"❌ 創建分頁圖片時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _draw_image_button(self, base_image: Image.Image, btn_pos: Dict, btn_text: str, image_key: str, font_small):
        """繪製圖片按鈕 - 直接使用user_images中的現有圖片"""
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
            
            # 計算圖片大小 - 使用配置中的尺寸
            image_settings = self.button_images_config.get("image_settings", {})
            button_size = image_settings.get("button_size", 120)  # 縮小圖片尺寸，為文字留空間
            
            # 調整圖片大小，保持比例
            button_img.thumbnail((button_size, button_size), Image.Resampling.LANCZOS)
            
            # 圖片位置 (在按鈕中心)
            img_x = btn_pos["x"] + (btn_pos["width"] - button_img.width) // 2
            img_y = btn_pos["y"] + (btn_pos["height"] - button_img.height) // 2
            
            # 確保圖片在按鈕範圍內
            img_x = max(btn_pos["x"], min(img_x, btn_pos["x"] + btn_pos["width"] - button_img.width))
            img_y = max(btn_pos["y"], min(img_y, btn_pos["y"] + btn_pos["height"] - button_img.height))
            
            # 直接貼上按鈕圖片
            if button_img.mode == 'RGBA':
                base_image.paste(button_img, (img_x, img_y), button_img)
            else:
                base_image.paste(button_img, (img_x, img_y))
            
            # 添加文字標籤 (在按鈕底下)
            draw = ImageDraw.Draw(base_image)
            text_x = btn_pos["x"] + btn_pos["width"] // 2  # 文字水平居中於按鈕
            text_y = btn_pos["y"] + btn_pos["height"] + 20  # 文字在按鈕底部下方20px
            
            # 增大字體尺寸，讓說明文字更清楚
            try:
                text_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 56)  # 增大說明文字字體到56px
            except:
                text_font = font_small if font_small else ImageFont.load_default()
            
            # 繪製黑色文字，在按鈕底下居中
            draw.text((text_x, text_y), btn_text, fill=(0, 0, 0), 
                     font=text_font, anchor="mt")  # 使用 "mt" 錨點：中間頂部對齊
            
            logger.debug(f"✅ 圖片按鈕繪製成功: {image_key} at 圖片({img_x}, {img_y}), 文字({text_x}, {text_y})")
            
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
            
            # 使用傳入的字體或載入預設字體，優先使用主函數傳入的font_small
            if font_small is None:
                try:
                    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)  # 備用字體大小48px
                except:
                    font_small = ImageFont.load_default()
            # 如果font_small已有值，就直接使用，不重新載入
            
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
    
    def clear_cache(self):
        """清空內部緩存"""
        try:
            self.rich_menu_cache.clear()
            logger.info("✅ 駕駛視窗選單緩存已清空")
        except Exception as e:
            logger.error(f"❌ 清空緩存失敗: {e}")
    
    def validate_cached_menu(self, menu_id: str) -> bool:
        """
        驗證緩存的選單是否仍然存在於 LINE 平台
        
        Args:
            menu_id: Rich Menu ID
            
        Returns:
            bool: 選單是否存在
        """
        try:
            self._ensure_manager()
            existing_menus = self.manager.get_rich_menu_list()
            if existing_menus:
                for menu in existing_menus:
                    if menu.get("richMenuId") == menu_id:
                        # 檢查選單名稱是否包含當前版本
                        menu_name = menu.get("name", "")
                        if self.menu_version in menu_name:
                            return True
                        else:
                            logger.info(f"🔄 發現舊版本選單: {menu_name}")
                            return False
            return False
        except Exception as e:
            logger.error(f"❌ 驗證緩存選單失敗: {e}")
            return False
    
    def cleanup_old_driver_menus(self, keep_current_version: bool = True) -> int:
        """
        清理舊的駕駛視窗選單
        
        Args:
            keep_current_version: 是否保留當前版本的選單
            
        Returns:
            int: 清理的選單數量
        """
        try:
            self._ensure_manager()
            all_menus = self.manager.get_rich_menu_list()
            if not all_menus:
                logger.info("📋 沒有找到任何 Rich Menu")
                return 0
            
            # 篩選駕駛視窗選單
            driver_menus = []
            for menu in all_menus:
                menu_name = menu.get("name", "")
                if ("DriverView" in menu_name or 
                    "driver_view" in menu_name.lower() or
                    "駕駛視窗" in menu_name):
                    driver_menus.append(menu)
            
            if not driver_menus:
                logger.info("📋 沒有找到駕駛視窗選單")
                return 0
            
            logger.info(f"📋 找到 {len(driver_menus)} 個駕駛視窗選單")
            
            deleted_count = 0
            current_cache_values = set(self.rich_menu_cache.values())
            
            for menu in driver_menus:
                menu_id = menu.get("richMenuId")
                menu_name = menu.get("name", "")
                
                should_delete = False
                
                if keep_current_version:
                    # 檢查是否為舊版本
                    if self.menu_version not in menu_name:
                        should_delete = True
                        logger.info(f"🗑️ 標記刪除（舊版本）: {menu_name}")
                    # 檢查是否不在當前緩存中
                    elif menu_id not in current_cache_values:
                        should_delete = True
                        logger.info(f"🗑️ 標記刪除（未使用）: {menu_name}")
                else:
                    # 刪除所有駕駛視窗選單
                    should_delete = True
                    logger.info(f"🗑️ 標記刪除（全部清理）: {menu_name}")
                
                if should_delete:
                    if self.manager.delete_rich_menu(menu_id):
                        deleted_count += 1
                        logger.info(f"✅ 已刪除: {menu_name} ({menu_id})")
                        
                        # 從緩存中移除
                        for cache_key, cached_id in list(self.rich_menu_cache.items()):
                            if cached_id == menu_id:
                                del self.rich_menu_cache[cache_key]
                                logger.info(f"🧹 從緩存移除: {cache_key}")
                    else:
                        logger.warning(f"⚠️ 刪除失敗: {menu_name} ({menu_id})")
                else:
                    logger.info(f"✅ 保留選單: {menu_name}")
            
            logger.info(f"🧹 清理完成！刪除了 {deleted_count} 個舊選單")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 清理舊選單失敗: {e}")
            return 0
    
    def force_refresh_menu(self, tab_name: str) -> Optional[str]:
        """
        強制刷新指定分頁的選單（清除緩存並重新創建）
        
        Args:
            tab_name: 分頁名稱
            
        Returns:
            str: 新的 Rich Menu ID
        """
        try:
            cache_key = f"driver_view_{tab_name}"
            
            # 清除緩存中的舊選單
            if cache_key in self.rich_menu_cache:
                old_menu_id = self.rich_menu_cache[cache_key]
                logger.info(f"🔄 清除舊緩存: {cache_key} -> {old_menu_id}")
                del self.rich_menu_cache[cache_key]
                
                # 嘗試刪除舊選單
                self._ensure_manager()
                if self.manager.delete_rich_menu(old_menu_id):
                    logger.info(f"✅ 刪除舊選單: {old_menu_id}")
                else:
                    logger.warning(f"⚠️ 刪除舊選單失敗: {old_menu_id}")
            
            # 創建新選單
            new_menu_id = self.create_tab_rich_menu(tab_name)
            if new_menu_id:
                logger.info(f"✅ 強制刷新成功: {tab_name} -> {new_menu_id}")
            else:
                logger.error(f"❌ 強制刷新失敗: {tab_name}")
            
            return new_menu_id
            
        except Exception as e:
            logger.error(f"❌ 強制刷新選單失敗: {e}")
            return None
    
    def get_cache_status(self) -> Dict:
        """
        獲取緩存狀態資訊
        
        Returns:
            Dict: 緩存狀態
        """
        try:
            cache_status = {
                "version": self.menu_version,
                "cached_menus": len(self.rich_menu_cache),
                "cache_details": {}
            }
            
            # 驗證每個緩存的選單
            self._ensure_manager()
            for cache_key, menu_id in self.rich_menu_cache.items():
                is_valid = self.validate_cached_menu(menu_id)
                cache_status["cache_details"][cache_key] = {
                    "menu_id": menu_id,
                    "is_valid": is_valid
                }
            
            return cache_status
            
        except Exception as e:
            logger.error(f"❌ 獲取緩存狀態失敗: {e}")
            return {"error": str(e)}

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
            rich_menu_id = None
            
            if cache_key in self.rich_menu_cache:
                cached_id = self.rich_menu_cache[cache_key]
                # 驗證緩存的選單是否仍然有效
                if self.validate_cached_menu(cached_id):
                    rich_menu_id = cached_id
                    logger.info(f"✅ 使用有效的緩存 Rich Menu: {rich_menu_id}")
                else:
                    logger.info(f"🔄 緩存的選單已無效，將重新創建: {cached_id}")
                    del self.rich_menu_cache[cache_key]
            
            # 如果沒有有效的緩存選單，創建新的
            if not rich_menu_id:
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
            
            # 創建 Rich Menu 配置 - 包含版本號
            tab_display_name = self.tab_configs.get(tab_name, {}).get("name", tab_name)
            rich_menu_config = {
                "size": {
                    "width": LineBotConfig.RICH_MENU_WIDTH,
                    "height": LineBotConfig.RICH_MENU_HEIGHT
                },
                "selected": True,
                "name": f"DriverView_{tab_name}_{self.menu_version}",  # 加入版本號
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
    
    def setup_default_tab(self, user_id: str, tab_name: str = "basic", force_refresh: bool = False) -> bool:
        """
        為用戶設定預設分頁
        
        Args:
            user_id: 用戶 ID
            tab_name: 預設分頁名稱
            force_refresh: 是否強制刷新選單
            
        Returns:
            bool: 是否成功設定
        """
        try:
            if force_refresh:
                # 強制刷新選單
                menu_id = self.force_refresh_menu(tab_name)
                if menu_id:
                    self._ensure_manager()
                    return self.manager.set_user_rich_menu(user_id, menu_id)
                else:
                    return False
            else:
                # 使用普通切換
                return self.switch_to_tab(user_id, tab_name)
        except Exception as e:
            logger.error(f"❌ 設定預設分頁失敗: {e}")
            return False
    
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
            default_image = "rich_menu_images/drive_view.jpg"  # 使用壓縮後的駕駛視窗圖片
            default_areas = self.create_button_areas("basic")
            return default_image, default_areas

# 全局實例
driver_view_handler = DriverViewRichMenuHandler() 