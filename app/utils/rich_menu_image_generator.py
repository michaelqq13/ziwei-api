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
        創建星球按鈕
        """
        size = button_config["size"]
        color = button_config["color"]
        planet_name = button_config["planet"]
        button_text = button_config["text"]
        
        # 創建按鈕圖片
        button_img = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(button_img)
        
        # 解析顏色
        hex_color = color.lstrip('#')
        rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 繪製星球（帶有漸變效果）
        center = size
        self._draw_planet_with_gradient(draw, center, center, size // 2, rgb_color)
        
        # 添加星球環帶效果（部分星球）
        if planet_name in ["土星"]:
            self._draw_planet_rings(draw, center, center, size // 2, rgb_color)
        
        # 添加文字標籤
        self._add_button_text(draw, button_text, size * 2, size * 2, rgb_color)
        
        # 返回按鈕位置
        position = (button_config["x"] - size, button_config["y"] - size)
        
        return button_img, position
    
    def _draw_planet_with_gradient(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int, base_color: Tuple[int, int, int]):
        """
        繪製帶有漸變效果的星球
        """
        # 繪製星球主體（多層圓形營造立體感）
        for r in range(radius, 0, -2):
            # 計算亮度變化
            brightness_factor = 0.6 + 0.4 * (radius - r) / radius
            
            adjusted_color = tuple(int(c * brightness_factor) for c in base_color)
            adjusted_color = tuple(min(255, max(0, c)) for c in adjusted_color)
            
            draw.ellipse([
                (center_x - r, center_y - r),
                (center_x + r, center_y + r)
            ], fill=adjusted_color + (255,))
        
        # 添加高光效果
        highlight_radius = radius // 3
        highlight_x = center_x - radius // 3
        highlight_y = center_y - radius // 3
        
        highlight_color = tuple(min(255, c + 80) for c in base_color)
        draw.ellipse([
            (highlight_x - highlight_radius, highlight_y - highlight_radius),
            (highlight_x + highlight_radius, highlight_y + highlight_radius)
        ], fill=highlight_color + (180,))
    
    def _draw_planet_rings(self, draw: ImageDraw.Draw, center_x: int, center_y: int, planet_radius: int, base_color: Tuple[int, int, int]):
        """
        繪製星球環帶
        """
        ring_color = tuple(c // 2 for c in base_color) + (120,)
        
        # 外環
        outer_radius = int(planet_radius * 1.8)
        inner_radius = int(planet_radius * 1.4)
        
        # 繪製環帶（橢圓形）
        for r in range(outer_radius, inner_radius, -1):
            ellipse_height = r // 3  # 扁平化效果
            draw.ellipse([
                (center_x - r, center_y - ellipse_height),
                (center_x + r, center_y + ellipse_height)
            ], outline=ring_color, width=1)
    
    def _add_button_text(self, draw: ImageDraw.Draw, text: str, img_width: int, img_height: int, text_color: Tuple[int, int, int]):
        """
        添加按鈕文字
        """
        try:
            # 嘗試載入字體
            font_size = 24
            font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # 計算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (img_width - text_width) // 2
        text_y = img_height - text_height - 10  # 在星球下方
        
        # 添加文字陰影
        shadow_color = (0, 0, 0, 180)
        draw.text((text_x + 2, text_y + 2), text, font=font, fill=shadow_color)
        
        # 添加主要文字
        bright_text_color = tuple(min(255, c + 100) for c in text_color) + (255,)
        draw.text((text_x, text_y), text, font=font, fill=bright_text_color)
    
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
            # 按鈕區域 (x, y, width, height)
            size = button["size"]
            area = {
                "bounds": {
                    "x": button["x"] - size,
                    "y": button["y"] - size,
                    "width": size * 2,
                    "height": size * 2
                },
                "action": {
                    "type": "message",
                    "text": button["action_text"]
                }
            }
            areas.append(area)
        
        return areas

# 全局實例
rich_menu_image_generator = RichMenuImageGenerator()

def generate_starry_rich_menu(output_path: str = "rich_menu_images/starry_sky_menu.png") -> Tuple[str, List[Dict]]:
    """
    生成星空主題 Rich Menu 的便捷函數
    
    Returns:
        Tuple[str, List[Dict]]: (圖片路徑, 按鈕區域配置)
    """
    image_path = rich_menu_image_generator.generate_rich_menu_image(output_path)
    button_areas = rich_menu_image_generator.get_button_areas()
    
    return image_path, button_areas

# 導出
__all__ = [
    "RichMenuImageGenerator",
    "rich_menu_image_generator", 
    "generate_starry_rich_menu"
] 