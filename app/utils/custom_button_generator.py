from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
from typing import Dict, List, Tuple, Optional
import math

class CustomButtonGenerator:
    """
    生成器，可以將用戶提供的圖片轉換為按鈕
    """
    
    def __init__(self):
        self.button_size = (200, 200)
        self.font_size = 24
        
    def create_button_from_image(self, 
                               image_path: str, 
                               button_text: str,
                               button_size: Tuple[int, int] = (200, 200),
                               text_color: Tuple[int, int, int] = (255, 255, 255),
                               add_background: bool = True,
                               add_border: bool = True,
                               add_shadow: bool = True) -> Image.Image:
        """
        將用戶提供的圖片轉換為按鈕
        
        Args:
            image_path: 圖片檔案路徑
            button_text: 按鈕文字
            button_size: 按鈕尺寸
            text_color: 文字顏色
            add_background: 是否添加背景
            add_border: 是否添加邊框
            add_shadow: 是否添加陰影
        """
        # 載入用戶圖片
        try:
            user_image = Image.open(image_path)
        except Exception as e:
            print(f"無法載入圖片 {image_path}: {e}")
            return self._create_fallback_button(button_text, button_size, text_color)
        
        # 創建按鈕畫布
        button = Image.new('RGBA', button_size, (0, 0, 0, 0))
        
        # 添加背景
        if add_background:
            self._add_starry_background(button)
        
        # 處理用戶圖片
        processed_image = self._process_user_image(user_image, button_size)
        
        # 將處理後的圖片貼到按鈕上
        if processed_image:
            # 計算居中位置
            img_x = (button_size[0] - processed_image.width) // 2
            img_y = (button_size[1] - processed_image.height) // 2 - 20  # 稍微向上偏移為文字留空間
            
            button.paste(processed_image, (img_x, img_y), processed_image if processed_image.mode == 'RGBA' else None)
        
        # 添加特效
        if add_shadow:
            button = self._add_glow_effect(button)
        
        if add_border:
            button = self._add_border(button)
        
        # 添加文字
        button = self._add_text(button, button_text, text_color)
        
        return button
    
    def _process_user_image(self, user_image: Image.Image, button_size: Tuple[int, int]) -> Optional[Image.Image]:
        """處理用戶圖片：調整大小、優化品質"""
        try:
            # 計算合適的圖片大小（留空間給文字）
            max_img_size = min(button_size[0] - 40, button_size[1] - 60)
            
            # 保持寬高比調整大小
            img_ratio = user_image.width / user_image.height
            if img_ratio > 1:  # 寬圖
                new_width = max_img_size
                new_height = int(max_img_size / img_ratio)
            else:  # 高圖或正方形
                new_height = max_img_size
                new_width = int(max_img_size * img_ratio)
            
            # 調整大小
            resized_image = user_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 轉換為RGBA以支援透明度
            if resized_image.mode != 'RGBA':
                resized_image = resized_image.convert('RGBA')
            
            # 增強對比度和亮度
            enhancer = ImageEnhance.Contrast(resized_image)
            resized_image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Brightness(resized_image)
            resized_image = enhancer.enhance(1.1)
            
            return resized_image
            
        except Exception as e:
            print(f"處理圖片時出錯: {e}")
            return None
    
    def _add_starry_background(self, button: Image.Image):
        """添加星空背景"""
        draw = ImageDraw.Draw(button)
        width, height = button.size
        
        # 漸變背景
        for y in range(height):
            progress = y / height
            r = int(20 + progress * 30)
            g = int(25 + progress * 35)
            b = int(60 + progress * 80)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 200))
        
        # 添加星星
        import random
        for _ in range(15):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            draw.ellipse([x-size, y-size, x+size, y+size], 
                        fill=(brightness, brightness, brightness, 180))
    
    def _add_glow_effect(self, button: Image.Image) -> Image.Image:
        """添加發光效果"""
        # 創建發光層
        glow = Image.new('RGBA', button.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        
        width, height = button.size
        center_x, center_y = width // 2, height // 2
        
        # 繪製多層發光圓圈
        for i in range(5):
            radius = 80 + i * 20
            alpha = 30 - i * 5
            glow_draw.ellipse([center_x - radius, center_y - radius, 
                              center_x + radius, center_y + radius], 
                             fill=(255, 255, 255, alpha))
        
        # 模糊發光效果
        glow = glow.filter(ImageFilter.GaussianBlur(radius=10))
        
        # 合併發光效果
        result = Image.alpha_composite(glow, button)
        return result
    
    def _add_border(self, button: Image.Image) -> Image.Image:
        """添加邊框"""
        draw = ImageDraw.Draw(button)
        width, height = button.size
        
        # 外層邊框
        draw.rectangle([0, 0, width-1, height-1], outline=(255, 255, 255, 100), width=2)
        # 內層邊框
        draw.rectangle([3, 3, width-4, height-4], outline=(200, 200, 255, 80), width=1)
        
        return button
    
    def _add_text(self, button: Image.Image, text: str, text_color: Tuple[int, int, int]) -> Image.Image:
        """添加文字"""
        draw = ImageDraw.Draw(button)
        width, height = button.size
        
        # 嘗試載入字體
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size)
            except:
                font = ImageFont.load_default()
        
        # 計算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = height - text_height - 20
        
        # 添加文字陰影
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
                 fill=(0, 0, 0, 150), font=font)
        
        # 添加主文字
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        return button
    
    def _create_fallback_button(self, text: str, size: Tuple[int, int], text_color: Tuple[int, int, int]) -> Image.Image:
        """創建備用按鈕（當圖片載入失敗時）"""
        button = Image.new('RGBA', size, (50, 50, 100, 200))
        self._add_starry_background(button)
        
        draw = ImageDraw.Draw(button)
        width, height = size
        
        # 繪製問號圖示
        center_x, center_y = width // 2, height // 2 - 20
        draw.ellipse([center_x - 40, center_y - 40, center_x + 40, center_y + 40], 
                    fill=(100, 100, 100, 200), outline=(200, 200, 200, 255), width=3)
        
        # 問號
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        draw.text((center_x - 12, center_y - 25), "?", fill=(255, 255, 255), font=font)
        
        # 添加文字
        button = self._add_text(button, text, text_color)
        
        return button
    
    def create_button_set_from_images(self, 
                                    image_configs: List[Dict],
                                    output_dir: str = "custom_buttons") -> List[str]:
        """
        批量創建按鈕
        
        Args:
            image_configs: 圖片配置列表，每個包含：
                - image_path: 圖片路徑
                - button_text: 按鈕文字
                - output_name: 輸出檔名
                - 其他可選參數
        """
        os.makedirs(output_dir, exist_ok=True)
        output_paths = []
        
        for i, config in enumerate(image_configs):
            try:
                button = self.create_button_from_image(
                    image_path=config.get('image_path'),
                    button_text=config.get('button_text', f'按鈕{i+1}'),
                    button_size=config.get('button_size', (200, 200)),
                    text_color=config.get('text_color', (255, 255, 255)),
                    add_background=config.get('add_background', True),
                    add_border=config.get('add_border', True),
                    add_shadow=config.get('add_shadow', True)
                )
                
                output_name = config.get('output_name', f'custom_button_{i+1}.png')
                output_path = os.path.join(output_dir, output_name)
                
                button.save(output_path)
                output_paths.append(output_path)
                print(f"✅ 成功創建按鈕: {output_path}")
                
            except Exception as e:
                print(f"❌ 創建按鈕失敗 (配置 {i+1}): {e}")
        
        return output_paths
    
    def integrate_with_rich_menu(self, 
                               button_images: List[str],
                               button_configs: List[Dict],
                               menu_type: str = "custom") -> Tuple[str, List[Dict]]:
        """
        將自定義按鈕整合到Rich Menu中
        
        Args:
            button_images: 按鈕圖片路徑列表
            button_configs: 按鈕配置列表（包含action等）
            menu_type: 選單類型
        """
        from .rich_menu_image_generator import RichMenuImageGenerator
        
        # 創建Rich Menu背景
        generator = RichMenuImageGenerator()
        background = generator.create_starry_background()
        
        # 計算按鈕位置
        positions = self._calculate_button_positions(len(button_images), background.size)
        
        # 將按鈕貼到背景上
        button_areas = []
        for i, (button_img_path, position, config) in enumerate(zip(button_images, positions, button_configs)):
            try:
                button_img = Image.open(button_img_path)
                
                # 貼上按鈕
                x, y = position
                background.paste(button_img, (x, y), button_img if button_img.mode == 'RGBA' else None)
                
                # 記錄按鈕區域
                button_areas.append({
                    "bounds": {
                        "x": x,
                        "y": y,
                        "width": button_img.width,
                        "height": button_img.height
                    },
                    "action": config.get('action', {"type": "message", "text": f"按鈕{i+1}"})
                })
                
            except Exception as e:
                print(f"整合按鈕失敗 {button_img_path}: {e}")
        
        # 儲存最終的Rich Menu圖片
        output_path = f"rich_menu_images/custom_{menu_type}_menu.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        background.save(output_path)
        
        return output_path, button_areas
    
    def _calculate_button_positions(self, num_buttons: int, menu_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """計算按鈕在Rich Menu中的位置"""
        width, height = menu_size
        positions = []
        
        if num_buttons <= 3:
            # 水平排列
            button_width = width // num_buttons
            y = (height - 200) // 2
            
            for i in range(num_buttons):
                x = i * button_width + (button_width - 200) // 2
                positions.append((x, y))
        
        elif num_buttons <= 6:
            # 2x3 網格
            rows = 2
            cols = 3
            button_width = width // cols
            button_height = height // rows
            
            for i in range(num_buttons):
                row = i // cols
                col = i % cols
                x = col * button_width + (button_width - 200) // 2
                y = row * button_height + (button_height - 200) // 2
                positions.append((x, y))
        
        else:
            # 3x3 網格（最多9個按鈕）
            rows = 3
            cols = 3
            button_width = width // cols
            button_height = height // rows
            
            for i in range(min(num_buttons, 9)):
                row = i // cols
                col = i % cols
                x = col * button_width + (button_width - 200) // 2
                y = row * button_height + (button_height - 200) // 2
                positions.append((x, y))
        
        return positions


def create_custom_button_example():
    """示範如何使用自定義按鈕生成器"""
    generator = CustomButtonGenerator()
    
    # 示範配置
    example_configs = [
        {
            'image_path': 'user_images/my_icon1.png',  # 用戶提供的圖片
            'button_text': '我的功能',
            'output_name': 'my_custom_button1.png',
            'text_color': (255, 255, 255)
        },
        {
            'image_path': 'user_images/my_icon2.jpg',
            'button_text': '特殊功能',
            'output_name': 'my_custom_button2.png',
            'text_color': (255, 200, 100)
        }
    ]
    
    # 創建按鈕
    button_paths = generator.create_button_set_from_images(example_configs)
    
    # 整合到Rich Menu
    button_configs = [
        {"action": {"type": "message", "text": "執行我的功能"}},
        {"action": {"type": "message", "text": "執行特殊功能"}}
    ]
    
    menu_path, button_areas = generator.integrate_with_rich_menu(
        button_paths, button_configs, "my_custom_menu"
    )
    
    print(f"✅ 自定義Rich Menu已創建: {menu_path}")
    return menu_path, button_areas 