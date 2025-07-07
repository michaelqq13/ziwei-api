"""
分頁式 Rich Menu 生成器
支援三個分頁的選單系統：基本功能、運勢、進階選項
"""
import os
from PIL import Image, ImageDraw, ImageFont
import random
import math
from typing import List, Tuple, Dict, Optional

from app.config.linebot_config import LineBotConfig
from app.utils.rich_menu_image_generator import RichMenuImageGenerator
from app.utils.image_based_rich_menu_generator import ImageBasedRichMenuGenerator

class TabbedRichMenuGenerator:
    """分頁式 Rich Menu 生成器"""
    
    def __init__(self, border_style: str = "soft_glow"):
        """
        初始化分頁式 Rich Menu 生成器
        
        Args:
            border_style: 邊界樣式選項
                - "soft_glow": 柔和發光效果（默認）
                - "subtle_separator": 微妙分隔線
                - "gradient": 漸變邊界
                - "no_border": 無邊框（純粹依靠亮度區分）
        """
        self.width = LineBotConfig.RICH_MENU_WIDTH
        self.height = LineBotConfig.RICH_MENU_HEIGHT
        self.border_style = border_style
        
        # 分頁配置
        self.tab_height = 150  # 分頁標籤高度
        self.content_height = self.height - self.tab_height  # 內容區域高度
        
        # 按鈕配置
        self.button_configs = self._get_button_configs()
        
        # 初始化圖片生成器
        self.image_generator = ImageBasedRichMenuGenerator()
    
    def _get_button_configs(self) -> Dict[str, List[Dict]]:
        """獲取各分頁的按鈕配置"""
        return {
            "basic": [
                {
                    "name": "member_info",
                    "text": "會員資訊",
                    "action_text": "會員資訊",
                    "color": (200, 200, 200),
                    "planet": "月球",
                    "icon": "🌙"
                },
                {
                    "name": "weekly_divination", 
                    "text": "本週占卜",
                    "action_text": "本週占卜",
                    "color": (200, 150, 200),
                    "planet": "水晶球",
                    "icon": "🔮"
                },
                {
                    "name": "chart_binding",
                    "text": "命盤綁定",
                    "action_text": "命盤綁定",
                    "color": (150, 200, 255),
                    "planet": "衛星",
                    "icon": "🛰️"
                }
            ],
            "fortune": [
                {
                    "name": "yearly_fortune",
                    "text": "流年運勢", 
                    "action_text": "流年運勢",
                    "color": (150, 200, 255),
                    "planet": "地球",
                    "icon": "🌍"
                },
                {
                    "name": "monthly_fortune",
                    "text": "流月運勢",
                    "action_text": "流月運勢", 
                    "color": (255, 215, 100),
                    "planet": "土星",
                    "icon": "🪐"
                },
                {
                    "name": "daily_fortune",
                    "text": "流日運勢",
                    "action_text": "流日運勢",
                    "color": (255, 200, 100),
                    "planet": "太陽",
                    "icon": "☀️"
                }
            ],
            "admin": [
                {
                    "name": "scheduled_divination",
                    "text": "指定時間",
                    "action_text": "指定時間占卜",
                    "color": (255, 100, 255),
                    "planet": "時鐘",
                    "icon": "⏰"
                }
            ]
        }
    
    def _get_tab_configs(self, user_level: str) -> List[Dict]:
        """根據用戶等級獲取分頁配置"""
        base_tabs = [
            {
                "name": "basic",
                "text": "基本功能",
                "color": (100, 150, 200),
                "required_level": "free"  # 免費會員可用
            },
            {
                "name": "fortune", 
                "text": "運勢",
                "color": (200, 150, 100),
                "required_level": "premium"  # 付費會員可用
            },
            {
                "name": "admin",
                "text": "進階選項",
                "color": (150, 100, 200),
                "required_level": "admin"  # 管理員專用
            }
        ]
        
        # 根據用戶等級過濾分頁
        available_tabs = []
        for tab in base_tabs:
            if self._check_tab_permission(tab["required_level"], user_level):
                available_tabs.append(tab)
        
        return available_tabs
    
    def _check_tab_permission(self, required_level: str, user_level: str) -> bool:
        """檢查分頁權限"""
        level_hierarchy = {
            "free": 0,
            "premium": 1, 
            "admin": 2
        }
        
        user_level_value = level_hierarchy.get(user_level, 0)
        required_level_value = level_hierarchy.get(required_level, 0)
        
        return user_level_value >= required_level_value
    
    def create_starry_background(self) -> Image.Image:
        """創建星空背景"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(image)
        
        # 繪製漸變背景（從深藍到黑色）
        for y in range(self.height):
            ratio = y / self.height
            r = int(20 * (1 - ratio))
            g = int(25 * (1 - ratio))
            b = int(40 * (1 - ratio))
            color = (r, g, b, 255)
            draw.rectangle([(0, y), (self.width, y + 1)], fill=color)
        
        # 添加星星
        self._add_stars(draw)
        
        return image
    
    def _add_stars(self, draw: ImageDraw.Draw):
        """添加星星效果"""
        # 大星星
        for _ in range(80):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 4)
            brightness = random.randint(180, 255)
            color = (brightness, brightness, brightness, 255)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
        
        # 小星星
        for _ in range(200):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = 1
            brightness = random.randint(100, 180)
            color = (brightness, brightness, brightness, 200)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
    
    def create_tab_menu(self, active_tab: str, user_level: str = "free") -> Tuple[str, List[Dict]]:
        """
        創建分頁選單
        
        Args:
            active_tab: 當前活躍的分頁 ("basic", "fortune", "admin")
            user_level: 用戶等級 ("free", "premium", "admin")
            
        Returns:
            Tuple[str, List[Dict]]: (圖片路徑, 按鈕區域配置)
        """
        # 創建背景
        background = self.create_starry_background()
        draw = ImageDraw.Draw(background)
        
        # 繪製分頁標籤
        self._draw_tabs(draw, active_tab, user_level)
        
        # 繪製內容區域按鈕
        button_areas = self._draw_buttons_on_background(background, active_tab, user_level)
        
        # 保存圖片
        output_path = f"rich_menu_images/tabbed_menu_{active_tab}_{user_level}.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        background.save(output_path)
        
        return output_path, button_areas
    
    def _draw_tabs(self, draw: ImageDraw.Draw, active_tab: str, user_level: str):
        """繪製分頁標籤"""
        # 根據邊界樣式選擇不同的繪製方法
        if self.border_style == "no_border":
            self._draw_no_border_tabs(draw, active_tab, user_level)
            return
        
        # 獲取可用分頁
        tabs = self._get_tab_configs(user_level)
        
        if not tabs:
            return
        
        # 計算每個分頁的寬度
        tab_width = self.width // len(tabs)
        
        # 字體設定
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf", 36)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                font = ImageFont.load_default()
        
        for i, tab in enumerate(tabs):
            # 計算分頁位置
            x_start = i * tab_width
            x_end = (i + 1) * tab_width
            
            # 分頁顏色
            is_active = tab["name"] == active_tab
            if is_active:
                # 活躍分頁：使用較亮的星空背景
                self._draw_tab_starry_background(draw, x_start, x_end, brightness=1.2)
                text_color = (255, 255, 255, 255)
                
                # 根據樣式繪製邊界
                if self.border_style == "soft_glow":
                    self._draw_soft_glow_border(draw, x_start, x_end, 0, self.tab_height, 
                                               glow_color=(255, 255, 255), glow_intensity=0.5)
                elif self.border_style == "gradient":
                    self._draw_gradient_border(draw, x_start, x_end, 0, self.tab_height, 
                                             border_color=(255, 255, 255), fade_distance=15)
            else:
                # 非活躍分頁：使用較暗的星空背景
                self._draw_tab_starry_background(draw, x_start, x_end, brightness=0.7)
                text_color = (200, 200, 200, 255)
                
                # 根據樣式繪製分隔效果
                if self.border_style == "subtle_separator":
                    self._draw_subtle_separator(draw, x_start, x_end, 0, self.tab_height)
            
            # 繪製分頁文字（移除符號）
            text = tab['text']
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = x_start + (tab_width - text_width) // 2
            text_y = (self.tab_height - text_height) // 2
            
            draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    def _draw_tab_starry_background(self, draw: ImageDraw.Draw, x_start: int, x_end: int, brightness: float = 1.0):
        """為分頁標籤繪製星空背景"""
        # 繪製漸變背景（從深藍到黑色）
        for y in range(self.tab_height):
            ratio = y / self.tab_height
            base_r = int(20 * (1 - ratio) * brightness)
            base_g = int(25 * (1 - ratio) * brightness)
            base_b = int(40 * (1 - ratio) * brightness)
            color = (base_r, base_g, base_b, 255)
            draw.rectangle([(x_start, y), (x_end, y + 1)], fill=color)
        
        # 添加星星（在分頁範圍內）
        tab_width = x_end - x_start
        
        # 小星星
        for _ in range(int(15 * brightness)):
            x = random.randint(x_start, x_end)
            y = random.randint(0, self.tab_height)
            size = 1
            star_brightness = int(random.randint(100, 180) * brightness)
            color = (star_brightness, star_brightness, star_brightness, 200)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
        
        # 大星星
        for _ in range(int(5 * brightness)):
            x = random.randint(x_start, x_end)
            y = random.randint(0, self.tab_height)
            size = random.randint(2, 3)
            star_brightness = int(random.randint(180, 255) * brightness)
            color = (star_brightness, star_brightness, star_brightness, 255)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
    
    def _draw_soft_glow_border(self, draw: ImageDraw.Draw, x_start: int, x_end: int, 
                              y_start: int, y_end: int, glow_color: Tuple[int, int, int], 
                              glow_intensity: float = 0.5):
        """繪製柔和的發光邊界效果（增強版）"""
        # 繪製多層漸變邊界來模擬發光效果
        for layer in range(5):  # 增加層數
            alpha = int(255 * glow_intensity * (1 - layer * 0.2))
            width = layer + 1
            
            # 只在底部繪製發光線條
            for offset in range(width):
                line_alpha = int(alpha * (1 - offset / width))
                color = (*glow_color, line_alpha)
                
                # 底部發光線（增強效果）
                y_pos = y_end - offset
                if y_pos >= y_start:
                    draw.line([(x_start, y_pos), (x_end, y_pos)], 
                             fill=color, width=2)  # 增加線條寬度
                    
                    # 添加額外的發光效果
                    if layer < 2:
                        inner_glow_color = (*glow_color, int(line_alpha * 0.3))
                        draw.line([(x_start + 5, y_pos), (x_end - 5, y_pos)], 
                                 fill=inner_glow_color, width=1)
    
    def _draw_subtle_separator(self, draw: ImageDraw.Draw, x_start: int, x_end: int, 
                              y_start: int, y_end: int):
        """繪製微妙的分隔線（增強版）"""
        # 只在分頁之間繪製垂直分隔線
        if x_start > 0:  # 不是第一個分頁
            # 繪製更明顯的漸變分隔線
            for y in range(y_start + 10, y_end - 10):  # 覆蓋更多高度
                ratio = abs(y - (y_start + y_end) / 2) / ((y_end - y_start) / 2)
                alpha = int(180 * (1 - ratio))  # 增加不透明度
                color = (150, 170, 200, alpha)  # 更明顯的顏色
                
                # 繪製多像素寬度的分隔線
                for x_offset in range(3):
                    draw.point((x_start + x_offset, y), fill=color)
    
    def _draw_gradient_border(self, draw: ImageDraw.Draw, x_start: int, x_end: int, 
                             y_start: int, y_end: int, border_color: Tuple[int, int, int], 
                             fade_distance: int = 15):
        """繪製漸變邊界（增強版）"""
        # 底部漸變邊界
        for i in range(fade_distance):
            alpha = int(255 * (1 - i / fade_distance))
            color = (*border_color, alpha)
            y_pos = y_end - i
            if y_pos >= y_start:
                # 繪製更寬的漸變線
                draw.line([(x_start, y_pos), (x_end, y_pos)], fill=color, width=3)
                
                # 添加內部漸變效果
                if i < fade_distance // 2:
                    inner_color = (border_color[0], border_color[1], border_color[2], int(alpha * 0.5))
                    draw.line([(x_start + 10, y_pos), (x_end - 10, y_pos)], 
                             fill=inner_color, width=1)
    
    def _draw_no_border_tabs(self, draw: ImageDraw.Draw, active_tab: str, user_level: str):
        """繪製無邊框的分頁標籤（增強亮度對比）"""
        # 獲取可用分頁
        tabs = self._get_tab_configs(user_level)
        
        if not tabs:
            return
        
        # 計算每個分頁的寬度
        tab_width = self.width // len(tabs)
        
        # 字體設定
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf", 36)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                font = ImageFont.load_default()
        
        for i, tab in enumerate(tabs):
            # 計算分頁位置
            x_start = i * tab_width
            x_end = (i + 1) * tab_width
            
            # 分頁顏色（增強亮度對比）
            is_active = tab["name"] == active_tab
            if is_active:
                # 活躍分頁：使用非常亮的星空背景
                self._draw_tab_starry_background(draw, x_start, x_end, brightness=2.0)
                text_color = (255, 255, 255, 255)
            else:
                # 非活躍分頁：使用非常暗的星空背景
                self._draw_tab_starry_background(draw, x_start, x_end, brightness=0.4)
                text_color = (120, 120, 120, 255)
            
            # 繪製分頁文字
            text = tab['text']
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = x_start + (tab_width - text_width) // 2
            text_y = (self.tab_height - text_height) // 2
            
            draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    def _draw_buttons_on_background(self, background: Image.Image, active_tab: str, user_level: str) -> List[Dict]:
        """在背景上繪製按鈕"""
        content_y_start = self.tab_height
        
        # 獲取當前分頁的按鈕配置
        buttons = self.button_configs.get(active_tab, [])
        
        if not buttons:
            return []
        
        # 計算最佳按鈕大小
        optimal_button_size = self._calculate_optimal_button_size(buttons, content_y_start)
        
        # 計算按鈕位置（三個按鈕水平並排在中央）
        button_positions = self._calculate_horizontal_button_positions(buttons, content_y_start)
        
        # 繪製按鈕
        button_areas = []
        for i, button_config in enumerate(buttons):
            if i < len(button_positions):
                x, y = button_positions[i]
                
                self._draw_enhanced_planet_button(background, x, y, button_config, optimal_button_size)
                
                # 添加按鈕區域配置，使用圖片按鈕的實際尺寸
                actual_button_size = optimal_button_size * 2  # 實際按鈕尺寸
                button_areas.append({
                    "bounds": {
                        "x": max(0, x - actual_button_size // 2),
                        "y": max(0, y - actual_button_size // 2),
                        "width": actual_button_size,
                        "height": actual_button_size
                    },
                    "action": {
                        "type": "message",
                        "text": button_config["action_text"]
                    }
                })
        
        # 添加分頁切換區域
        self._add_tab_switch_areas(button_areas, user_level)
        
        return button_areas
    
    def _calculate_optimal_button_size(self, buttons: List[Dict], content_y_start: int) -> int:
        """計算最佳按鈕大小"""
        num_buttons = len(buttons)
        content_height = self.content_height
        content_width = self.width
        
        # 設定邊距和間距
        margin = 100  # 邊距
        min_spacing = 50  # 按鈕間最小間距
        
        if num_buttons <= 3:
            # 水平排列：計算基於寬度的最大按鈕尺寸
            available_width = content_width - 2 * margin
            max_button_width = (available_width - (num_buttons - 1) * min_spacing) // num_buttons
            
            # 計算基於高度的最大按鈕尺寸
            available_height = content_height - 2 * margin
            max_button_height = available_height
            
            # 取較小值，確保按鈕不會超出範圍
            max_button_size = min(max_button_width, max_button_height)
            
            # 限制按鈕大小範圍（考慮到ImageBasedRichMenuGenerator會放大2倍）
            min_size = 80   # 最小80像素
            max_size = 200  # 最大200像素（實際顯示400像素）
            
            optimal_size = max(min_size, min(max_size, max_button_size))
            
        else:
            # 多於3個按鈕：使用兩行佈局
            buttons_per_row = (num_buttons + 1) // 2
            
            # 計算每行的最大按鈕尺寸
            available_width = content_width - 2 * margin
            max_button_width = (available_width - (buttons_per_row - 1) * min_spacing) // buttons_per_row
            
            # 計算兩行的最大按鈕尺寸
            available_height = content_height - 2 * margin
            max_button_height = (available_height - min_spacing) // 2  # 兩行之間的間距
            
            max_button_size = min(max_button_width, max_button_height)
            
            # 限制按鈕大小範圍
            min_size = 60   # 多按鈕時稍微小一些
            max_size = 150  # 多按鈕時最大150像素
            
            optimal_size = max(min_size, min(max_size, max_button_size))
        
        print(f"🎯 按鈕數量: {num_buttons}, 計算出的最佳按鈕大小: {optimal_size}px (實際顯示: {optimal_size * 2}px)")
        return optimal_size

    def _calculate_horizontal_button_positions(self, buttons: List[Dict], content_y_start: int) -> List[Tuple[int, int]]:
        """計算水平並排按鈕位置"""
        num_buttons = len(buttons)
        content_center_y = content_y_start + self.content_height // 2
        
        # 設定更智能的間距
        margin = 150  # 增加邊距
        
        if num_buttons == 1:
            # 單個按鈕：置中
            return [(self.width // 2, content_center_y)]
        elif num_buttons == 2:
            # 兩個按鈕：左右對稱，增加間距
            spacing = self.width // 3
            return [
                (spacing, content_center_y),
                (self.width - spacing, content_center_y)
            ]
        elif num_buttons == 3:
            # 三個按鈕：左中右，優化間距
            left_x = margin + 200  # 左側位置
            right_x = self.width - margin - 200  # 右側位置
            center_x = self.width // 2  # 中央位置
            
            return [
                (left_x, content_center_y),    # 左
                (center_x, content_center_y),  # 中
                (right_x, content_center_y)    # 右
            ]
        else:
            # 超過三個按鈕：分兩行，優化垂直間距
            row_spacing = self.content_height // 4  # 行間距
            row1_y = content_y_start + row_spacing
            row2_y = content_y_start + self.content_height - row_spacing
            
            positions = []
            buttons_per_row = (num_buttons + 1) // 2
            
            for i in range(num_buttons):
                if i < buttons_per_row:
                    # 第一行：均勻分佈
                    x = margin + (i + 1) * (self.width - 2 * margin) // (buttons_per_row + 1)
                    positions.append((x, row1_y))
                else:
                    # 第二行：均勻分佈
                    row_index = i - buttons_per_row
                    remaining_buttons = num_buttons - buttons_per_row
                    x = margin + (row_index + 1) * (self.width - 2 * margin) // (remaining_buttons + 1)
                    positions.append((x, row2_y))
            
            return positions
    
    def _draw_enhanced_planet_button(self, background: Image.Image, x: int, y: int, button_config: Dict, button_size: int):
        """繪製增強版星球按鈕，使用用戶自定義圖片"""
        # 使用ImageBasedRichMenuGenerator創建按鈕
        button_name = button_config.get("name", "")
        
        # 創建按鈕圖片
        button_img = self.image_generator.create_image_button(button_name, button_config)
        
        # 調整按鈕大小以適應分頁選單
        target_size = button_size * 2  # 因為ImageBasedRichMenuGenerator創建的是較大的按鈕
        if button_img.width != target_size or button_img.height != target_size:
            button_img = button_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # 計算按鈕位置（居中）
        paste_x = x - button_img.width // 2
        paste_y = y - button_img.height // 2
        
        # 確保按鈕不會超出背景範圍
        paste_x = max(0, min(paste_x, background.width - button_img.width))
        paste_y = max(0, min(paste_y, background.height - button_img.height))
        
        # 將按鈕貼到背景上
        if button_img.mode == 'RGBA':
            background.paste(button_img, (paste_x, paste_y), button_img)
        else:
            background.paste(button_img, (paste_x, paste_y))
    
    def _add_tab_switch_areas(self, button_areas: List[Dict], user_level: str):
        """添加分頁切換區域"""
        # 獲取可用分頁
        tabs = self._get_tab_configs(user_level)
        
        if not tabs:
            return
        
        # 計算每個分頁的寬度
        tab_width = self.width // len(tabs)
        
        # 為每個可用分頁添加切換區域
        for i, tab in enumerate(tabs):
            x_start = i * tab_width
            
            button_areas.append({
                "bounds": {
                    "x": x_start,
                    "y": 0,
                    "width": tab_width,
                    "height": self.tab_height
                },
                "action": {
                    "type": "message",
                    "text": f"切換到{tab['text']}"
                }
            })

# 全局實例
tabbed_rich_menu_generator = TabbedRichMenuGenerator()

def generate_tabbed_rich_menu(active_tab: str, user_level: str, border_style: str = "soft_glow") -> Tuple[str, List[Dict]]:
    """
    生成分頁式 Rich Menu
    
    Args:
        active_tab: 當前活躍的分頁 ("basic", "fortune", "admin")
        user_level: 用戶等級 ("free", "premium", "admin")
        border_style: 邊界樣式 ("soft_glow", "subtle_separator", "gradient", "no_border")
        
    Returns:
        Tuple[str, List[Dict]]: (圖片路徑, 按鈕區域配置)
    """
    # 如果需要不同的邊界樣式，創建新的生成器實例
    if border_style != "soft_glow":
        generator = TabbedRichMenuGenerator(border_style=border_style)
        return generator.create_tab_menu(active_tab, user_level)
    else:
        return tabbed_rich_menu_generator.create_tab_menu(active_tab, user_level)

def set_default_border_style(border_style: str):
    """
    設置默認邊界樣式
    
    Args:
        border_style: 邊界樣式選項
            - "soft_glow": 柔和發光效果
            - "subtle_separator": 微妙分隔線  
            - "gradient": 漸變邊界
            - "no_border": 無邊框
    """
    global tabbed_rich_menu_generator
    tabbed_rich_menu_generator = TabbedRichMenuGenerator(border_style=border_style)
    print(f"✅ 已設置默認邊界樣式為: {border_style}")

def get_available_border_styles() -> List[str]:
    """獲取可用的邊界樣式列表"""
    return ["soft_glow", "subtle_separator", "gradient", "no_border"] 