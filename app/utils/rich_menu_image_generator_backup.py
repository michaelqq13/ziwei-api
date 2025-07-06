"""
Rich Menu 圖片生成器
生成星空主題的選單圖片，包含星球按鈕
"""
import os
from PIL import Image, ImageDraw, ImageFont
import random
import math
from typing import List, Tuple, Dict

from app.config.linebot_config import LineBotConfig

class RichMenuImageGenerator:
    """Rich Menu 圖片生成器"""
    
    def __init__(self):
        self.width = LineBotConfig.RICH_MENU_WIDTH
        self.height = LineBotConfig.RICH_MENU_HEIGHT
        self.buttons = LineBotConfig.RICH_MENU_BUTTONS
        
    def create_starry_background(self) -> Image.Image:
        """
        創建星空背景
        """
        # 創建基礎圖片 - 深空藍到黑色的漸變
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(image)
        
        # 繪製漸變背景（從深藍到黑色）
        for y in range(self.height):
            # 計算漸變色
            ratio = y / self.height
            
            # 深藍到黑色漸變
            r = int(20 * (1 - ratio))  # 深紅色分量
            g = int(25 * (1 - ratio))  # 深綠色分量  
            b = int(40 * (1 - ratio))  # 深藍色分量
            
            color = (r, g, b, 255)
            draw.rectangle([(0, y), (self.width, y + 1)], fill=color)
        
        # 添加星星
        self._add_stars(draw)
        
        # 添加星雲效果
        self._add_nebula_effects(image)
        
        return image
    
    def _add_stars(self, draw: ImageDraw.Draw):
        """
        添加星星效果
        """
        # 大星星 (較亮)
        for _ in range(80):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 4)
            brightness = random.randint(180, 255)
            
            # 白色星星
            color = (brightness, brightness, brightness, 255)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
            
            # 添加星芒效果（十字光芒）
            if size >= 3:
                beam_length = size * 3
                draw.line([(x-beam_length, y), (x+beam_length, y)], 
                         fill=(brightness//2, brightness//2, brightness//2, 128), width=1)
                draw.line([(x, y-beam_length), (x, y+beam_length)], 
                         fill=(brightness//2, brightness//2, brightness//2, 128), width=1)
        
        # 小星星 (較暗)
        for _ in range(200):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = 1
            brightness = random.randint(100, 180)
            
            color = (brightness, brightness, brightness, 200)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
    
    def _add_nebula_effects(self, image: Image.Image):
        """
        添加星雲效果
        """
        # 創建星雲覆蓋層
        nebula_overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        nebula_draw = ImageDraw.Draw(nebula_overlay)
        
        # 添加幾個星雲區域
        nebula_areas = [
            {"center": (400, 300), "radius": 300, "color": (100, 50, 150, 30)},  # 紫色星雲
            {"center": (2000, 800), "radius": 250, "color": (50, 100, 150, 25)},  # 藍色星雲
            {"center": (1200, 1400), "radius": 200, "color": (150, 100, 50, 20)}, # 橙色星雲
        ]
        
        for nebula in nebula_areas:
            center_x, center_y = nebula["center"]
            radius = nebula["radius"]
            color = nebula["color"]
            
            # 繪製漸變的圓形星雲
            for r in range(radius, 0, -10):
                alpha = int(color[3] * (radius - r) / radius)
                current_color = (color[0], color[1], color[2], alpha)
                
                nebula_draw.ellipse([
                    (center_x - r, center_y - r),
                    (center_x + r, center_y + r)
                ], fill=current_color)
        
        # 混合星雲效果到主圖片
        image.alpha_composite(nebula_overlay)
    
    def create_planet_button(self, button_config: Dict) -> Tuple[Image.Image, Tuple[int, int]]:
        """
        創建單個星球按鈕圖片
        
        Args:
            button_config: 按鈕配置字典，包含 text, color, planet 等信息
            
        Returns:
            Tuple[Image.Image, Tuple[int, int]]: (按鈕圖片, 按鈕中心位置)
        """
        # 按鈕基本參數
        button_size = 400
        button_radius = button_size // 2
        
        # 創建按鈕圖片
        button_img = Image.new('RGBA', (button_size, button_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(button_img)
        
        # 獲取按鈕配置
        text = button_config.get('text', '')
        base_color = button_config.get('color', (255, 255, 255))
        planet_name = button_config.get('planet', '預設')
        rocket_style = button_config.get('rocket_style', 'classic')  # 火箭造型參數
        sun_style = button_config.get('sun_style', 'classic')  # 太陽樣式參數
        earth_style = button_config.get('earth_style', 'classic')  # 地球樣式參數
        moon_style = button_config.get('moon_style', 'classic')  # 月亮樣式參數
        
        # 按鈕中心位置
        center_x = button_size // 2
        center_y = button_size // 2
        
        # 計算星球半徑
        planet_radius = int(button_radius * 0.6)
        
        # 繪製不同的星球樣式
        if planet_name == "火箭":
            # 傳遞火箭造型參數
            self._draw_rocket_detailed(draw, center_x, center_y, planet_radius, base_color, rocket_style)
        else:
            # 其他星球繪製，傳遞樣式參數
            self._draw_unique_planet(draw, center_x, center_y, planet_radius, base_color, text, planet_name, sun_style, earth_style, moon_style)
        
        # 添加按鈕文字
        text_color = (255, 255, 255)
        self._add_button_text(draw, text, button_size, button_size, text_color, center_y, planet_radius)
        
        return button_img, (center_x, center_y)
    
    def _draw_unique_planet(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int], button_name: str, planet_name: str, sun_style: str = "classic", earth_style: str = "classic", moon_style: str = "classic"):
        """根據星球名稱繪製不同的詳細星球"""
        if planet_name == "太陽":
            self._draw_sun_detailed(draw, center_x, center_y, radius, base_color, sun_style)
        elif planet_name == "地球":
            self._draw_earth_detailed(draw, center_x, center_y, radius, base_color, earth_style)
        elif planet_name == "月球":
            self._draw_moon_detailed(draw, center_x, center_y, radius, base_color, moon_style)
        elif planet_name == "土星":
            self._draw_saturn_detailed(draw, center_x, center_y, radius, base_color)
        elif planet_name == "火箭":
            # 檢查是否有指定火箭樣式
            rocket_style = getattr(self, '_current_rocket_style', 'classic')
            self._draw_rocket_detailed(draw, center_x, center_y, radius, base_color, rocket_style)
        elif planet_name == "太空人":
            self._draw_astronaut_detailed(draw, center_x, center_y, radius, base_color)
        elif planet_name == "衛星":
            self._draw_satellite_detailed(draw, center_x, center_y, radius, base_color)
        elif planet_name == "時鐘":
            self._draw_clock_detailed(draw, center_x, center_y, radius, base_color)
        elif planet_name == "天王星":
            self._draw_uranus_detailed(draw, center_x, center_y, radius, base_color)
        elif planet_name == "海王星":
            self._draw_neptune_detailed(draw, center_x, center_y, radius, base_color)
        else:
            # 預設繪製簡單的星球
            draw.ellipse([
                (center_x - radius, center_y - radius),
                (center_x + radius, center_y + radius)
            ], fill=base_color)
    
    def _draw_sun_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int], sun_style: str = "classic"):
        """
        繪製塗鴉風格的太陽 - 支持多種樣式
        """
        if sun_style == "classic":
            self._draw_classic_sun(draw, center_x, center_y, radius, base_color)
        elif sun_style == "cute":
            self._draw_cute_sun(draw, center_x, center_y, radius, base_color)
        elif sun_style == "cartoon":
            self._draw_cartoon_sun(draw, center_x, center_y, radius, base_color)
        elif sun_style == "modern":
            self._draw_modern_sun(draw, center_x, center_y, radius, base_color)
        elif sun_style == "kawaii":
            self._draw_kawaii_sun(draw, center_x, center_y, radius, base_color)
        else:
            self._draw_classic_sun(draw, center_x, center_y, radius, base_color)
    
    def _draw_classic_sun(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        經典太陽樣式 - 改善光芒比例
        """
        # 繪製太陽主體（圓形，帶點不規則）
        sun_points = []
        for i in range(16):
            angle = i * 22.5
            angle_rad = math.radians(angle)
            # 添加一些隨機變化讓邊緣更手繪
            r_variation = radius + random.randint(-8, 8)
            x = center_x + r_variation * math.cos(angle_rad)
            y = center_y + r_variation * math.sin(angle_rad)
            sun_points.append((x, y))
        
        # 漸變效果 - 從中心的亮黃到邊緣的橙色
        for i in range(radius, 0, -5):
            ratio = i / radius
            r = int(255 * ratio + 255 * (1 - ratio))
            g = int(200 * ratio + 150 * (1 - ratio))
            b = int(50 * ratio + 50 * (1 - ratio))
            
            current_radius = int(radius * ratio)
            draw.ellipse([
                (center_x - current_radius, center_y - current_radius),
                (center_x + current_radius, center_y + current_radius)
            ], fill=(r, g, b))
        
        # 繪製光芒（加粗線條，改善比例）
        ray_colors = [(255, 220, 100), (255, 200, 80), (255, 180, 60)]
        for i in range(12):  # 減少光芒數量讓比例更好
            angle = i * 30  # 每30度一條光芒
            angle_rad = math.radians(angle)
            
            # 光芒起點（太陽邊緣）
            start_x = center_x + (radius + 10) * math.cos(angle_rad)
            start_y = center_y + (radius + 10) * math.sin(angle_rad)
            
            # 光芒終點（更長的光芒）
            ray_length = radius * 0.8  # 增加光芒長度
            end_x = center_x + (radius + ray_length) * math.cos(angle_rad)
            end_y = center_y + (radius + ray_length) * math.sin(angle_rad)
            
            # 繪製加粗的光芒
            color = ray_colors[i % len(ray_colors)]
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=8)  # 加粗到8像素
        
        # 添加可愛的表情
        self._draw_sun_face(draw, center_x, center_y, radius)
        
        # 添加腮紅
        blush_color = (255, 150, 150, 150)
        blush_size = radius // 6
        draw.ellipse([
            (center_x - radius//2 - blush_size, center_y + radius//4 - blush_size//2),
            (center_x - radius//2 + blush_size, center_y + radius//4 + blush_size//2)
        ], fill=blush_color)
        draw.ellipse([
            (center_x + radius//2 - blush_size, center_y + radius//4 - blush_size//2),
            (center_x + radius//2 + blush_size, center_y + radius//4 + blush_size//2)
        ], fill=blush_color)
    
    def _draw_cute_sun(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        可愛太陽樣式 - 花瓣狀光芒
        """
        # 主體
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=(255, 220, 100))
        
        # 花瓣狀光芒
        for i in range(8):
            angle = i * 45
            angle_rad = math.radians(angle)
            
            # 花瓣中心
            petal_x = center_x + (radius + 20) * math.cos(angle_rad)
            petal_y = center_y + (radius + 20) * math.sin(angle_rad)
            
            # 繪製花瓣
            petal_size = 25
            draw.ellipse([
                (petal_x - petal_size, petal_y - petal_size//2),
                (petal_x + petal_size, petal_y + petal_size//2)
            ], fill=(255, 200, 80))
        
        # 大眼睛
        eye_size = radius // 4
        draw.ellipse([
            (center_x - radius//3 - eye_size, center_y - radius//4 - eye_size),
            (center_x - radius//3 + eye_size, center_y - radius//4 + eye_size)
        ], fill=(255, 255, 255))
        draw.ellipse([
            (center_x + radius//3 - eye_size, center_y - radius//4 - eye_size),
            (center_x + radius//3 + eye_size, center_y - radius//4 + eye_size)
        ], fill=(255, 255, 255))
        
        # 瞳孔
        pupil_size = eye_size // 2
        draw.ellipse([
            (center_x - radius//3 - pupil_size, center_y - radius//4 - pupil_size),
            (center_x - radius//3 + pupil_size, center_y - radius//4 + pupil_size)
        ], fill=(0, 0, 0))
        draw.ellipse([
            (center_x + radius//3 - pupil_size, center_y - radius//4 - pupil_size),
            (center_x + radius//3 + pupil_size, center_y - radius//4 + pupil_size)
        ], fill=(0, 0, 0))
        
        # 微笑
        mouth_width = radius // 2
        draw.arc([
            (center_x - mouth_width, center_y),
            (center_x + mouth_width, center_y + mouth_width)
        ], 0, 180, fill=(255, 100, 100), width=6)
    
    def _draw_cartoon_sun(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        卡通太陽樣式 - 三角形光芒
        """
        # 主體
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=(255, 215, 0))
        
        # 三角形光芒
        for i in range(16):
            angle = i * 22.5
            angle_rad = math.radians(angle)
            
            # 三角形頂點
            tip_x = center_x + (radius + 40) * math.cos(angle_rad)
            tip_y = center_y + (radius + 40) * math.sin(angle_rad)
            
            # 三角形底邊
            base_angle1 = angle_rad - 0.3
            base_angle2 = angle_rad + 0.3
            base_x1 = center_x + radius * math.cos(base_angle1)
            base_y1 = center_y + radius * math.sin(base_angle1)
            base_x2 = center_x + radius * math.cos(base_angle2)
            base_y2 = center_y + radius * math.sin(base_angle2)
            
            # 繪製三角形
            draw.polygon([
                (tip_x, tip_y),
                (base_x1, base_y1),
                (base_x2, base_y2)
            ], fill=(255, 200, 0))
        
        # 簡單表情
        self._draw_simple_sun_face(draw, center_x, center_y, radius)
    
    def _draw_modern_sun(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        現代太陽樣式 - 簡潔幾何
        """
        # 主體（多邊形）
        sun_points = []
        for i in range(12):
            angle = i * 30
            angle_rad = math.radians(angle)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            sun_points.append((x, y))
        
        draw.polygon(sun_points, fill=(255, 200, 50))
        
        # 幾何光芒
        for i in range(8):
            angle = i * 45
            angle_rad = math.radians(angle)
            
            # 長方形光芒
            rect_length = 30
            rect_width = 8
            
            start_x = center_x + radius * math.cos(angle_rad)
            start_y = center_y + radius * math.sin(angle_rad)
            end_x = center_x + (radius + rect_length) * math.cos(angle_rad)
            end_y = center_y + (radius + rect_length) * math.sin(angle_rad)
            
            draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 180, 30), width=rect_width)
        
        # 現代表情
        self._draw_modern_sun_face(draw, center_x, center_y, radius)
    
    def _draw_kawaii_sun(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        可愛日系太陽樣式
        """
        # 主體（稍微扁平）
        draw.ellipse([
            (center_x - radius, center_y - int(radius * 0.9)),
            (center_x + radius, center_y + int(radius * 0.9))
        ], fill=(255, 230, 120))
        
        # 波浪狀光芒
        for i in range(12):
            angle = i * 30
            angle_rad = math.radians(angle)
            
            # 波浪光芒
            wave_points = []
            for j in range(5):
                wave_radius = radius + 15 + j * 8
                wave_angle = angle_rad + (j - 2) * 0.1
                x = center_x + wave_radius * math.cos(wave_angle)
                y = center_y + wave_radius * math.sin(wave_angle)
                wave_points.append((x, y))
            
            # 繪製波浪
            if len(wave_points) >= 3:
                for k in range(len(wave_points) - 1):
                    draw.line([wave_points[k], wave_points[k + 1]], fill=(255, 200, 100), width=4)
        
        # 可愛表情
        self._draw_kawaii_sun_face(draw, center_x, center_y, radius)
    
    def _draw_earth_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int], earth_style: str = "classic"):
        """
        繪製塗鴉風格的地球 - 支持多種樣式
        """
        if earth_style == "classic":
            self._draw_classic_earth(draw, center_x, center_y, radius, base_color)
        elif earth_style == "detailed":
            self._draw_detailed_earth(draw, center_x, center_y, radius, base_color)
        elif earth_style == "cute_arms":
            self._draw_earth_with_arms(draw, center_x, center_y, radius, base_color)
        elif earth_style == "eyes_only":
            self._draw_earth_eyes_only(draw, center_x, center_y, radius, base_color)
        elif earth_style == "kawaii":
            self._draw_kawaii_earth(draw, center_x, center_y, radius, base_color)
        else:
            self._draw_classic_earth(draw, center_x, center_y, radius, base_color)
    
    def _draw_classic_earth(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        經典地球樣式
        """
        # 地球主體 - 海洋藍色
        ocean_color = (70, 130, 180)
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=ocean_color)
        
        # 大氣層效果
        for i in range(3):
            atmosphere_radius = radius + 5 + i * 3
            atmosphere_alpha = 50 - i * 15
            atmosphere_color = (135, 206, 235, atmosphere_alpha)
            draw.ellipse([
                (center_x - atmosphere_radius, center_y - atmosphere_radius),
                (center_x + atmosphere_radius, center_y + atmosphere_radius)
            ], outline=atmosphere_color, width=2)
        
        # 大陸 - 手繪風格
        continent_color = (34, 139, 34)
        
        # 大陸1 - 左上
        continent1_points = [
            (center_x - radius * 0.6, center_y - radius * 0.4),
            (center_x - radius * 0.2, center_y - radius * 0.6),
            (center_x - radius * 0.1, center_y - radius * 0.3),
            (center_x - radius * 0.3, center_y - radius * 0.1),
            (center_x - radius * 0.7, center_y - radius * 0.2)
        ]
        draw.polygon(continent1_points, fill=continent_color)
        
        # 大陸2 - 右側
        continent2_points = [
            (center_x + radius * 0.2, center_y - radius * 0.3),
            (center_x + radius * 0.6, center_y - radius * 0.1),
            (center_x + radius * 0.7, center_y + radius * 0.2),
            (center_x + radius * 0.3, center_y + radius * 0.4),
            (center_x + radius * 0.1, center_y + radius * 0.1)
        ]
        draw.polygon(continent2_points, fill=continent_color)
        
        # 雲朵
        cloud_color = (255, 255, 255, 180)
        self._draw_earth_clouds(draw, center_x, center_y, radius, cloud_color)
        
        # 表情
        self._draw_earth_face(draw, center_x, center_y, radius)
    
    def _draw_detailed_earth(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        詳細地球樣式 - 強化細節
        """
        # 地球主體 - 漸變海洋色
        for i in range(radius, 0, -3):
            ratio = i / radius
            r = int(70 * ratio + 30 * (1 - ratio))
            g = int(130 * ratio + 100 * (1 - ratio))
            b = int(180 * ratio + 150 * (1 - ratio))
            
            current_radius = int(radius * ratio)
            draw.ellipse([
                (center_x - current_radius, center_y - current_radius),
                (center_x + current_radius, center_y + current_radius)
            ], fill=(r, g, b))
        
        # 詳細大陸
        continent_colors = [(34, 139, 34), (46, 125, 50), (56, 142, 60)]
        
        # 多個大陸塊
        for i in range(5):
            angle = i * 72
            angle_rad = math.radians(angle)
            
            # 大陸中心
            continent_x = center_x + radius * 0.4 * math.cos(angle_rad)
            continent_y = center_y + radius * 0.4 * math.sin(angle_rad)
            
            # 大陸形狀
            continent_points = []
            for j in range(6):
                point_angle = angle_rad + j * math.pi / 3
                point_radius = radius * random.uniform(0.15, 0.25)
                x = continent_x + point_radius * math.cos(point_angle)
                y = continent_y + point_radius * math.sin(point_angle)
                continent_points.append((x, y))
            
            color = continent_colors[i % len(continent_colors)]
            draw.polygon(continent_points, fill=color)
        
        # 詳細雲層
        for i in range(8):
            cloud_x = center_x + radius * 0.6 * math.cos(i * math.pi / 4)
            cloud_y = center_y + radius * 0.6 * math.sin(i * math.pi / 4)
            cloud_size = random.randint(15, 25)
            
            draw.ellipse([
                (cloud_x - cloud_size, cloud_y - cloud_size//2),
                (cloud_x + cloud_size, cloud_y + cloud_size//2)
            ], fill=(255, 255, 255, 150))
        
        # 只有眼睛
        self._draw_earth_eyes_only_face(draw, center_x, center_y, radius)
    
    def _draw_earth_with_arms(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        帶手腳的地球樣式
        """
        # 地球主體
        self._draw_classic_earth(draw, center_x, center_y, radius, base_color)
        
        # 手臂
        arm_color = (70, 130, 180)
        arm_width = 12
        arm_length = 40
        
        # 左手臂
        left_arm_start_x = center_x - radius
        left_arm_start_y = center_y - radius // 3
        left_arm_end_x = left_arm_start_x - arm_length
        left_arm_end_y = left_arm_start_y - 20
        
        draw.line([
            (left_arm_start_x, left_arm_start_y),
            (left_arm_end_x, left_arm_end_y)
        ], fill=arm_color, width=arm_width)
        
        # 左手
        draw.ellipse([
            (left_arm_end_x - 15, left_arm_end_y - 10),
            (left_arm_end_x + 5, left_arm_end_y + 10)
        ], fill=arm_color)
        
        # 右手臂
        right_arm_start_x = center_x + radius
        right_arm_start_y = center_y - radius // 3
        right_arm_end_x = right_arm_start_x + arm_length
        right_arm_end_y = right_arm_start_y - 20
        
        draw.line([
            (right_arm_start_x, right_arm_start_y),
            (right_arm_end_x, right_arm_end_y)
        ], fill=arm_color, width=arm_width)
        
        # 右手
        draw.ellipse([
            (right_arm_end_x - 5, right_arm_end_y - 10),
            (right_arm_end_x + 15, right_arm_end_y + 10)
        ], fill=arm_color)
        
        # 腳
        foot_color = (70, 130, 180)
        foot_width = 10
        foot_length = 30
        
        # 左腳
        left_foot_start_x = center_x - radius // 3
        left_foot_start_y = center_y + radius
        left_foot_end_x = left_foot_start_x - 15
        left_foot_end_y = left_foot_start_y + foot_length
        
        draw.line([
            (left_foot_start_x, left_foot_start_y),
            (left_foot_end_x, left_foot_end_y)
        ], fill=foot_color, width=foot_width)
        
        # 左腳掌
        draw.ellipse([
            (left_foot_end_x - 15, left_foot_end_y - 5),
            (left_foot_end_x + 5, left_foot_end_y + 15)
        ], fill=foot_color)
        
        # 右腳
        right_foot_start_x = center_x + radius // 3
        right_foot_start_y = center_y + radius
        right_foot_end_x = right_foot_start_x + 15
        right_foot_end_y = right_foot_start_y + foot_length
        
        draw.line([
            (right_foot_start_x, right_foot_start_y),
            (right_foot_end_x, right_foot_end_y)
        ], fill=foot_color, width=foot_width)
        
        # 右腳掌
        draw.ellipse([
            (right_foot_end_x - 5, right_foot_end_y - 5),
            (right_foot_end_x + 15, right_foot_end_y + 15)
        ], fill=foot_color)
    
    def _draw_earth_eyes_only(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        只有眼睛的地球樣式
        """
        # 地球主體
        self._draw_detailed_earth(draw, center_x, center_y, radius, base_color)
        
        # 只繪製眼睛，不要其他表情
        # 已在_draw_detailed_earth中處理
    
    def _draw_kawaii_earth(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        可愛日系地球樣式
        """
        # 地球主體（稍微扁平）
        draw.ellipse([
            (center_x - radius, center_y - int(radius * 0.95)),
            (center_x + radius, center_y + int(radius * 0.95))
        ], fill=(100, 150, 200))
        
        # 心形大陸
        heart_color = (60, 180, 75)
        
        # 心形1
        heart1_x = center_x - radius // 3
        heart1_y = center_y - radius // 4
        self._draw_heart_continent(draw, heart1_x, heart1_y, 20, heart_color)
        
        # 心形2
        heart2_x = center_x + radius // 2
        heart2_y = center_y + radius // 3
        self._draw_heart_continent(draw, heart2_x, heart2_y, 15, heart_color)
        
        # 星星裝飾
        star_color = (255, 255, 255, 200)
        for i in range(6):
            star_x = center_x + radius * 0.7 * math.cos(i * math.pi / 3)
            star_y = center_y + radius * 0.7 * math.sin(i * math.pi / 3)
            self._draw_cute_star(draw, star_x, star_y, 8, star_color)
        
        # 可愛表情
        self._draw_kawaii_earth_face(draw, center_x, center_y, radius)
    
    def _draw_saturn_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製塗鴉風格的土星 - 優化細節避開表情區域
        """
        # 土星主體 - 金黃色漸變
        saturn_color = (255, 215, 100, 255)
        
        # 繪製土星主體
        draw.ellipse([(center_x - radius, center_y - radius), 
                     (center_x + radius, center_y + radius)], fill=saturn_color)
        
        # 先繪製土星可愛表情 - 確保不被遮擋
        # 眼睛 - 更大更可愛
        eye_size = 10
        left_eye_x = center_x - radius // 3
        right_eye_x = center_x + radius // 3
        eye_y = center_y - radius // 4
        
        # 眼睛底色（白色）
        eye_white_color = (255, 255, 255, 255)
        draw.ellipse([(left_eye_x - eye_size, eye_y - eye_size), 
                     (left_eye_x + eye_size, eye_y + eye_size)], fill=eye_white_color)
        draw.ellipse([(right_eye_x - eye_size, eye_y - eye_size), 
                     (right_eye_x + eye_size, eye_y + eye_size)], fill=eye_white_color)
        
        # 眼珠（更大更溫柔）
        eye_color = (255, 140, 0, 255)  # 金黃色眼珠，與土星顏色呼應
        eye_pupil_size = 7
        draw.ellipse([(left_eye_x - eye_pupil_size, eye_y - eye_pupil_size), 
                     (left_eye_x + eye_pupil_size, eye_y + eye_pupil_size)], fill=eye_color)
        draw.ellipse([(right_eye_x - eye_pupil_size, eye_y - eye_pupil_size), 
                     (right_eye_x + eye_pupil_size, eye_y + eye_pupil_size)], fill=eye_color)
        
        # 眼睛高光（更大更明顯）
        highlight_color = (255, 255, 255, 255)
        draw.ellipse([(left_eye_x - 3, eye_y - 4), (left_eye_x + 2, eye_y)], fill=highlight_color)
        draw.ellipse([(right_eye_x - 3, eye_y - 4), (right_eye_x + 2, eye_y)], fill=highlight_color)
        
        # 可愛的睫毛
        eyelash_color = (150, 100, 50, 255)
        for i in range(4):
            # 左眼睫毛
            lash_x = left_eye_x - eye_size + i * 6
            lash_y = eye_y - eye_size - 2
            draw.line([(lash_x, lash_y), (lash_x + 1, lash_y - 5)], fill=eyelash_color, width=2)
            
            # 右眼睫毛
            lash_x = right_eye_x - eye_size + i * 6
            lash_y = eye_y - eye_size - 2
            draw.line([(lash_x, lash_y), (lash_x + 1, lash_y - 5)], fill=eyelash_color, width=2)
        
        # 甜美的得意笑容（更彎曲）
        mouth_y = center_y + radius // 4
        mouth_width = radius // 2
        mouth_color = (255, 140, 0, 255)  # 金黃色嘴巴
        
        # 繪製甜美的得意笑容弧線（更彎曲）
        for i in range(mouth_width):
            x = center_x - mouth_width // 2 + i
            y_offset = int(18 * math.sin(math.pi * i / mouth_width))
            draw.ellipse([(x - 3, mouth_y + y_offset - 3), 
                         (x + 3, mouth_y + y_offset + 3)], fill=mouth_color)
        
        # 更明顯的腮紅
        blush_color = (255, 180, 180, 200)
        blush_size = 15
        draw.ellipse([(center_x - radius * 0.8, center_y - blush_size), 
                     (center_x - radius * 0.8 + blush_size * 2, center_y + blush_size)], fill=blush_color)
        draw.ellipse([(center_x + radius * 0.8 - blush_size * 2, center_y - blush_size), 
                     (center_x + radius * 0.8, center_y + blush_size)], fill=blush_color)
        
        # 土星表面紋理 - 避開表情區域
        # 定義表情保護區域
        face_center_x = center_x
        face_center_y = center_y - radius // 8
        face_radius = radius * 0.6
        
        # 大氣漩渦紋理 - 分散在表情區域外
        swirl_color = (240, 200, 80, 120)  # 降低透明度
        swirl_positions = [
            (center_x - radius * 0.7, center_y - radius * 0.8),  # 左上
            (center_x + radius * 0.7, center_y - radius * 0.8),  # 右上
            (center_x - radius * 0.8, center_y + radius * 0.6),  # 左下
            (center_x + radius * 0.8, center_y + radius * 0.6),  # 右下
            (center_x - radius * 0.9, center_y),                 # 左側
            (center_x + radius * 0.9, center_y),                 # 右側
        ]
        
        for swirl_x, swirl_y in swirl_positions:
            if (swirl_x - center_x)**2 + (swirl_y - center_y)**2 <= radius**2:
                # 檢查是否在表情區域內
                if (swirl_x - face_center_x)**2 + (swirl_y - face_center_y)**2 > face_radius**2:
                    # 繪製小漩渦
                    for j in range(3):
                        spiral_radius = 8 - j * 2
                        draw.ellipse([(swirl_x - spiral_radius, swirl_y - spiral_radius), 
                                     (swirl_x + spiral_radius, swirl_y + spiral_radius)], fill=swirl_color)
        
        # 土星的條紋帶（避開表情區域，改為局部條紋）
        stripe_colors = [(250, 220, 90, 150), (240, 200, 80, 120), (230, 180, 70, 100)]
        
        # 上方條紋
        for i, stripe_color in enumerate(stripe_colors):
            stripe_y = center_y - radius * 0.8 + i * 8
            stripe_width = int(radius * 1.2)
            draw.ellipse([(center_x - stripe_width, stripe_y - 4), 
                         (center_x + stripe_width, stripe_y + 4)], fill=stripe_color)
        
        # 下方條紋
        for i, stripe_color in enumerate(stripe_colors):
            stripe_y = center_y + radius * 0.6 + i * 8
            stripe_width = int(radius * 1.2)
            draw.ellipse([(center_x - stripe_width, stripe_y - 4), 
                         (center_x + stripe_width, stripe_y + 4)], fill=stripe_color)
        
        # 土星環帶 - 更立體的3D效果
        ring_colors = [(255, 230, 150, 220), (255, 200, 100, 180), (240, 180, 80, 140)]
        
        for i, ring_color in enumerate(ring_colors):
            ring_radius = radius + (i + 1) * 18
            ring_thickness = 10 - i * 2
            
            # 主環帶（橢圓形，有透視效果）
            ring_height = ring_radius // 3  # 壓扁效果
            draw.ellipse([
                (center_x - ring_radius, center_y - ring_height),
                (center_x + ring_radius, center_y + ring_height)
            ], outline=ring_color, width=ring_thickness)
            
            # 環帶陰影效果
            shadow_color = (200, 150, 60, 100)
            draw.ellipse([
                (center_x - ring_radius, center_y - ring_height + 3),
                (center_x + ring_radius, center_y + ring_height + 3)
            ], outline=shadow_color, width=ring_thickness // 2)
        
        # 可愛的小皇冠裝飾 - 移到土星上方遠一點
        crown_color = (255, 215, 0, 255)  # 金色皇冠
        crown_y = center_y - radius - 25  # 增加距離
        
        # 皇冠底座
        draw.ellipse([(center_x - 18, crown_y - 6), (center_x + 18, crown_y + 6)], fill=crown_color)
        
        # 皇冠尖塔
        crown_points = [
            (center_x - 12, crown_y - 6),
            (center_x - 8, crown_y - 15),
            (center_x - 4, crown_y - 6),
            (center_x, crown_y - 20),
            (center_x + 4, crown_y - 6),
            (center_x + 8, crown_y - 15),
            (center_x + 12, crown_y - 6)
        ]
        draw.polygon(crown_points, fill=crown_color)
        
        # 皇冠上的小寶石
        gem_color = (255, 20, 147, 255)  # 粉色寶石
        gem_positions = [
            (center_x - 8, crown_y - 12),
            (center_x, crown_y - 17),
            (center_x + 8, crown_y - 12)
        ]
        
        for gem_x, gem_y in gem_positions:
            draw.ellipse([(gem_x - 2, gem_y - 2), (gem_x + 2, gem_y + 2)], fill=gem_color)
    
    def _draw_rocket_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int], rocket_style: str = "classic"):
        """
        繪製手繪風格的可愛火箭 - 提供多種造型選擇
        """
        if rocket_style == "classic":
            self._draw_classic_rocket(draw, center_x, center_y, radius, base_color)
        elif rocket_style == "cartoon":
            self._draw_cartoon_rocket(draw, center_x, center_y, radius, base_color)
        elif rocket_style == "retro":
            self._draw_retro_rocket(draw, center_x, center_y, radius, base_color)
        elif rocket_style == "space_shuttle":
            self._draw_space_shuttle_rocket(draw, center_x, center_y, radius, base_color)
        elif rocket_style == "mini_rocket":
            self._draw_mini_rocket(draw, center_x, center_y, radius, base_color)
        else:  # modern
            self._draw_modern_rocket(draw, center_x, center_y, radius, base_color)
    
    def _draw_classic_rocket(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """經典火箭造型 - 三角頭 + 圓柱身體 + 尾翼"""
        # 火箭尺寸
        rocket_height = int(radius * 2.4)
        body_width = int(radius * 0.7)
        nose_height = int(radius * 0.6)
        
        # 火箭主體（圓柱形）
        body_color = (220, 220, 220, 255)  # 銀白色
        body_top = center_y - rocket_height // 3
        body_bottom = center_y + rocket_height // 3
        
        draw.rectangle([
            (center_x - body_width // 2, body_top),
            (center_x + body_width // 2, body_bottom)
        ], fill=body_color)
        
        # 火箭頭部（三角形）
        nose_color = (255, 100, 100, 255)  # 紅色
        nose_tip = body_top - nose_height
        nose_points = [
            (center_x, nose_tip),
            (center_x - body_width // 2, body_top),
            (center_x + body_width // 2, body_top)
        ]
        draw.polygon(nose_points, fill=nose_color)
        
        # 火箭尾翼
        fin_color = (255, 150, 100, 255)  # 橙色
        fin_width = int(body_width * 0.3)
        fin_height = int(radius * 0.4)
        
        # 左尾翼
        left_fin_points = [
            (center_x - body_width // 2, body_bottom - fin_height),
            (center_x - body_width // 2 - fin_width, body_bottom),
            (center_x - body_width // 2, body_bottom)
        ]
        draw.polygon(left_fin_points, fill=fin_color)
        
        # 右尾翼
        right_fin_points = [
            (center_x + body_width // 2, body_bottom - fin_height),
            (center_x + body_width // 2 + fin_width, body_bottom),
            (center_x + body_width // 2, body_bottom)
        ]
        draw.polygon(right_fin_points, fill=fin_color)
        
        # 觀察窗
        window_color = (100, 200, 255, 255)
        window_radius = int(radius * 0.2)
        window_y = center_y - radius // 6
        
        draw.ellipse([
            (center_x - window_radius, window_y - window_radius),
            (center_x + window_radius, window_y + window_radius)
        ], fill=window_color)
        
        # 可愛表情
        self._draw_rocket_face(draw, center_x, window_y, window_radius)
        
        # 火焰效果
        self._draw_rocket_flames(draw, center_x, body_bottom, body_width)
    
    def _draw_cartoon_rocket(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """卡通火箭造型 - 圓潤可愛風格"""
        # 火箭主體（膠囊形狀）
        rocket_height = int(radius * 2.2)
        body_width = int(radius * 0.8)
        
        # 主體顏色
        body_color = (255, 200, 200, 255)  # 粉色
        
        # 繪製膠囊形主體
        body_top = center_y - rocket_height // 2
        body_bottom = center_y + rocket_height // 2
        
        # 上半圓
        draw.ellipse([
            (center_x - body_width // 2, body_top),
            (center_x + body_width // 2, body_top + body_width)
        ], fill=body_color)
        
        # 中間矩形
        draw.rectangle([
            (center_x - body_width // 2, body_top + body_width // 2),
            (center_x + body_width // 2, body_bottom - body_width // 2)
        ], fill=body_color)
        
        # 下半圓
        draw.ellipse([
            (center_x - body_width // 2, body_bottom - body_width),
            (center_x + body_width // 2, body_bottom)
        ], fill=body_color)
        
        # 彩色條紋
        stripe_colors = [
            (255, 100, 100, 255),  # 紅
            (255, 165, 0, 255),    # 橙
            (255, 255, 0, 255),    # 黃
            (0, 255, 0, 255),      # 綠
            (0, 100, 255, 255)     # 藍
        ]
        
        stripe_height = 8
        for i, color in enumerate(stripe_colors):
            stripe_y = body_top + body_width // 2 + i * stripe_height * 2
            if stripe_y < body_bottom - body_width // 2:
                draw.rectangle([
                    (center_x - body_width // 2 + 5, stripe_y),
                    (center_x + body_width // 2 - 5, stripe_y + stripe_height)
                ], fill=color)
        
        # 大眼睛
        eye_color = (255, 255, 255, 255)
        eye_radius = int(radius * 0.15)
        left_eye_x = center_x - body_width // 4
        right_eye_x = center_x + body_width // 4
        eye_y = center_y - radius // 3
        
        # 眼睛底色
        draw.ellipse([
            (left_eye_x - eye_radius, eye_y - eye_radius),
            (left_eye_x + eye_radius, eye_y + eye_radius)
        ], fill=eye_color)
        draw.ellipse([
            (right_eye_x - eye_radius, eye_y - eye_radius),
            (right_eye_x + eye_radius, eye_y + eye_radius)
        ], fill=eye_color)
        
        # 眼珠
        pupil_color = (50, 50, 50, 255)
        pupil_radius = eye_radius // 2
        draw.ellipse([
            (left_eye_x - pupil_radius, eye_y - pupil_radius),
            (left_eye_x + pupil_radius, eye_y + pupil_radius)
        ], fill=pupil_color)
        draw.ellipse([
            (right_eye_x - pupil_radius, eye_y - pupil_radius),
            (right_eye_x + pupil_radius, eye_y + pupil_radius)
        ], fill=pupil_color)
        
        # 開心的嘴巴
        mouth_color = (255, 100, 100, 255)
        mouth_y = center_y
        mouth_width = body_width // 2
        
        for i in range(mouth_width):
            x = center_x - mouth_width // 2 + i
            y_offset = int(8 * math.sin(math.pi * i / mouth_width))
            draw.ellipse([
                (x - 2, mouth_y + y_offset - 2),
                (x + 2, mouth_y + y_offset + 2)
            ], fill=mouth_color)
        
        # 腮紅
        blush_color = (255, 150, 150, 150)
        blush_radius = int(radius * 0.1)
        draw.ellipse([
            (center_x - body_width // 2 + 5, center_y - blush_radius),
            (center_x - body_width // 2 + 5 + blush_radius * 2, center_y + blush_radius)
        ], fill=blush_color)
        draw.ellipse([
            (center_x + body_width // 2 - 5 - blush_radius * 2, center_y - blush_radius),
            (center_x + body_width // 2 - 5, center_y + blush_radius)
        ], fill=blush_color)
        
        # 火焰效果
        self._draw_cartoon_flames(draw, center_x, body_bottom, body_width)
    
    def _draw_retro_rocket(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """復古火箭造型 - 50年代科幻風格"""
        # 火箭主體（流線型）
        rocket_height = int(radius * 2.3)
        body_width = int(radius * 0.75)
        
        # 主體顏色（金屬銀色）
        body_color = (200, 200, 200, 255)
        
        # 計算火箭輪廓點
        rocket_points = []
        body_top = center_y - rocket_height // 2
        body_bottom = center_y + rocket_height // 2
        
        # 頂部尖端
        rocket_points.append((center_x, body_top))
        
        # 頭部曲線
        for i in range(10):
            angle = math.pi * i / 20
            x = center_x + int((body_width // 2) * math.sin(angle))
            y = body_top + int((rocket_height // 4) * (1 - math.cos(angle)))
            rocket_points.append((x, y))
        
        # 身體右側
        rocket_points.append((center_x + body_width // 2, body_bottom - rocket_height // 6))
        
        # 底部曲線
        for i in range(5):
            angle = math.pi * i / 10
            x = center_x + int((body_width // 2) * math.cos(angle))
            y = body_bottom - int((rocket_height // 6) * math.sin(angle))
            rocket_points.append((x, y))
        
        # 身體左側（鏡像）
        for i in range(5):
            angle = math.pi * (5 - i) / 10
            x = center_x - int((body_width // 2) * math.cos(angle))
            y = body_bottom - int((rocket_height // 6) * math.sin(angle))
            rocket_points.append((x, y))
        
        rocket_points.append((center_x - body_width // 2, body_bottom - rocket_height // 6))
        
        # 頭部曲線（左側）
        for i in range(10):
            angle = math.pi * (10 - i) / 20
            x = center_x - int((body_width // 2) * math.sin(angle))
            y = body_top + int((rocket_height // 4) * (1 - math.cos(angle)))
            rocket_points.append((x, y))
        
        # 繪製主體
        draw.polygon(rocket_points, fill=body_color)
        
        # 金屬質感條紋
        stripe_color = (180, 180, 180, 255)
        for i in range(5):
            stripe_y = body_top + rocket_height // 4 + i * (rocket_height // 2) // 5
            draw.line([
                (center_x - body_width // 2 + 5, stripe_y),
                (center_x + body_width // 2 - 5, stripe_y)
            ], fill=stripe_color, width=2)
        
        # 復古觀察窗（矩形）
        window_color = (100, 255, 100, 255)  # 綠色
        window_width = int(body_width * 0.4)
        window_height = int(radius * 0.3)
        window_y = center_y - radius // 4
        
        draw.rectangle([
            (center_x - window_width // 2, window_y - window_height // 2),
            (center_x + window_width // 2, window_y + window_height // 2)
        ], fill=window_color)
        
        # 復古表情
        self._draw_retro_face(draw, center_x, window_y, window_width, window_height)
        
        # 復古火焰
        self._draw_retro_flames(draw, center_x, body_bottom, body_width)
    
    def _draw_modern_rocket(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """現代火箭造型 - 簡潔科技風格"""
        # 火箭主體（長方形為主）
        rocket_height = int(radius * 2.1)
        body_width = int(radius * 0.7)
        
        # 主體顏色（科技藍）
        body_color = (70, 130, 180, 255)
        
        body_top = center_y - rocket_height // 2
        body_bottom = center_y + rocket_height // 2
        
        # 主體矩形
        draw.rectangle([
            (center_x - body_width // 2, body_top + 20),
            (center_x + body_width // 2, body_bottom - 20)
        ], fill=body_color)
        
        # 頭部（圓角矩形）
        nose_color = (255, 255, 255, 255)
        draw.ellipse([
            (center_x - body_width // 2, body_top),
            (center_x + body_width // 2, body_top + 40)
        ], fill=nose_color)
        
        # 側面推進器
        thruster_color = (100, 100, 100, 255)
        thruster_width = int(body_width * 0.2)
        thruster_height = int(rocket_height * 0.6)
        
        # 左推進器
        draw.rectangle([
            (center_x - body_width // 2 - thruster_width, center_y - thruster_height // 2),
            (center_x - body_width // 2, center_y + thruster_height // 2)
        ], fill=thruster_color)
        
        # 右推進器
        draw.rectangle([
            (center_x + body_width // 2, center_y - thruster_height // 2),
            (center_x + body_width // 2 + thruster_width, center_y + thruster_height // 2)
        ], fill=thruster_color)
        
        # 科技感細節線條
        detail_color = (255, 255, 255, 150)
        for i in range(3):
            y = body_top + 30 + i * 20
            draw.line([
                (center_x - body_width // 2 + 10, y),
                (center_x + body_width // 2 - 10, y)
            ], fill=detail_color, width=2)
        
        # 現代化表情
        self._draw_modern_face(draw, center_x, center_y - radius // 4, radius // 3)
        
        # 推進器火焰
        self._draw_modern_flames(draw, center_x, body_bottom, body_width)
    
    def _draw_space_shuttle_rocket(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製太空梭造型火箭 - 無表情版本，加上火焰和裝飾
        """
        # 計算太空梭尺寸
        shuttle_width = int(radius * 1.4)
        shuttle_height = int(radius * 1.8)
        
        # 太空梭主體（扁平寬體）
        main_body_points = [
            (center_x - shuttle_width//3, center_y - shuttle_height//2),  # 頂部左
            (center_x + shuttle_width//3, center_y - shuttle_height//2),  # 頂部右
            (center_x + shuttle_width//2, center_y + shuttle_height//4),  # 右側
            (center_x - shuttle_width//2, center_y + shuttle_height//4),  # 左側
        ]
        
        # 繪製主體
        draw.polygon(main_body_points, fill=(220, 220, 220))  # 淺灰色主體
        draw.polygon(main_body_points, outline=(180, 180, 180), width=3)
        
        # 繪製機頭（圓潤）
        nose_radius = shuttle_width // 4
        draw.ellipse([
            (center_x - nose_radius, center_y - shuttle_height//2 - nose_radius//2),
            (center_x + nose_radius, center_y - shuttle_height//2 + nose_radius//2)
        ], fill=(200, 200, 200))
        
        # 繪製側翼
        wing_points_left = [
            (center_x - shuttle_width//2, center_y),
            (center_x - shuttle_width//2 - 30, center_y + 20),
            (center_x - shuttle_width//2 - 20, center_y + 40),
            (center_x - shuttle_width//3, center_y + 20)
        ]
        wing_points_right = [
            (center_x + shuttle_width//2, center_y),
            (center_x + shuttle_width//2 + 30, center_y + 20),
            (center_x + shuttle_width//2 + 20, center_y + 40),
            (center_x + shuttle_width//3, center_y + 20)
        ]
        
        draw.polygon(wing_points_left, fill=(180, 180, 180))
        draw.polygon(wing_points_right, fill=(180, 180, 180))
        
        # 裝飾：彩色線條
        line_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        for i, color in enumerate(line_colors):
            y_pos = center_y - shuttle_height//3 + i * 15
            draw.line([
                (center_x - shuttle_width//4, y_pos),
                (center_x + shuttle_width//4, y_pos)
            ], fill=color, width=4)
        
        # 裝飾：圓點
        dot_colors = [(255, 150, 150), (150, 255, 150), (150, 150, 255), (255, 255, 150)]
        for i in range(8):
            x_offset = (i % 4 - 1.5) * 20
            y_offset = (i // 4 - 0.5) * 25
            dot_x = center_x + x_offset
            dot_y = center_y + y_offset
            color = dot_colors[i % len(dot_colors)]
            draw.ellipse([
                (dot_x - 6, dot_y - 6),
                (dot_x + 6, dot_y + 6)
            ], fill=color)
        
        # 繪製推進器
        thruster_width = shuttle_width // 3
        thruster_height = 25
        
        # 左推進器
        left_thruster = [
            (center_x - thruster_width//2 - 20, center_y + shuttle_height//4),
            (center_x - 20, center_y + shuttle_height//4),
            (center_x - 20, center_y + shuttle_height//4 + thruster_height),
            (center_x - thruster_width//2 - 20, center_y + shuttle_height//4 + thruster_height)
        ]
        
        # 右推進器
        right_thruster = [
            (center_x + 20, center_y + shuttle_height//4),
            (center_x + thruster_width//2 + 20, center_y + shuttle_height//4),
            (center_x + thruster_width//2 + 20, center_y + shuttle_height//4 + thruster_height),
            (center_x + 20, center_y + shuttle_height//4 + thruster_height)
        ]
        
        # 中央推進器
        center_thruster = [
            (center_x - thruster_width//4, center_y + shuttle_height//4),
            (center_x + thruster_width//4, center_y + shuttle_height//4),
            (center_x + thruster_width//4, center_y + shuttle_height//4 + thruster_height),
            (center_x - thruster_width//4, center_y + shuttle_height//4 + thruster_height)
        ]
        
        draw.polygon(left_thruster, fill=(150, 150, 150))
        draw.polygon(right_thruster, fill=(150, 150, 150))
        draw.polygon(center_thruster, fill=(150, 150, 150))
        
        # 繪製火焰效果
        flame_y = center_y + shuttle_height//4 + thruster_height
        self._draw_shuttle_flames(draw, center_x, flame_y, shuttle_width)
    
    def _draw_mini_rocket(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """迷你火箭造型 - 小巧精緻風格"""
        # 迷你火箭尺寸
        rocket_height = int(radius * 1.8)
        body_width = int(radius * 0.6)
        
        # 主體顏色（亮黃色）
        body_color = (255, 220, 100, 255)
        
        body_top = center_y - rocket_height // 2
        body_bottom = center_y + rocket_height // 2
        
        # 火箭主體（圓角矩形）
        draw.rounded_rectangle([
            (center_x - body_width // 2, body_top + 15),
            (center_x + body_width // 2, body_bottom - 15)
        ], radius=10, fill=body_color)
        
        # 圓形頭部
        nose_color = (255, 150, 150, 255)
        nose_radius = body_width // 2
        
        draw.ellipse([
            (center_x - nose_radius, body_top),
            (center_x + nose_radius, body_top + nose_radius * 2)
        ], fill=nose_color)
        
        # 小尾翼
        fin_color = (255, 100, 100, 255)
        fin_size = int(body_width * 0.25)
        
        # 左尾翼
        left_fin_points = [
            (center_x - body_width // 2, body_bottom - fin_size),
            (center_x - body_width // 2 - fin_size, body_bottom),
            (center_x - body_width // 2, body_bottom)
        ]
        draw.polygon(left_fin_points, fill=fin_color)
        
        # 右尾翼
        right_fin_points = [
            (center_x + body_width // 2, body_bottom - fin_size),
            (center_x + body_width // 2 + fin_size, body_bottom),
            (center_x + body_width // 2, body_bottom)
        ]
        draw.polygon(right_fin_points, fill=fin_color)
        
        # 小窗戶
        window_color = (150, 200, 255, 255)
        window_size = int(body_width * 0.3)
        
        draw.ellipse([
            (center_x - window_size // 2, center_y - window_size // 2),
            (center_x + window_size // 2, center_y + window_size // 2)
        ], fill=window_color)
        
        # 超可愛表情
        self._draw_mini_face(draw, center_x, center_y, window_size)
        
        # 小火焰
        self._draw_mini_flames(draw, center_x, body_bottom, body_width)
    
    def _draw_rocket_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """繪製火箭的可愛表情"""
        # 眼睛
        eye_color = (50, 50, 50, 255)
        eye_size = max(2, radius // 8)
        left_eye_x = center_x - radius // 2
        right_eye_x = center_x + radius // 2
        eye_y = center_y - radius // 3
        
        draw.ellipse([
            (left_eye_x - eye_size, eye_y - eye_size),
            (left_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        draw.ellipse([
            (right_eye_x - eye_size, eye_y - eye_size),
            (right_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        
        # 嘴巴
        mouth_color = (255, 100, 100, 255)
        draw.ellipse([
            (center_x - radius // 3, center_y + radius // 4 - 2),
            (center_x + radius // 3, center_y + radius // 4 + 2)
        ], fill=mouth_color)
    
    def _draw_cartoon_flames(self, draw: ImageDraw.Draw, center_x: int, flame_y: int, width: int):
        """繪製卡通風格火焰"""
        flame_colors = [
            (255, 100, 100, 255),  # 紅
            (255, 165, 0, 255),    # 橙
            (255, 255, 0, 255),    # 黃
        ]
        
        for i, color in enumerate(flame_colors):
            flame_height = 30 - i * 8
            flame_width = width - i * 10
            
            # 波浪形火焰
            for j in range(flame_width):
                if flame_width > 0:
                    x = center_x - flame_width // 2 + j
                    wave_height = int(flame_height * (1 + 0.3 * math.sin(j * 0.8)))
                    for k in range(0, wave_height, 3):
                        y = flame_y + k
                        draw.ellipse([(x - 1, y - 1), (x + 1, y + 1)], fill=color)
    
    def _draw_rocket_flames(self, draw: ImageDraw.Draw, center_x: int, flame_y: int, width: int):
        """繪製經典火箭火焰"""
        flame_colors = [
            (255, 100, 100, 255),  # 紅
            (255, 165, 0, 255),    # 橙
            (255, 255, 0, 255),    # 黃
            (255, 255, 255, 200)   # 白
        ]
        
        for i, color in enumerate(flame_colors):
            flame_height = 40 - i * 8
            flame_width = width - i * 6
            
            if flame_width > 0:
                # 三角形火焰
                flame_points = [
                    (center_x - flame_width // 2, flame_y),
                    (center_x + flame_width // 2, flame_y),
                    (center_x, flame_y + flame_height)
                ]
                draw.polygon(flame_points, fill=color)
    
    def _draw_retro_flames(self, draw: ImageDraw.Draw, center_x: int, flame_y: int, width: int):
        """繪製復古風格火焰"""
        flame_colors = [
            (255, 0, 0, 255),      # 純紅
            (255, 100, 0, 255),    # 深橙
            (255, 200, 0, 255),    # 金黃
        ]
        
        for i, color in enumerate(flame_colors):
            flame_height = 35 - i * 6
            flame_width = width - i * 8
            
            if flame_width > 0:
                # 矩形火焰
                draw.rectangle([
                    (center_x - flame_width // 2, flame_y),
                    (center_x + flame_width // 2, flame_y + flame_height)
                ], fill=color)
    
    def _draw_modern_flames(self, draw: ImageDraw.Draw, center_x: int, flame_y: int, width: int):
        """現代化火焰效果"""
        flame_colors = [
            (255, 255, 255, 200),  # 白色
            (100, 200, 255, 180),  # 藍色
            (0, 150, 255, 160)     # 深藍色
        ]
        
        for i, color in enumerate(flame_colors):
            flame_height = 30 - i * 8
            flame_width = width - i * 10
            
            # 簡潔的火焰形狀
            flame_points = [
                (center_x - flame_width // 4, flame_y),
                (center_x - flame_width // 6, flame_y + flame_height // 2),
                (center_x, flame_y + flame_height),
                (center_x + flame_width // 6, flame_y + flame_height // 2),
                (center_x + flame_width // 4, flame_y)
            ]
            draw.polygon(flame_points, fill=color)
    
    def _draw_retro_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, width: int, height: int):
        """繪製復古風格表情"""
        # 方形眼睛
        eye_size = 3
        left_eye_x = center_x - width // 4
        right_eye_x = center_x + width // 4
        eye_y = center_y - height // 4
        
        draw.rectangle([
            (left_eye_x - eye_size, eye_y - eye_size),
            (left_eye_x + eye_size, eye_y + eye_size)
        ], fill=(255, 255, 255, 255))
        draw.rectangle([
            (right_eye_x - eye_size, eye_y - eye_size),
            (right_eye_x + eye_size, eye_y + eye_size)
        ], fill=(255, 255, 255, 255))
        
        # 直線嘴巴
        draw.line([
            (center_x - width // 4, center_y + height // 4),
            (center_x + width // 4, center_y + height // 4)
        ], fill=(255, 255, 255, 255), width=2)
    
    def _draw_modern_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """繪製現代風格表情"""
        # LED風格眼睛
        eye_color = (0, 255, 0, 255)  # 綠色LED
        eye_size = 2
        left_eye_x = center_x - radius // 2
        right_eye_x = center_x + radius // 2
        eye_y = center_y - radius // 3
        
        draw.ellipse([
            (left_eye_x - eye_size, eye_y - eye_size),
            (left_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        draw.ellipse([
            (right_eye_x - eye_size, eye_y - eye_size),
            (right_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        
        # 數字顯示風格嘴巴
        draw.rectangle([
            (center_x - radius // 3, center_y + radius // 4 - 1),
            (center_x + radius // 3, center_y + radius // 4 + 1)
        ], fill=eye_color)
    
    def _draw_uranus_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製天王星的詳細設計 - 有環帶的可愛星球
        """
        # 天王星主體 - 藍綠色
        uranus_color = (100, 200, 200, 255)
        
        # 主體星球
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=uranus_color)
        
        # 大氣層效果
        atmosphere_color = (150, 220, 220, 100)
        for i in range(3):
            atm_radius = radius - i * 15
            if atm_radius > 0:
                draw.ellipse([
                    (center_x - atm_radius, center_y - atm_radius),
                    (center_x + atm_radius, center_y + atm_radius)
                ], outline=atmosphere_color, width=2)
        
        # 垂直環帶系統（天王星特色）
        ring_color = (200, 200, 200, 150)
        ring_width = radius * 2.5
        ring_height = radius * 0.3
        
        # 主環帶
        draw.ellipse([
            (center_x - ring_width // 2, center_y - ring_height // 2),
            (center_x + ring_width // 2, center_y + ring_height // 2)
        ], outline=ring_color, width=8)
        
        # 次環帶
        for i in range(2):
            offset = (i + 1) * 12
            draw.ellipse([
                (center_x - ring_width // 2, center_y - ring_height // 2 - offset),
                (center_x + ring_width // 2, center_y + ring_height // 2 - offset)
            ], outline=ring_color, width=4)
            draw.ellipse([
                (center_x - ring_width // 2, center_y - ring_height // 2 + offset),
                (center_x + ring_width // 2, center_y + ring_height // 2 + offset)
            ], outline=ring_color, width=4)
        
        # 表面紋理
        texture_color = (80, 180, 180, 255)
        for _ in range(8):
            spot_x = center_x + random.randint(-radius + 20, radius - 20)
            spot_y = center_y + random.randint(-radius + 20, radius - 20)
            spot_size = random.randint(8, 15)
            draw.ellipse([
                (spot_x - spot_size, spot_y - spot_size),
                (spot_x + spot_size, spot_y + spot_size)
            ], fill=texture_color)
        
        # 可愛表情 - 神秘的眼神
        eye_color = (255, 255, 255, 255)
        eye_size = radius // 6
        left_eye_x = center_x - radius // 3
        right_eye_x = center_x + radius // 3
        eye_y = center_y - radius // 4
        
        # 眼睛
        draw.ellipse([
            (left_eye_x - eye_size, eye_y - eye_size),
            (left_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        draw.ellipse([
            (right_eye_x - eye_size, eye_y - eye_size),
            (right_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        
        # 眼珠
        pupil_color = (50, 50, 50, 255)
        pupil_size = eye_size // 2
        draw.ellipse([
            (left_eye_x - pupil_size, eye_y - pupil_size),
            (left_eye_x + pupil_size, eye_y + pupil_size)
        ], fill=pupil_color)
        draw.ellipse([
            (right_eye_x - pupil_size, eye_y - pupil_size),
            (right_eye_x + pupil_size, eye_y + pupil_size)
        ], fill=pupil_color)
        
        # 微笑
        mouth_color = (255, 255, 255, 255)
        mouth_y = center_y + radius // 3
        mouth_width = radius // 2
        draw.arc([
            (center_x - mouth_width, mouth_y - mouth_width // 2),
            (center_x + mouth_width, mouth_y + mouth_width // 2)
        ], start=0, end=180, fill=mouth_color, width=4)
        
        # 周圍的小星星
        star_color = (200, 255, 255, 200)
        for _ in range(6):
            star_x = center_x + random.randint(-radius * 2, radius * 2)
            star_y = center_y + random.randint(-radius, radius)
            if (abs(star_x - center_x) > radius + 30 or 
                abs(star_y - center_y) > radius + 30):
                self._draw_cute_star(draw, star_x, star_y, 4, star_color)

    def _draw_neptune_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製海王星的詳細設計 - 深藍色有環帶的可愛星球
        """
        # 海王星主體 - 深藍色
        neptune_color = (70, 130, 180, 255)  # 鋼藍色
        
        # 主體星球
        draw.ellipse([
            (center_x - radius, center_y - radius),
            (center_x + radius, center_y + radius)
        ], fill=neptune_color)
        
        # 漸層效果 - 從深藍到淺藍
        gradient_colors = [
            (90, 150, 200, 180),
            (110, 170, 220, 120),
            (130, 190, 240, 80)
        ]
        
        for i, color in enumerate(gradient_colors):
            gradient_radius = radius - i * 15
            if gradient_radius > 0:
                draw.ellipse([
                    (center_x - gradient_radius, center_y - gradient_radius),
                    (center_x + gradient_radius, center_y + gradient_radius)
                ], fill=color)
        
        # 大氣層漩渦紋理
        swirl_color = (50, 100, 150, 200)
        for i in range(4):
            swirl_radius = radius - i * 20
            if swirl_radius > 20:
                # 創建漩渦效果
                for angle in range(0, 360, 30):
                    angle_rad = math.radians(angle)
                    swirl_x = center_x + int(swirl_radius * 0.7 * math.cos(angle_rad))
                    swirl_y = center_y + int(swirl_radius * 0.7 * math.sin(angle_rad))
                    draw.ellipse([
                        (swirl_x - 3, swirl_y - 3),
                        (swirl_x + 3, swirl_y + 3)
                    ], fill=swirl_color)
        
        # 美麗的環帶系統（比土星更精緻）
        ring_colors = [
            (200, 200, 220, 200),  # 淺色主環
            (180, 180, 200, 150),  # 中色環
            (160, 160, 180, 100),  # 深色環
            (220, 220, 240, 120),  # 亮色環
        ]
        
        for i, ring_color in enumerate(ring_colors):
            ring_radius = radius + 30 + i * 12
            ring_thickness = 6 - i
            
            # 主環帶
            draw.ellipse([
                (center_x - ring_radius, center_y - ring_radius // 4),
                (center_x + ring_radius, center_y + ring_radius // 4)
            ], outline=ring_color, width=ring_thickness)
            
            # 環帶上的小顆粒效果
            if i == 0:  # 只在主環上添加顆粒
                for angle in range(0, 360, 15):
                    angle_rad = math.radians(angle)
                    particle_x = center_x + int(ring_radius * 0.9 * math.cos(angle_rad))
                    particle_y = center_y + int((ring_radius // 4) * 0.9 * math.sin(angle_rad))
                    draw.ellipse([
                        (particle_x - 1, particle_y - 1),
                        (particle_x + 1, particle_y + 1)
                    ], fill=ring_color)
        
        # 可愛表情 - 溫和友善的眼神
        eye_color = (255, 255, 255, 255)
        eye_size = radius // 5
        left_eye_x = center_x - radius // 3
        right_eye_x = center_x + radius // 3
        eye_y = center_y - radius // 4
        
        # 眼睛底色
        draw.ellipse([
            (left_eye_x - eye_size, eye_y - eye_size),
            (left_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        draw.ellipse([
            (right_eye_x - eye_size, eye_y - eye_size),
            (right_eye_x + eye_size, eye_y + eye_size)
        ], fill=eye_color)
        
        # 眼珠（深藍色）
        pupil_color = (20, 50, 100, 255)
        pupil_size = int(eye_size * 0.7)
        draw.ellipse([
            (left_eye_x - pupil_size, eye_y - pupil_size),
            (left_eye_x + pupil_size, eye_y + pupil_size)
        ], fill=pupil_color)
        draw.ellipse([
            (right_eye_x - pupil_size, eye_y - pupil_size),
            (right_eye_x + pupil_size, eye_y + pupil_size)
        ], fill=pupil_color)
        
        # 眼睛高光
        highlight_color = (255, 255, 255, 255)
        highlight_size = pupil_size // 3
        draw.ellipse([
            (left_eye_x - highlight_size, eye_y - pupil_size // 2 - highlight_size),
            (left_eye_x + highlight_size, eye_y - pupil_size // 2 + highlight_size)
        ], fill=highlight_color)
        draw.ellipse([
            (right_eye_x - highlight_size, eye_y - pupil_size // 2 - highlight_size),
            (right_eye_x + highlight_size, eye_y - pupil_size // 2 + highlight_size)
        ], fill=highlight_color)
        
        # 溫和的微笑
        mouth_color = (255, 255, 255, 255)
        mouth_y = center_y + radius // 3
        mouth_width = radius // 2
        
        # 繪製微笑弧線
        draw.arc([
            (center_x - mouth_width, mouth_y - mouth_width // 3),
            (center_x + mouth_width, mouth_y + mouth_width // 3)
        ], start=0, end=180, fill=mouth_color, width=5)
        
        # 可愛的腮紅
        blush_color = (255, 200, 200, 150)
        blush_size = radius // 8
        draw.ellipse([
            (center_x - radius // 2 - blush_size, center_y - blush_size),
            (center_x - radius // 2 + blush_size, center_y + blush_size)
        ], fill=blush_color)
        draw.ellipse([
            (center_x + radius // 2 - blush_size, center_y - blush_size),
            (center_x + radius // 2 + blush_size, center_y + blush_size)
        ], fill=blush_color)
        
        # 周圍的海洋波紋效果
        wave_color = (100, 200, 255, 100)
        for i in range(3):
            wave_radius = radius + 50 + i * 20
            draw.ellipse([
                (center_x - wave_radius, center_y - wave_radius),
                (center_x + wave_radius, center_y + wave_radius)
            ], outline=wave_color, width=2)
        
        # 周圍的小水滴
        drop_color = (150, 200, 255, 200)
        for _ in range(8):
            drop_x = center_x + random.randint(-radius * 2, radius * 2)
            drop_y = center_y + random.randint(-radius, radius)
            if (abs(drop_x - center_x) > radius + 40 or 
                abs(drop_y - center_y) > radius + 40):
                self._draw_water_drop(draw, drop_x, drop_y, 4, drop_color)
    
    def _draw_water_drop(self, draw: ImageDraw.Draw, center_x: int, center_y: int, size: int, color: Tuple[int, int, int, int]):
        """繪製可愛的小水滴"""
        # 水滴形狀
        drop_points = [
            (center_x, center_y - size),  # 頂點
            (center_x - size // 2, center_y),  # 左邊
            (center_x, center_y + size),  # 底部
            (center_x + size // 2, center_y),  # 右邊
        ]
        draw.polygon(drop_points, fill=color)
        
        # 高光效果
        highlight_color = (255, 255, 255, 200)
        draw.ellipse([
            (center_x - size // 3, center_y - size // 2),
            (center_x + size // 3, center_y)
        ], fill=highlight_color)
    
    def _add_button_text(self, draw: ImageDraw.Draw, text: str, img_width: int, img_height: int, text_color: Tuple[int, int, int], center_y: int, planet_radius: int):
        """
        添加按鈕文字 - 使用更明顯的顏色
        """
        # 清理文字，移除任何符號前綴
        clean_text = text.strip()
        # 如果文字開頭有表情符號或特殊符號，移除它們
        import re
        clean_text = re.sub(r'^[^\w\u4e00-\u9fff]+', '', clean_text)
        
        # 使用PIL的默認字體，但增大尺寸
        font_size = 48  # 增大字體
        
        # 創建一個簡單但有效的字體
        try:
            # 嘗試使用系統字體
            font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf", font_size)
        except:
            try:
                # 備用字體
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                # 最後使用默認字體
                font = ImageFont.load_default()
        
        # 計算文字位置
        bbox = draw.textbbox((0, 0), clean_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 文字水平居中
        text_x = (img_width - text_width) // 2
        # 文字位置在星球下方，保持適當間距
        text_y = center_y + planet_radius + 32  # 增加間距
        
        # 確保文字不會超出按鈕範圍
        if text_y + text_height > img_height - 20:
            text_y = img_height - text_height - 20
        
        # 繪製文字陰影 - 更深的陰影
        shadow_offsets = [(5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]
        shadow_colors = [(0, 0, 0, 255), (30, 30, 30, 200), (60, 60, 60, 150), (90, 90, 90, 100), (120, 120, 120, 50)]
        
        for (dx, dy), shadow_color in zip(shadow_offsets, shadow_colors):
            draw.text((text_x + dx, text_y + dy), clean_text, font=font, fill=shadow_color)
        
        # 繪製主要文字 - 使用明亮的黃白色
        main_text_color = (255, 255, 220, 255)  # 明亮的黃白色，比純白色更溫暖
        draw.text((text_x, text_y), clean_text, font=font, fill=main_text_color)
        
        # 添加文字高光效果 - 更亮的高光
        highlight_color = (255, 255, 255, 150)  # 更不透明的高光
        draw.text((text_x - 1, text_y - 1), clean_text, font=font, fill=highlight_color)
        
        # 添加文字邊框效果
        border_color = (200, 200, 150, 100)  # 淡金色邊框
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((text_x + dx, text_y + dy), clean_text, font=font, fill=border_color)
    
    def _draw_cute_star(self, draw: ImageDraw.Draw, center_x: int, center_y: int, size: int, color: Tuple[int, int, int, int]):
        """
        繪製可愛的小星星 - 手繪風格
        """
        # 簡單的十字星
        draw.line([(center_x - size, center_y), (center_x + size, center_y)], fill=color, width=2)
        draw.line([(center_x, center_y - size), (center_x, center_y + size)], fill=color, width=2)
        draw.line([(center_x - size//2, center_y - size//2), (center_x + size//2, center_y + size//2)], fill=color, width=1)
        draw.line([(center_x - size//2, center_y + size//2), (center_x + size//2, center_y - size//2)], fill=color, width=1)
    
    def _draw_astronaut_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製塗鴉風格的太空人 - 人形穿著連身太空服
        """
        # 太空人頭部（圓形頭盔內的頭部）
        head_color = (255, 220, 180, 255)  # 膚色
        head_radius = int(radius * 0.35)
        head_y = center_y - radius * 0.7
        
        # 頭部
        draw.ellipse([
            (center_x - head_radius, head_y - head_radius),
            (center_x + head_radius, head_y + head_radius)
        ], fill=head_color)
        
        # 太空人頭盔（透明圓形頭盔）
        helmet_color = (200, 230, 255, 120)  # 半透明藍色頭盔
        helmet_radius = int(radius * 0.45)
        
        # 頭盔主體
        draw.ellipse([
            (center_x - helmet_radius, head_y - helmet_radius),
            (center_x + helmet_radius, head_y + helmet_radius)
        ], fill=helmet_color)
        
        # 頭盔邊框（金屬邊框）
        helmet_border_color = (180, 180, 180, 255)
        draw.ellipse([
            (center_x - helmet_radius, head_y - helmet_radius),
            (center_x + helmet_radius, head_y + helmet_radius)
        ], outline=helmet_border_color, width=4)
        
        # 頭盔反光效果
        reflection_color = (255, 255, 255, 100)
        reflection_size = helmet_radius // 2
        draw.ellipse([
            (center_x - helmet_radius//3, head_y - helmet_radius//3),
            (center_x - helmet_radius//3 + reflection_size, head_y - helmet_radius//3 + reflection_size)
        ], fill=reflection_color)
        
        # 太空人臉部表情
        # 眼睛
        eye_size = 4
        left_eye_x = center_x - head_radius // 2
        right_eye_x = center_x + head_radius // 2
        eye_y = head_y - head_radius // 4
        
        eye_color = (50, 50, 50, 255)
        draw.ellipse([(left_eye_x - eye_size, eye_y - eye_size), 
                     (left_eye_x + eye_size, eye_y + eye_size)], fill=eye_color)
        draw.ellipse([(right_eye_x - eye_size, eye_y - eye_size), 
                     (right_eye_x + eye_size, eye_y + eye_size)], fill=eye_color)
        
        # 眼睛高光
        highlight_color = (255, 255, 255, 255)
        draw.ellipse([(left_eye_x - 1, eye_y - 2), (left_eye_x + 1, eye_y)], fill=highlight_color)
        draw.ellipse([(right_eye_x - 1, eye_y - 2), (right_eye_x + 1, eye_y)], fill=highlight_color)
        
        # 嘴巴 - 開心的笑容
        mouth_y = head_y + head_radius // 4
        mouth_width = head_radius // 2
        mouth_color = (200, 100, 50, 255)
        
        # 繪製微笑弧線
        for i in range(mouth_width):
            x = center_x - mouth_width // 2 + i
            y_offset = int(4 * math.sin(math.pi * i / mouth_width))
            draw.ellipse([(x - 1, mouth_y + y_offset - 1), 
                         (x + 1, mouth_y + y_offset + 1)], fill=mouth_color)
        
        # 連身太空服身體（橢圓形連身設計）
        body_color = (240, 240, 240, 255)  # 白色太空服
        body_width = int(radius * 1.2)
        body_height = int(radius * 1.8)
        body_y = center_y + radius * 0.1
        
        # 連身太空服主體（橢圓形）
        draw.ellipse([
            (center_x - body_width // 2, body_y - body_height // 2),
            (center_x + body_width // 2, body_y + body_height // 2)
        ], fill=body_color)
        
        # 太空服邊框
        body_border_color = (200, 200, 200, 255)
        draw.ellipse([
            (center_x - body_width // 2, body_y - body_height // 2),
            (center_x + body_width // 2, body_y + body_height // 2)
        ], outline=body_border_color, width=3)
        
        # 胸前控制面板
        panel_color = (100, 100, 100, 255)
        panel_width = body_width // 2
        panel_height = body_height // 4
        panel_y = body_y - body_height // 4
        
        draw.rectangle([
            (center_x - panel_width // 2, panel_y - panel_height // 2),
            (center_x + panel_width // 2, panel_y + panel_height // 2)
        ], fill=panel_color)
        
        # 控制面板按鈕
        button_colors = [(255, 100, 100, 255), (100, 255, 100, 255), (100, 100, 255, 255)]
        button_positions = [
            (center_x - 12, panel_y - 8),
            (center_x, panel_y - 8),
            (center_x + 12, panel_y - 8),
            (center_x - 6, panel_y + 6),
            (center_x + 6, panel_y + 6)
        ]
        
        for i, (btn_x, btn_y) in enumerate(button_positions):
            btn_color = button_colors[i % len(button_colors)]
            draw.ellipse([(btn_x - 2, btn_y - 2), (btn_x + 2, btn_y + 2)], fill=btn_color)
        
        # 連身太空服的手臂部分（從身體延伸出來）
        arm_color = (220, 220, 220, 255)
        
        # 左手臂（從身體側面延伸）
        left_arm_start_x = center_x - body_width // 2 + 10
        left_arm_start_y = body_y - body_height // 3
        left_arm_end_x = center_x - body_width // 2 - 25
        left_arm_end_y = body_y - body_height // 6
        
        # 左手臂（橢圓形）
        arm_width = 20
        arm_height = 35
        draw.ellipse([
            (left_arm_end_x - arm_width // 2, left_arm_end_y - arm_height // 2),
            (left_arm_end_x + arm_width // 2, left_arm_end_y + arm_height // 2)
        ], fill=arm_color)
        
        # 右手臂（從身體側面延伸）
        right_arm_start_x = center_x + body_width // 2 - 10
        right_arm_start_y = body_y - body_height // 3
        right_arm_end_x = center_x + body_width // 2 + 25
        right_arm_end_y = body_y - body_height // 6
        
        # 右手臂（橢圓形）
        draw.ellipse([
            (right_arm_end_x - arm_width // 2, right_arm_end_y - arm_height // 2),
            (right_arm_end_x + arm_width // 2, right_arm_end_y + arm_height // 2)
        ], fill=arm_color)
        
        # 太空手套
        glove_color = (200, 200, 200, 255)
        glove_size = 12
        
        # 左手套
        draw.ellipse([(left_arm_end_x - glove_size, left_arm_end_y + arm_height // 2 - 5), 
                     (left_arm_end_x + glove_size, left_arm_end_y + arm_height // 2 + 15)], fill=glove_color)
        
        # 右手套
        draw.ellipse([(right_arm_end_x - glove_size, right_arm_end_y + arm_height // 2 - 5), 
                     (right_arm_end_x + glove_size, right_arm_end_y + arm_height // 2 + 15)], fill=glove_color)
        
        # 連身太空服的腿部部分（從身體下方延伸）
        leg_color = (220, 220, 220, 255)
        
        # 左腿（橢圓形）
        left_leg_x = center_x - body_width // 4
        left_leg_y = body_y + body_height // 2 + 20
        leg_width = 25
        leg_height = 45
        
        draw.ellipse([
            (left_leg_x - leg_width // 2, left_leg_y - leg_height // 2),
            (left_leg_x + leg_width // 2, left_leg_y + leg_height // 2)
        ], fill=leg_color)
        
        # 右腿（橢圓形）
        right_leg_x = center_x + body_width // 4
        right_leg_y = body_y + body_height // 2 + 20
        
        draw.ellipse([
            (right_leg_x - leg_width // 2, right_leg_y - leg_height // 2),
            (right_leg_x + leg_width // 2, right_leg_y + leg_height // 2)
        ], fill=leg_color)
        
        # 太空靴
        boot_color = (180, 180, 180, 255)
        boot_width = 18
        boot_height = 12
        
        # 左靴
        draw.ellipse([(left_leg_x - boot_width, left_leg_y + leg_height // 2 - 5), 
                     (left_leg_x + boot_width, left_leg_y + leg_height // 2 + boot_height)], fill=boot_color)
        
        # 右靴
        draw.ellipse([(right_leg_x - boot_width, right_leg_y + leg_height // 2 - 5), 
                     (right_leg_x + boot_width, right_leg_y + leg_height // 2 + boot_height)], fill=boot_color)
        
        # 生命維持背包
        backpack_color = (160, 160, 160, 255)
        backpack_width = 20
        backpack_height = 35
        backpack_x = center_x + body_width // 2 - 8
        backpack_y = body_y - body_height // 4
        
        draw.rectangle([
            (backpack_x, backpack_y - backpack_height // 2),
            (backpack_x + backpack_width, backpack_y + backpack_height // 2)
        ], fill=backpack_color)
        
        # 氧氣管線
        tube_color = (100, 100, 100, 255)
        draw.line([(backpack_x, backpack_y - 5), (center_x + helmet_radius - 5, head_y + helmet_radius // 2)], 
                 fill=tube_color, width=3)
        
        # 太空服上的裝飾線條
        decoration_color = (180, 180, 180, 255)
        # 胸前裝飾線
        draw.line([(center_x - body_width // 3, body_y - body_height // 3), 
                  (center_x + body_width // 3, body_y - body_height // 3)], 
                 fill=decoration_color, width=2)
        # 腰部裝飾線
        draw.line([(center_x - body_width // 2 + 10, body_y), 
                  (center_x + body_width // 2 - 10, body_y)], 
                 fill=decoration_color, width=2)
        
        # 周圍的小星星
        star_color = (255, 255, 100, 200)
        for _ in range(6):
            star_x = center_x + random.randint(-radius * 2, radius * 2)
            star_y = center_y + random.randint(-radius, radius)
            if abs(star_x - center_x) > body_width // 2 + 30:  # 在太空人外
                self._draw_cute_star(draw, star_x, star_y, random.randint(3, 5), star_color)
    
    def _draw_satellite_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製塗鴉風格的衛星 - 可愛的手繪風格
        """
        # 衛星主體 - 方形金屬外殼
        body_color = (180, 180, 180, 255)  # 銀灰色
        body_size = int(radius * 1.2)
        body_left = center_x - body_size // 2
        body_top = center_y - body_size // 2
        body_right = center_x + body_size // 2
        body_bottom = center_y + body_size // 2
        
        draw.rectangle([
            (body_left, body_top),
            (body_right, body_bottom)
        ], fill=body_color)
        
        # 衛星邊框
        border_color = (150, 150, 150, 255)
        draw.rectangle([
            (body_left, body_top),
            (body_right, body_bottom)
        ], outline=border_color, width=4)
        
        # 太陽能板 - 左側
        solar_panel_color = (50, 50, 150, 255)  # 深藍色
        panel_width = body_size // 2
        panel_height = body_size * 1.5
        
        # 左太陽能板
        left_panel_x = body_left - panel_width - 10
        left_panel_y = center_y - panel_height // 2
        draw.rectangle([
            (left_panel_x, left_panel_y),
            (left_panel_x + panel_width, left_panel_y + panel_height)
        ], fill=solar_panel_color)
        
        # 右太陽能板
        right_panel_x = body_right + 10
        right_panel_y = center_y - panel_height // 2
        draw.rectangle([
            (right_panel_x, right_panel_y),
            (right_panel_x + panel_width, right_panel_y + panel_height)
        ], fill=solar_panel_color)
        
        # 太陽能板格線
        grid_color = (80, 80, 180, 255)
        # 左面板格線
        for i in range(1, 4):
            y = left_panel_y + i * panel_height // 4
            draw.line([(left_panel_x, y), (left_panel_x + panel_width, y)], 
                     fill=grid_color, width=2)
        for i in range(1, 3):
            x = left_panel_x + i * panel_width // 3
            draw.line([(x, left_panel_y), (x, left_panel_y + panel_height)], 
                     fill=grid_color, width=2)
        
        # 右面板格線
        for i in range(1, 4):
            y = right_panel_y + i * panel_height // 4
            draw.line([(right_panel_x, y), (right_panel_x + panel_width, y)], 
                     fill=grid_color, width=2)
        for i in range(1, 3):
            x = right_panel_x + i * panel_width // 3
            draw.line([(x, right_panel_y), (x, right_panel_y + panel_height)], 
                     fill=grid_color, width=2)
        
        # 衛星天線
        antenna_color = (200, 200, 200, 255)
        antenna_base_x = center_x
        antenna_base_y = body_top
        antenna_tip_x = center_x
        antenna_tip_y = body_top - radius // 2
        
        # 主天線桿
        draw.line([(antenna_base_x, antenna_base_y), (antenna_tip_x, antenna_tip_y)], 
                 fill=antenna_color, width=6)
        
        # 天線頂部
        antenna_top_size = 8
        draw.ellipse([
            (antenna_tip_x - antenna_top_size, antenna_tip_y - antenna_top_size),
            (antenna_tip_x + antenna_top_size, antenna_tip_y + antenna_top_size)
        ], fill=antenna_color)
        
        # 側面小天線
        side_antenna_color = (180, 180, 180, 255)
        # 左側天線
        left_antenna_start_x = body_left
        left_antenna_start_y = center_y - body_size // 4
        left_antenna_end_x = body_left - 20
        left_antenna_end_y = center_y - body_size // 4
        draw.line([(left_antenna_start_x, left_antenna_start_y), 
                  (left_antenna_end_x, left_antenna_end_y)], 
                 fill=side_antenna_color, width=4)
        
        # 右側天線
        right_antenna_start_x = body_right
        right_antenna_start_y = center_y - body_size // 4
        right_antenna_end_x = body_right + 20
        right_antenna_end_y = center_y - body_size // 4
        draw.line([(right_antenna_start_x, right_antenna_start_y), 
                  (right_antenna_end_x, right_antenna_end_y)], 
                 fill=side_antenna_color, width=4)
        
        # 衛星可愛表情
        # 眼睛
        eye_size = 8
        left_eye_x = center_x - body_size // 4
        right_eye_x = center_x + body_size // 4
        eye_y = center_y - body_size // 4
        
        eye_color = (50, 50, 50, 255)
        draw.ellipse([(left_eye_x - eye_size, eye_y - eye_size), 
                     (left_eye_x + eye_size, eye_y + eye_size)], fill=eye_color)
        draw.ellipse([(right_eye_x - eye_size, eye_y - eye_size), 
                     (right_eye_x + eye_size, eye_y + eye_size)], fill=eye_color)
        
        # 眼睛高光
        highlight_color = (255, 255, 255, 255)
        draw.ellipse([(left_eye_x - 2, eye_y - 4), (left_eye_x + 2, eye_y)], fill=highlight_color)
        draw.ellipse([(right_eye_x - 2, eye_y - 4), (right_eye_x + 2, eye_y)], fill=highlight_color)
        
        # 嘴巴 - 專注的表情
        mouth_y = center_y + body_size // 4
        mouth_width = body_size // 3
        mouth_color = (100, 100, 100, 255)
        
        # 繪製直線嘴巴（專注表情）
        draw.line([(center_x - mouth_width // 2, mouth_y), 
                  (center_x + mouth_width // 2, mouth_y)], 
                 fill=mouth_color, width=4)
        
        # 衛星設備指示燈
        light_colors = [(255, 100, 100, 255), (100, 255, 100, 255), (100, 100, 255, 255)]
        light_positions = [
            (center_x - body_size // 3, center_y + body_size // 3),
            (center_x, center_y + body_size // 3),
            (center_x + body_size // 3, center_y + body_size // 3)
        ]
        
        for i, (light_x, light_y) in enumerate(light_positions):
            light_color = light_colors[i]
            light_size = 4
            draw.ellipse([(light_x - light_size, light_y - light_size), 
                         (light_x + light_size, light_y + light_size)], fill=light_color)
        
        # 信號波紋效果
        signal_color = (100, 255, 100, 100)
        for i in range(3):
            wave_radius = antenna_top_size + (i + 1) * 15
            draw.ellipse([
                (antenna_tip_x - wave_radius, antenna_tip_y - wave_radius),
                (antenna_tip_x + wave_radius, antenna_tip_y + wave_radius)
            ], outline=signal_color, width=2)
        
        # 周圍的小星星
        star_color = (255, 255, 100, 200)
        for _ in range(6):
            star_x = center_x + random.randint(-radius * 2, radius * 2)
            star_y = center_y + random.randint(-radius, radius)
            if (abs(star_x - center_x) > body_size + 50 or 
                abs(star_y - center_y) > body_size + 50):  # 在衛星外
                self._draw_cute_star(draw, star_x, star_y, 4, star_color)
    
    def _draw_clock_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製塗鴉風格的時鐘 - 可愛的手繪風格
        """
        # 時鐘外框 - 圓形
        clock_color = (255, 220, 150, 255)  # 溫暖的金黃色
        clock_radius = int(radius * 0.9)
        draw.ellipse([
            (center_x - clock_radius, center_y - clock_radius),
            (center_x + clock_radius, center_y + clock_radius)
        ], fill=clock_color)
        
        # 時鐘邊框
        border_color = (200, 150, 100, 255)
        draw.ellipse([
            (center_x - clock_radius, center_y - clock_radius),
            (center_x + clock_radius, center_y + clock_radius)
        ], outline=border_color, width=6)
        
        # 時鐘刻度 - 12個小時刻度
        tick_color = (150, 100, 50, 255)
        for hour in range(12):
            angle = hour * 30 - 90  # 從12點開始
            angle_rad = math.radians(angle)
            
            # 外圈刻度點
            outer_x = center_x + int((clock_radius - 15) * math.cos(angle_rad))
            outer_y = center_y + int((clock_radius - 15) * math.sin(angle_rad))
            
            # 內圈刻度點
            inner_x = center_x + int((clock_radius - 25) * math.cos(angle_rad))
            inner_y = center_y + int((clock_radius - 25) * math.sin(angle_rad))
            
            # 主要刻度（12, 3, 6, 9點）
            if hour % 3 == 0:
                draw.line([(inner_x, inner_y), (outer_x, outer_y)], 
                         fill=tick_color, width=4)
            else:
                # 次要刻度
                draw.line([(inner_x, inner_y), (outer_x, outer_y)], 
                         fill=tick_color, width=2)
        
        # 時鐘數字 - 手繪風格的數字
        number_color = (100, 50, 0, 255)
        number_positions = [
            (center_x, center_y - clock_radius + 35, "12"),
            (center_x + clock_radius - 35, center_y, "3"),
            (center_x, center_y + clock_radius - 35, "6"),
            (center_x - clock_radius + 35, center_y, "9")
        ]
        
        for num_x, num_y, number in number_positions:
            # 簡單的數字繪製（用小圓點組成）
            if number == "12":
                # 1
                draw.line([(num_x - 8, num_y - 8), (num_x - 8, num_y + 8)], 
                         fill=number_color, width=3)
                # 2
                draw.arc([(num_x - 2, num_y - 8), (num_x + 6, num_y)], 
                        start=0, end=180, fill=number_color, width=3)
                draw.line([(num_x - 2, num_y), (num_x + 6, num_y + 8)], 
                         fill=number_color, width=3)
                draw.line([(num_x - 2, num_y + 8), (num_x + 6, num_y + 8)], 
                         fill=number_color, width=3)
            elif number == "3":
                draw.arc([(num_x - 6, num_y - 8), (num_x + 6, num_y + 8)], 
                        start=270, end=90, fill=number_color, width=3)
                draw.line([(num_x, num_y), (num_x + 4, num_y)], 
                         fill=number_color, width=3)
            elif number == "6":
                draw.ellipse([(num_x - 6, num_y - 8), (num_x + 6, num_y + 8)], 
                           outline=number_color, width=3)
                draw.arc([(num_x - 4, num_y - 2), (num_x + 4, num_y + 6)], 
                        start=0, end=180, fill=number_color, width=3)
            elif number == "9":
                draw.ellipse([(num_x - 6, num_y - 8), (num_x + 6, num_y + 8)], 
                           outline=number_color, width=3)
                draw.arc([(num_x - 4, num_y - 6), (num_x + 4, num_y + 2)], 
                        start=180, end=360, fill=number_color, width=3)
        
        # 時鐘指針 - 顯示大約2:30的時間
        needle_color = (100, 50, 0, 255)
        
        # 時針（短針）- 指向2點多
        hour_angle = math.radians(30 * 2.5 - 90)  # 2:30
        hour_length = clock_radius * 0.5
        hour_end_x = center_x + int(hour_length * math.cos(hour_angle))
        hour_end_y = center_y + int(hour_length * math.sin(hour_angle))
        draw.line([(center_x, center_y), (hour_end_x, hour_end_y)], 
                 fill=needle_color, width=6)
        
        # 分針（長針）- 指向6點（30分）
        minute_angle = math.radians(6 * 30 - 90)  # 30分鐘
        minute_length = clock_radius * 0.7
        minute_end_x = center_x + int(minute_length * math.cos(minute_angle))
        minute_end_y = center_y + int(minute_length * math.sin(minute_angle))
        draw.line([(center_x, center_y), (minute_end_x, minute_end_y)], 
                 fill=needle_color, width=4)
        
        # 中心點
        center_dot_color = (150, 100, 50, 255)
        center_dot_size = 8
        draw.ellipse([
            (center_x - center_dot_size, center_y - center_dot_size),
            (center_x + center_dot_size, center_y + center_dot_size)
        ], fill=center_dot_color)
        
        # 時鐘可愛表情
        # 眼睛 - 在時鐘上方
        eye_size = 6
        left_eye_x = center_x - clock_radius // 3
        right_eye_x = center_x + clock_radius // 3
        eye_y = center_y - clock_radius // 2
        
        eye_color = (100, 50, 0, 255)
        draw.ellipse([(left_eye_x - eye_size, eye_y - eye_size), 
                     (left_eye_x + eye_size, eye_y + eye_size)], fill=eye_color)
        draw.ellipse([(right_eye_x - eye_size, eye_y - eye_size), 
                     (right_eye_x + eye_size, eye_y + eye_size)], fill=eye_color)
        
        # 嘴巴 - 在時鐘下方，微笑
        mouth_y = center_y + clock_radius // 2
        mouth_width = clock_radius // 3
        mouth_color = (150, 100, 50, 255)
        
        # 繪製微笑弧線
        for i in range(mouth_width):
            x = center_x - mouth_width // 2 + i
            y_offset = int(8 * math.sin(math.pi * i / mouth_width))
            draw.ellipse([(x - 2, mouth_y + y_offset - 2), 
                         (x + 2, mouth_y + y_offset + 2)], fill=mouth_color)
        
        # 時鐘周圍的時間符號
        time_symbol_color = (255, 200, 100, 200)
        
        for i in range(6):
            symbol_angle = i * 60
            symbol_angle_rad = math.radians(symbol_angle)
            symbol_distance = clock_radius + 30
            
            symbol_x = center_x + int(symbol_distance * math.cos(symbol_angle_rad))
            symbol_y = center_y + int(symbol_distance * math.sin(symbol_angle_rad))
            
            # 繪製小時鐘符號（用小圓和線條代替）
            symbol_size = 6
            draw.ellipse([
                (symbol_x - symbol_size, symbol_y - symbol_size),
                (symbol_x + symbol_size, symbol_y + symbol_size)
            ], outline=time_symbol_color, width=2)
            
            # 小指針
            draw.line([(symbol_x, symbol_y), 
                      (symbol_x + 3, symbol_y - 3)], 
                     fill=time_symbol_color, width=2)
            draw.line([(symbol_x, symbol_y), 
                      (symbol_x + 2, symbol_y + 4)], 
                     fill=time_symbol_color, width=1)
    
    def generate_rich_menu_image(self, output_path: str = "rich_menu_starry_sky.png") -> str:
        """
        生成完整的 Rich Menu 圖片
        """
        # 創建星空背景
        image = self.create_starry_background()
        
        # 添加所有星球按鈕
        for button_config in self.buttons:
            button_img, position = self.create_planet_button(button_config)
            
            # 將按鈕貼到主圖片上
            image.alpha_composite(button_img, position)
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # 保存圖片
        image.save(output_path, "PNG")
        
        return output_path
    
    def get_button_areas(self) -> List[Dict]:
        """
        獲取按鈕區域配置（用於 Rich Menu API）
        """
        areas = []
        
        for button in self.buttons:
            # 計算新的按鈕尺寸（與 create_planet_button 保持一致）
            size = button["size"]
            button_width = int(size * 2.8)
            button_height = int(size * 3.0)
            
            # 按鈕區域 (x, y, width, height)
            area = {
                "bounds": {
                    "x": button["x"] - button_width // 2,
                    "y": button["y"] - button_height // 2,
                    "width": button_width,
                    "height": button_height
                },
                "action": {
                    "type": "message",
                    "text": button["action_text"]
                }
            }
            areas.append(area)
        
        return areas

    def generate_three_zone_positions(self, num_buttons: int, width: int, height: int) -> List[Tuple[int, int]]:
        """
        生成三區塊分佈的按鈕位置：左邊2個，中間2個，右邊3個
        """
        import random
        
        positions = []
        
        # 設定安全邊界
        margin_x = 200
        margin_y = 150
        
        # 將寬度分成三個區塊
        zone_width = (width - 2 * margin_x) // 3
        
        # 定義三個區塊的範圍
        zones = [
            {"start_x": margin_x, "end_x": margin_x + zone_width, "count": 2},  # 左邊區塊
            {"start_x": margin_x + zone_width, "end_x": margin_x + 2 * zone_width, "count": 2},  # 中間區塊
            {"start_x": margin_x + 2 * zone_width, "end_x": width - margin_x, "count": 3}  # 右邊區塊
        ]
        
        button_index = 0
        
        for zone in zones:
            zone_start_x = zone["start_x"]
            zone_end_x = zone["end_x"]
            zone_count = zone["count"]
            
            # 在每個區塊內隨機分佈按鈕
            for i in range(zone_count):
                if button_index >= num_buttons:
                    break
                
                # 在區塊內隨機選擇位置
                x = random.randint(zone_start_x + 50, zone_end_x - 50)
                y = random.randint(margin_y, height - margin_y)
                
                # 確保與同區塊內其他按鈕有足夠距離
                attempts = 0
                while attempts < 50:
                    valid = True
                    for existing_x, existing_y in positions:
                        distance = ((x - existing_x)**2 + (y - existing_y)**2)**0.5
                        if distance < 200:  # 最小距離
                            valid = False
                            break
                    
                    if valid:
                        break
                    
                    # 重新生成位置
                    x = random.randint(zone_start_x + 50, zone_end_x - 50)
                    y = random.randint(margin_y, height - margin_y)
                    attempts += 1
                
                positions.append((x, y))
                button_index += 1
        
        return positions

# 全局實例
rich_menu_image_generator = RichMenuImageGenerator()

def generate_admin_starry_rich_menu(output_path: str = "rich_menu_images/admin_starry_sky_menu.png") -> Tuple[str, List[Dict]]:
    """生成管理員版本的星空主題 Rich Menu 圖片"""
    
    # 管理員選單按鈕配置 (7個按鈕)
    admin_buttons = [
        {"text": "本週占卜", "color": (255, 200, 100), "planet": "太陽"},
        {"text": "流年運勢", "color": (100, 200, 255), "planet": "地球"},
        {"text": "流月運勢", "color": (200, 200, 200), "planet": "月球"},
        {"text": "流日運勢", "color": (70, 130, 180), "planet": "海王星"},  # 替換為海王星
        {"text": "命盤綁定", "color": (255, 100, 100), "planet": "火箭", "rocket_style": "space_shuttle"},  # 太空梭造型
        {"text": "會員資訊", "color": (180, 180, 180), "planet": "衛星"},
        {"text": "指定時間", "color": (255, 215, 0), "planet": "時鐘"}
    ]
    
    # 創建圖片生成器
    generator = RichMenuImageGenerator()
    
    # 生成星空背景
    background = generator.create_starry_background()
    
    # 生成按鈕位置（3區域分佈）
    button_positions = generator.generate_three_zone_positions(
        num_buttons=7,
        width=LineBotConfig.RICH_MENU_WIDTH,
        height=LineBotConfig.RICH_MENU_HEIGHT
    )
    
    # 在背景上繪製按鈕
    for i, button_config in enumerate(admin_buttons):
        if i < len(button_positions):
            # 創建按鈕圖片
            button_img, _ = generator.create_planet_button(button_config)
            
            # 計算按鈕位置
            x, y = button_positions[i]
            button_x = x - button_img.width // 2
            button_y = y - button_img.height // 2
            
            # 將按鈕貼到背景上
            background.paste(button_img, (button_x, button_y), button_img)
    
    # 保存圖片
    background.save(output_path)
    
    # 生成按鈕區域配置
    button_areas = []
    for i, button_config in enumerate(admin_buttons):
        if i < len(button_positions):
            x, y = button_positions[i]
            button_areas.append({
                "bounds": {
                    "x": max(0, x - 100),
                    "y": max(0, y - 100),
                    "width": 200,
                    "height": 200
                },
                "action": {
                    "type": "message",
                    "text": button_config["text"]
                }
            })
    
    return output_path, button_areas

def generate_starry_rich_menu(output_path: str = "rich_menu_images/starry_sky_menu.png") -> Tuple[str, List[Dict]]:
    """
    生成星空主題 Rich Menu 的便捷函數（一般會員版本）
    使用三區塊分佈：左邊2個，中間2個，右邊2個（共6個按鈕）
    
    Returns:
        Tuple[str, List[Dict]]: (圖片路徑, 按鈕區域配置)
    """
    from app.config.linebot_config import LineBotConfig
    
    def generate_three_zone_positions_6buttons(num_buttons: int, width: int, height: int) -> List[Tuple[int, int]]:
        """
        生成三區塊分佈的按鈕位置：左邊2個，中間2個，右邊2個（共6個按鈕）
        
        Args:
            num_buttons: 按鈕數量
            width: 選單寬度
            height: 選單高度
            
        Returns:
            List[Tuple[int, int]]: 按鈕位置列表 (x, y)
        """
        import random
        
        positions = []
        
        # 設定安全邊界
        margin_x = 200
        margin_y = 150
        
        # 將寬度分成三個區塊
        zone_width = (width - 2 * margin_x) // 3
        
        # 定義三個區塊的範圍（每個區塊2個按鈕）
        zones = [
            {"start_x": margin_x, "end_x": margin_x + zone_width, "count": 2},  # 左邊區塊
            {"start_x": margin_x + zone_width, "end_x": margin_x + 2 * zone_width, "count": 2},  # 中間區塊
            {"start_x": margin_x + 2 * zone_width, "end_x": width - margin_x, "count": 2}  # 右邊區塊
        ]
        
        button_index = 0
        
        for zone in zones:
            zone_start_x = zone["start_x"]
            zone_end_x = zone["end_x"]
            zone_count = zone["count"]
            
            # 在每個區塊內隨機分佈按鈕
            for i in range(zone_count):
                if button_index >= num_buttons:
                    break
                
                # 在區塊內隨機選擇位置
                x = random.randint(zone_start_x + 50, zone_end_x - 50)
                y = random.randint(margin_y, height - margin_y)
                
                # 確保與同區塊內其他按鈕有足夠距離
                attempts = 0
                while attempts < 50:
                    valid = True
                    for existing_x, existing_y in positions:
                        distance = ((x - existing_x)**2 + (y - existing_y)**2)**0.5
                        if distance < 200:  # 最小距離
                            valid = False
                            break
                    
                    if valid:
                        break
                    
                    # 重新生成位置
                    x = random.randint(zone_start_x + 50, zone_end_x - 50)
                    y = random.randint(margin_y, height - margin_y)
                    attempts += 1
                
                positions.append((x, y))
                button_index += 1
        
        return positions
    
    # 生成三區塊分佈的按鈕位置
    button_positions = generate_three_zone_positions_6buttons(
        num_buttons=6,
        width=LineBotConfig.RICH_MENU_WIDTH,
        height=LineBotConfig.RICH_MENU_HEIGHT
    )
    
    # 更新一般會員按鈕配置，使用三區塊分佈
    member_buttons = [
        {
            "name": "divination",
            "text": "本週占卜", 
            "action_text": "本週占卜",
            "x": button_positions[0][0],
            "y": button_positions[0][1],
            "size": 170,
            "color": "#FFD700",  # 金色 - 太陽樣式
            "planet": "太陽"
        },
        {
            "name": "yearly_fortune", 
            "text": "流年運勢",
            "action_text": "流年運勢", 
            "x": button_positions[1][0],
            "y": button_positions[1][1],
            "size": 170,
            "color": "#4682B4",  # 鋼藍色 - 地球樣式
            "planet": "地球"
        },
        {
            "name": "monthly_fortune",
            "text": "流月運勢", 
            "action_text": "流月運勢",
            "x": button_positions[2][0],
            "y": button_positions[2][1],
            "size": 170,
            "color": "#C0C0C0",  # 銀色 - 月球樣式
            "planet": "月球"
        },
        {
            "name": "daily_fortune",
            "text": "流日運勢",
            "action_text": "流日運勢", 
            "x": button_positions[3][0],
            "y": button_positions[3][1],
            "size": 160,
            "color": "#DAA520",  # 金棕色 - 土星樣式
            "planet": "土星"
        },
        {
            "name": "chart_binding",
            "text": "命盤綁定",
            "action_text": "命盤綁定",
            "x": button_positions[4][0],
            "y": button_positions[4][1],
            "size": 160,
            "color": "#FF4500",  # 橙紅色 - 太空人樣式
            "planet": "太空人"
        },
        {
            "name": "member_info",
            "text": "會員資訊", 
            "action_text": "會員資訊",
            "x": button_positions[5][0],
            "y": button_positions[5][1],
            "size": 160,
            "color": "#00CED1",  # 暗綠松石色 - 衛星樣式
            "planet": "衛星"
        }
    ]
    
    # 創建圖片生成器實例
    generator = RichMenuImageGenerator()
    
    # 臨時替換按鈕配置
    original_buttons = generator.buttons
    generator.buttons = member_buttons
    
    try:
        # 生成圖片
        image_path = generator.generate_rich_menu_image(output_path)
        
        # 獲取按鈕區域
        button_areas = generator.get_button_areas()
        
        return image_path, button_areas
        
    finally:
        # 恢復原始按鈕配置
        generator.buttons = original_buttons

# 導出
__all__ = [
    "RichMenuImageGenerator",
    "rich_menu_image_generator", 
    "generate_starry_rich_menu"
]

# 添加缺失的輔助函數
def _draw_shuttle_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, width: int, height: int):
    """太空梭表情"""
    eye_color = (255, 255, 255, 255)
    eye_width = width // 6
    eye_height = height // 4
    
    draw.ellipse([
        (center_x - width // 4 - eye_width // 2, center_y - eye_height // 2),
        (center_x - width // 4 + eye_width // 2, center_y + eye_height // 2)
    ], fill=eye_color)
    
    draw.ellipse([
        (center_x + width // 4 - eye_width // 2, center_y - eye_height // 2),
        (center_x + width // 4 + eye_width // 2, center_y + eye_height // 2)
    ], fill=eye_color)
    
    pupil_color = (50, 50, 50, 255)
    pupil_size = eye_width // 2
    
    draw.ellipse([
        (center_x - width // 4 - pupil_size // 2, center_y - pupil_size // 2),
        (center_x - width // 4 + pupil_size // 2, center_y + pupil_size // 2)
    ], fill=pupil_color)
    
    draw.ellipse([
        (center_x + width // 4 - pupil_size // 2, center_y - pupil_size // 2),
        (center_x + width // 4 + pupil_size // 2, center_y + pupil_size // 2)
    ], fill=pupil_color)
    
    mouth_color = (200, 200, 200, 255)
    draw.line([
        (center_x - width // 6, center_y + height // 4),
        (center_x + width // 6, center_y + height // 4)
    ], fill=mouth_color, width=2)

def _draw_shuttle_flames(self, draw: ImageDraw.Draw, center_x: int, flame_y: int, width: int):
    """太空梭火焰效果"""
    flame_colors = [
        (255, 200, 0, 255),
        (255, 100, 0, 200),
        (255, 255, 255, 180)
    ]
    
    for i, color in enumerate(flame_colors):
        flame_height = 40 - i * 10
        flame_width = width // 3 - i * 5
        
        flame_points = [
            (center_x - flame_width // 2, flame_y),
            (center_x - flame_width // 4, flame_y + flame_height // 2),
            (center_x, flame_y + flame_height),
            (center_x + flame_width // 4, flame_y + flame_height // 2),
            (center_x + flame_width // 2, flame_y)
        ]
        draw.polygon(flame_points, fill=color)
    
    side_flame_color = (255, 150, 0, 150)
    side_flame_size = width // 8
    
    draw.ellipse([
        (center_x - width // 2 - side_flame_size, flame_y - side_flame_size),
        (center_x - width // 2, flame_y + side_flame_size)
    ], fill=side_flame_color)
    
    draw.ellipse([
        (center_x + width // 2, flame_y - side_flame_size),
        (center_x + width // 2 + side_flame_size, flame_y + side_flame_size)
    ], fill=side_flame_color)

def _draw_mini_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, window_size: int):
    """迷你火箭表情"""
    eye_color = (255, 255, 255, 255)
    eye_radius = window_size // 6
    
    draw.ellipse([
        (center_x - window_size // 4 - eye_radius, center_y - eye_radius),
        (center_x - window_size // 4 + eye_radius, center_y + eye_radius)
    ], fill=eye_color)
    
    draw.ellipse([
        (center_x + window_size // 4 - eye_radius, center_y - eye_radius),
        (center_x + window_size // 4 + eye_radius, center_y + eye_radius)
    ], fill=eye_color)
    
    pupil_color = (50, 50, 50, 255)
    pupil_radius = eye_radius // 2
    
    draw.ellipse([
        (center_x - window_size // 4 - pupil_radius, center_y - pupil_radius),
        (center_x - window_size // 4 + pupil_radius, center_y + pupil_radius)
    ], fill=pupil_color)
    
    draw.ellipse([
        (center_x + window_size // 4 - pupil_radius, center_y - pupil_radius),
        (center_x + window_size // 4 + pupil_radius, center_y + pupil_radius)
    ], fill=pupil_color)
    
    highlight_color = (255, 255, 255, 255)
    highlight_size = pupil_radius // 3
    
    draw.ellipse([
        (center_x - window_size // 4 - highlight_size, center_y - highlight_size),
        (center_x - window_size // 4 + highlight_size, center_y + highlight_size)
    ], fill=highlight_color)
    
    draw.ellipse([
        (center_x + window_size // 4 - highlight_size, center_y - highlight_size),
        (center_x + window_size // 4 + highlight_size, center_y + highlight_size)
    ], fill=highlight_color)
    
    mouth_color = (255, 100, 100, 255)
    mouth_radius = window_size // 8
    
    draw.ellipse([
        (center_x - mouth_radius, center_y + window_size // 6 - mouth_radius),
        (center_x + mouth_radius, center_y + window_size // 6 + mouth_radius)
    ], fill=mouth_color)

def _draw_mini_flames(self, draw: ImageDraw.Draw, center_x: int, flame_y: int, width: int):
    """迷你火箭火焰效果"""
    flame_colors = [
        (255, 200, 100, 255),
        (255, 150, 100, 200),
        (255, 100, 150, 150)
    ]
    
    for i, color in enumerate(flame_colors):
        flame_height = 20 - i * 5
        flame_width = width // 4 - i * 3
        
        flame_points = [
            (center_x - flame_width // 2, flame_y),
            (center_x - flame_width // 4, flame_y + flame_height // 2),
            (center_x, flame_y + flame_height),
            (center_x + flame_width // 4, flame_y + flame_height // 2),
            (center_x + flame_width // 2, flame_y)
        ]
        draw.polygon(flame_points, fill=color)
    
    star_color = (255, 255, 100, 150)
    star_size = 3
    
    star_x = center_x - width // 3
    star_y = flame_y + 15
    self._draw_cute_star(draw, star_x, star_y, star_size, star_color)
    
    star_x = center_x + width // 3
    star_y = flame_y + 15
    self._draw_cute_star(draw, star_x, star_y, star_size, star_color)

# 將函數添加到 RichMenuImageGenerator 類
RichMenuImageGenerator._draw_shuttle_face = _draw_shuttle_face
RichMenuImageGenerator._draw_shuttle_flames = _draw_shuttle_flames
RichMenuImageGenerator._draw_mini_face = _draw_mini_face
RichMenuImageGenerator._draw_mini_flames = _draw_mini_flames

def _draw_moon_detailed(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int], moon_style: str = "classic"):
    """
    繪製塗鴉風格的月球 - 支持多種樣式
    """
    if moon_style == "classic":
        self._draw_classic_moon(draw, center_x, center_y, radius, base_color)
    elif moon_style == "sleepy":
        self._draw_sleepy_moon(draw, center_x, center_y, radius, base_color)
    elif moon_style == "crescent":
        self._draw_crescent_moon(draw, center_x, center_y, radius, base_color)
    elif moon_style == "kawaii":
        self._draw_kawaii_moon(draw, center_x, center_y, radius, base_color)
    elif moon_style == "mystical":
        self._draw_mystical_moon(draw, center_x, center_y, radius, base_color)
    else:
        self._draw_classic_moon(draw, center_x, center_y, radius, base_color)
    
def _draw_classic_moon(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
    """
    經典月亮樣式 - 去除背後圓圈線條
    """
    # 月球主體 - 淡灰色
    moon_color = (220, 220, 220)
    draw.ellipse([
        (center_x - radius, center_y - radius),
        (center_x + radius, center_y + radius)
    ], fill=moon_color)
    
    # 手繪風格的隕石坑
    crater_color = (180, 180, 180)
    
    # 大隕石坑
    large_craters = [
        (center_x - radius * 0.3, center_y - radius * 0.2, 15),
        (center_x + radius * 0.2, center_y + radius * 0.3, 12),
        (center_x - radius * 0.1, center_y + radius * 0.1, 10)
    ]
    
    for crater_x, crater_y, crater_size in large_craters:
        if (crater_x - center_x)**2 + (crater_y - center_y)**2 <= (radius * 0.8)**2:
            draw.ellipse([
                (crater_x - crater_size, crater_y - crater_size),
                (crater_x + crater_size, crater_y + crater_size)
            ], fill=crater_color)
    
    # 小隕石坑
    for _ in range(8):
        crater_x = center_x + random.randint(-radius//2, radius//2)
        crater_y = center_y + random.randint(-radius//2, radius//2)
        crater_size = random.randint(3, 8)
        
        if (crater_x - center_x)**2 + (crater_y - center_y)**2 <= (radius * 0.8)**2:
            draw.ellipse([
                (crater_x - crater_size, crater_y - crater_size),
                (crater_x + crater_size, crater_y + crater_size)
            ], fill=crater_color)
    
    # 月亮表情
    self._draw_moon_face(draw, center_x, center_y, radius)
    
def _draw_sleepy_moon(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
    """
    睡覺月亮樣式 - 經典睡眠表情
    """
    # 月球主體
    moon_color = (230, 230, 230)
    draw.ellipse([
        (center_x - radius, center_y - radius),
        (center_x + radius, center_y + radius)
    ], fill=moon_color)
    
    # 簡單隕石坑
    crater_color = (190, 190, 190)
    for _ in range(6):
        crater_x = center_x + random.randint(-radius//3, radius//3)
        crater_y = center_y + random.randint(-radius//3, radius//3)
        crater_size = random.randint(5, 12)
        
        draw.ellipse([
            (crater_x - crater_size, crater_y - crater_size),
            (crater_x + crater_size, crater_y + crater_size)
        ], fill=crater_color)
    
    # 睡覺表情
    self._draw_sleepy_moon_face(draw, center_x, center_y, radius)
    
    # ZZZ 效果
    self._draw_zzz_effect(draw, center_x, center_y, radius)
    
def _draw_crescent_moon(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
    """
    月牙樣式
    """
    # 月牙形狀
    moon_color = (240, 240, 240)
    
    # 主圓
    draw.ellipse([
        (center_x - radius, center_y - radius),
        (center_x + radius, center_y + radius)
    ], fill=moon_color)
    
    # 遮擋圓創造月牙效果
    mask_radius = int(radius * 0.8)
    mask_x = center_x + radius // 3
    draw.ellipse([
        (mask_x - mask_radius, center_y - mask_radius),
        (mask_x + mask_radius, center_y + mask_radius)
    ], fill=(47, 47, 79))  # 夜空色
    
    # 月牙上的隕石坑
    crater_color = (200, 200, 200)
    craters = [
        (center_x - radius * 0.4, center_y - radius * 0.3, 8),
        (center_x - radius * 0.2, center_y + radius * 0.2, 6),
        (center_x - radius * 0.6, center_y, 5)
    ]
    
    for crater_x, crater_y, crater_size in craters:
        # 檢查是否在月牙可見區域
        if (crater_x - center_x)**2 + (crater_y - center_y)**2 <= radius**2:
            if (crater_x - mask_x)**2 + (crater_y - center_y)**2 > mask_radius**2:
                draw.ellipse([
                    (crater_x - crater_size, crater_y - crater_size),
                    (crater_x + crater_size, crater_y + crater_size)
                ], fill=crater_color)
    
    # 月牙表情
    self._draw_crescent_moon_face(draw, center_x, center_y, radius)
    
def _draw_kawaii_moon(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
    """
    可愛日系月亮樣式
    """
    # 月球主體（稍微扁平）
    moon_color = (250, 250, 250)
    draw.ellipse([
        (center_x - radius, center_y - int(radius * 0.9)),
        (center_x + radius, center_y + int(radius * 0.9))
    ], fill=moon_color)
    
    # 心形隕石坑
    heart_crater_color = (220, 220, 220)
    heart_positions = [
        (center_x - radius * 0.3, center_y - radius * 0.2),
        (center_x + radius * 0.2, center_y + radius * 0.3)
    ]
    
    for heart_x, heart_y in heart_positions:
        self._draw_heart_crater(draw, heart_x, heart_y, 12, heart_crater_color)
    
    # 星星隕石坑
    star_crater_color = (210, 210, 210)
    for i in range(4):
        star_x = center_x + radius * 0.5 * math.cos(i * math.pi / 2)
        star_y = center_y + radius * 0.5 * math.sin(i * math.pi / 2)
        self._draw_star_crater(draw, star_x, star_y, 8, star_crater_color)
    
    # 可愛表情
    self._draw_kawaii_moon_face(draw, center_x, center_y, radius)
    
def _draw_mystical_moon(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
    """
    神秘月球樣式 - 魔法風格
    """
    # 主體（深色神秘色彩）
    draw.ellipse([
        (center_x - radius, center_y - radius),
        (center_x + radius, center_y + radius)
    ], fill=(100, 100, 150))
    
    # 隕石坑（神秘符號）
    crater_positions = [
        (center_x - radius//3, center_y - radius//3, radius//8),
        (center_x + radius//4, center_y - radius//4, radius//10),
        (center_x - radius//4, center_y + radius//3, radius//12),
        (center_x + radius//3, center_y + radius//4, radius//9)
    ]
    
    for crater_x, crater_y, crater_size in crater_positions:
        # 繪製星形符號
        self._draw_star_symbol(draw, crater_x, crater_y, crater_size, (80, 80, 120))
    
    # 神秘眼睛
    eye_size = radius // 5
    draw.ellipse([
        (center_x - radius//4 - eye_size, center_y - radius//6 - eye_size),
        (center_x - radius//4 + eye_size, center_y - radius//6 + eye_size)
    ], fill=(200, 200, 255))
    draw.ellipse([
        (center_x + radius//4 - eye_size, center_y - radius//6 - eye_size),
        (center_x + radius//4 + eye_size, center_y - radius//6 + eye_size)
    ], fill=(200, 200, 255))
    
    # 瞳孔
    pupil_size = eye_size // 2
    draw.ellipse([
        (center_x - radius//4 - pupil_size, center_y - radius//6 - pupil_size),
        (center_x - radius//4 + pupil_size, center_y - radius//6 + pupil_size)
    ], fill=(50, 50, 100))
    draw.ellipse([
        (center_x + radius//4 - pupil_size, center_y - radius//6 - pupil_size),
        (center_x + radius//4 + pupil_size, center_y - radius//6 + pupil_size)
    ], fill=(50, 50, 100))
    
    # 神秘微笑
    mouth_width = radius // 3
    draw.arc([
        (center_x - mouth_width, center_y + radius//6),
        (center_x + mouth_width, center_y + radius//6 + mouth_width)
    ], 0, 180, fill=(150, 150, 200), width=4)
    
    # 周圍魔法星星
    for i in range(6):
        angle = i * 60
        angle_rad = math.radians(angle)
        star_x = center_x + (radius + 30) * math.cos(angle_rad)
        star_y = center_y + (radius + 30) * math.sin(angle_rad)
        self._draw_star_symbol(draw, star_x, star_y, 8, (200, 200, 255))
    
    def _draw_star_symbol(self, draw: ImageDraw.Draw, center_x: int, center_y: int, size: int, color: Tuple[int, int, int]):
        """繪製星形符號"""
        points = []
        for i in range(10):
            angle = i * 36
            angle_rad = math.radians(angle)
            if i % 2 == 0:
                r = size
            else:
                r = size // 2
            x = center_x + r * math.cos(angle_rad)
            y = center_y + r * math.sin(angle_rad)
            points.append((x, y))
        
        draw.polygon(points, fill=color)

    def _draw_sun_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """繪製太陽表情 - 溫暖友善"""
        # 眼睛
        eye_size = radius // 6
        draw.ellipse([
            (center_x - radius//3 - eye_size, center_y - radius//4 - eye_size),
            (center_x - radius//3 + eye_size, center_y - radius//4 + eye_size)
        ], fill=(0, 0, 0))
        draw.ellipse([
            (center_x + radius//3 - eye_size, center_y - radius//4 - eye_size),
            (center_x + radius//3 + eye_size, center_y - radius//4 + eye_size)
        ], fill=(0, 0, 0))
        
        # 微笑
        mouth_width = radius // 2
        draw.arc([
            (center_x - mouth_width, center_y),
            (center_x + mouth_width, center_y + mouth_width)
        ], 0, 180, fill=(255, 100, 100), width=5)

    def _draw_simple_sun_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """繪製簡單太陽表情"""
        # 簡單的點眼睛
        eye_size = radius // 8
        draw.ellipse([
            (center_x - radius//4 - eye_size, center_y - radius//5 - eye_size),
            (center_x - radius//4 + eye_size, center_y - radius//5 + eye_size)
        ], fill=(0, 0, 0))
        draw.ellipse([
            (center_x + radius//4 - eye_size, center_y - radius//5 - eye_size),
            (center_x + radius//4 + eye_size, center_y - radius//5 + eye_size)
        ], fill=(0, 0, 0))
        
        # 簡單微笑
        mouth_width = radius // 3
        draw.arc([
            (center_x - mouth_width, center_y + radius//6),
            (center_x + mouth_width, center_y + radius//6 + mouth_width//2)
        ], 0, 180, fill=(255, 150, 0), width=4)

    def _draw_modern_sun_face(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """繪製現代太陽表情 - 幾何風格"""
        # 三角形眼睛
        eye_size = radius // 6
        # 左眼
        draw.polygon([
            (center_x - radius//3, center_y - radius//4 - eye_size),
            (center_x - radius//3 - eye_size, center_y - radius//4 + eye_size),
            (center_x - radius//3 + eye_size, center_y - radius//4 + eye_size)
        ], fill=(0, 0, 0))
        # 右眼
        draw.polygon([
            (center_x + radius//3, center_y - radius//4 - eye_size),
            (center_x + radius//3 - eye_size, center_y - radius//4 + eye_size),
            (center_x + radius//3 + eye_size, center_y - radius//4 + eye_size)
        ], fill=(0, 0, 0))
        
        # 幾何微笑
        mouth_width = radius // 3
        draw.polygon([
            (center_x - mouth_width, center_y + radius//6),
            (center_x, center_y + radius//3),
            (center_x + mouth_width, center_y + radius//6)
        ], fill=(255, 100, 0))