"""
圖片資源型 Rich Menu 生成器
使用用戶提供的圖片文件來創建 Rich Menu，而不是程式生成的圖案
"""
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional
import json

from app.config.linebot_config import LineBotConfig

class ImageBasedRichMenuGenerator:
    """基於圖片資源的 Rich Menu 生成器"""
    
    def __init__(self, image_base_path: str = "user_images"):
        """
        初始化圖片資源生成器
        
        Args:
            image_base_path: 圖片資源基礎路徑
        """
        self.width = LineBotConfig.RICH_MENU_WIDTH
        self.height = LineBotConfig.RICH_MENU_HEIGHT
        self.image_base_path = image_base_path
        
        # 確保圖片目錄存在
        os.makedirs(self.image_base_path, exist_ok=True)
        
        # 按鈕圖片映射配置
        self.button_image_mapping = self._load_button_image_mapping()
    
    def _load_button_image_mapping(self) -> Dict:
        """
        載入按鈕圖片映射配置
        如果配置文件不存在，則創建預設配置
        """
        config_path = os.path.join(self.image_base_path, "button_image_config.json")
        
        # 預設配置
        default_config = {
            "button_images": {
                "weekly_divination": {
                    "image_file": "crystal_ball.png",
                    "text": "本週占卜",
                    "fallback_color": (200, 150, 200),
                    "description": "水晶球圖片 - 用於本週占卜功能"
                },
                "yearly_fortune": {
                    "image_file": "rocket.png", 
                    "text": "流年運勢",
                    "fallback_color": (255, 140, 60),
                    "description": "火箭圖片 - 用於流年運勢功能"
                },
                "monthly_fortune": {
                    "image_file": "saturn.png",
                    "text": "流月運勢", 
                    "fallback_color": (255, 215, 100),
                    "description": "土星圖片 - 用於流月運勢功能"
                },
                "daily_fortune": {
                    "image_file": "ufo.png",
                    "text": "流日運勢",
                    "fallback_color": (180, 180, 180),
                    "description": "UFO圖片 - 用於流日運勢功能"
                },
                "chart_binding": {
                    "image_file": "earth.png",
                    "text": "命盤綁定",
                    "fallback_color": (150, 200, 255),
                    "description": "地球圖片 - 用於命盤綁定功能"
                },
                "member_info": {
                    "image_file": "moon.png",
                    "text": "會員資訊",
                    "fallback_color": (200, 200, 200),
                    "description": "月球圖片 - 用於會員資訊功能"
                },
                "scheduled_divination": {
                    "image_file": "clock.png",
                    "text": "指定時間",
                    "fallback_color": (255, 100, 255),
                    "description": "時鐘圖片 - 用於指定時間占卜功能（管理員專用）"
                }
            },
            "image_settings": {
                "button_size": 200,
                "image_resize": True,
                "maintain_aspect_ratio": True,
                "add_background_circle": True,
                "background_opacity": 0.3,
                "add_text_shadow": True,
                "text_position": "bottom"
            }
        }
        
        # 如果配置文件不存在，創建它
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"✅ 已創建按鈕圖片配置文件：{config_path}")
            self._create_readme_file()
        
        # 載入配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 載入配置文件失敗：{e}")
            return default_config
    
    def _create_readme_file(self):
        """創建使用說明文件"""
        readme_path = os.path.join(self.image_base_path, "README.md")
        
        readme_content = """# 按鈕圖片資源說明

## 目錄結構
```
user_images/
├── button_image_config.json  # 按鈕圖片配置文件
├── crystal_ball.png         # 水晶球圖片（本週占卜）
├── rocket.png              # 火箭圖片（流年運勢）
├── saturn.png              # 土星圖片（流月運勢）
├── ufo.png                 # UFO圖片（流日運勢）
├── earth.png               # 地球圖片（命盤綁定）
├── moon.png                # 月球圖片（會員資訊）
├── clock.png               # 時鐘圖片（指定時間占卜）
└── README.md               # 本說明文件
```

## 圖片要求

### 尺寸建議
- **建議尺寸**：200x200 到 400x400 像素
- **格式**：PNG（支援透明背景）或 JPG
- **背景**：建議使用透明背景的 PNG 格式

### 圖片風格
- 清晰、簡潔的圖案
- 避免過於複雜的細節
- 顏色鮮明，在深色背景上清晰可見

## 配置文件說明

### button_image_config.json
```json
{
  "button_images": {
    "按鈕名稱": {
      "image_file": "圖片文件名",
      "text": "按鈕顯示文字",
      "fallback_color": [R, G, B],
      "description": "按鈕描述"
    }
  },
  "image_settings": {
    "button_size": 200,              // 按鈕大小
    "image_resize": true,            // 是否調整圖片大小
    "maintain_aspect_ratio": true,   // 是否保持長寬比
    "add_background_circle": true,   // 是否添加背景圓圈
    "background_opacity": 0.3,       // 背景透明度
    "add_text_shadow": true,         // 是否添加文字陰影
    "text_position": "bottom"        // 文字位置
  }
}
```

## 使用方法

1. **放置圖片**：將您的圖片文件放在 `user_images/` 目錄中
2. **更新配置**：修改 `button_image_config.json` 中的圖片文件名
3. **重新生成**：運行系統重新生成 Rich Menu

## 注意事項

- 如果指定的圖片文件不存在，系統會使用 fallback_color 生成純色按鈕
- 建議使用透明背景的 PNG 格式以獲得最佳效果
- 圖片會自動調整大小以適應按鈕尺寸
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ 已創建使用說明文件：{readme_path}")
    
    def create_starry_background(self) -> Image.Image:
        """創建星空背景（保留星星，但星雲效果更輕微）"""
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
        
        # 保留星星效果
        self._add_stars(draw)
        
        # 添加非常輕微的星雲效果
        self._add_subtle_nebula_effects(image)
        
        return image
    
    def _add_stars(self, draw: ImageDraw.Draw):
        """添加星星效果"""
        import random
        
        # 添加小星星
        for _ in range(150):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            
            color = (brightness, brightness, brightness, 255)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        # 添加大星星
        for _ in range(30):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 4)
            brightness = random.randint(200, 255)
            
            color = (brightness, brightness, brightness, 255)
            # 繪製十字星
            draw.line([(x-size*2, y), (x+size*2, y)], fill=color, width=2)
            draw.line([(x, y-size*2), (x, y+size*2)], fill=color, width=2)
    
    def _add_subtle_nebula_effects(self, image: Image.Image):
        """添加非常輕微的星雲效果"""
        import random
        
        # 創建星雲層
        nebula_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        nebula_draw = ImageDraw.Draw(nebula_layer)
        
        # 添加極其輕微的彩色星雲
        colors = [
            (80, 40, 120, 8),    # 非常淡的紫色
            (40, 80, 120, 6),    # 非常淡的藍色
            (120, 40, 80, 5),    # 非常淡的粉色
        ]
        
        for color in colors:
            for _ in range(2):  # 減少數量
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                size = random.randint(300, 500)  # 更大的範圍，更柔和
                
                nebula_draw.ellipse([
                    x - size, y - size,
                    x + size, y + size
                ], fill=color)
        
        # 合併星雲效果
        image.alpha_composite(nebula_layer)
    
    def create_image_button(self, button_name: str, button_config: Dict) -> Image.Image:
        """
        創建基於圖片的按鈕
        
        Args:
            button_name: 按鈕名稱
            button_config: 按鈕配置
            
        Returns:
            Image.Image: 按鈕圖片
        """
        # 獲取圖片映射配置
        image_config = self.button_image_mapping.get("button_images", {}).get(button_name, {})
        settings = self.button_image_mapping.get("image_settings", {})
        
        # 按鈕基本參數
        button_size = settings.get("button_size", 200)
        button_img = Image.new('RGBA', (button_size * 2, button_size * 2), (0, 0, 0, 0))
        
        # 嘗試載入用戶提供的圖片
        image_file = image_config.get("image_file", "")
        image_path = os.path.join(self.image_base_path, image_file)
        
        if os.path.exists(image_path):
            try:
                # 載入並處理用戶圖片
                user_image = Image.open(image_path)
                processed_button = self._process_user_image(
                    user_image, button_img, button_name, button_config, settings
                )
                return processed_button
            except Exception as e:
                print(f"⚠️ 無法載入圖片 {image_path}: {e}")
        
        # 如果圖片不存在，使用備用方案
        return self._create_fallback_button(button_img, button_name, button_config, image_config)
    
    def _process_user_image(self, user_image: Image.Image, button_img: Image.Image, 
                           button_name: str, button_config: Dict, settings: Dict) -> Image.Image:
        """處理用戶提供的圖片"""
        draw = ImageDraw.Draw(button_img)
        
        # 按鈕尺寸
        button_size = settings.get("button_size", 200)
        center_x = button_img.width // 2
        center_y = button_img.height // 2
        
        # 調整圖片大小
        if settings.get("image_resize", True):
            if settings.get("maintain_aspect_ratio", True):
                # 保持長寬比
                user_image.thumbnail((button_size, button_size), Image.Resampling.LANCZOS)
            else:
                # 強制調整大小
                user_image = user_image.resize((button_size, button_size), Image.Resampling.LANCZOS)
        
        # 添加背景圓圈
        if settings.get("add_background_circle", True):
            bg_color = button_config.get("color", (100, 100, 100))
            opacity = int(255 * settings.get("background_opacity", 0.3))
            bg_color_with_alpha = (*bg_color, opacity)
            
            draw.ellipse([
                center_x - button_size//2 - 10,
                center_y - button_size//2 - 10,
                center_x + button_size//2 + 10,
                center_y + button_size//2 + 10
            ], fill=bg_color_with_alpha)
        
        # 將用戶圖片貼到按鈕上
        paste_x = center_x - user_image.width // 2
        paste_y = center_y - user_image.height // 2
        
        if user_image.mode == 'RGBA':
            button_img.paste(user_image, (paste_x, paste_y), user_image)
        else:
            button_img.paste(user_image, (paste_x, paste_y))
        
        # 添加文字
        text = button_config.get("text", "")
        if text:
            self._add_button_text(draw, text, button_img.width, button_img.height, 
                                center_y, button_size, settings)
        
        return button_img
    
    def _create_fallback_button(self, button_img: Image.Image, button_name: str, 
                               button_config: Dict, image_config: Dict) -> Image.Image:
        """創建備用按鈕（當圖片不存在時）"""
        draw = ImageDraw.Draw(button_img)
        
        center_x = button_img.width // 2
        center_y = button_img.height // 2
        button_size = 200
        
        # 使用備用顏色
        fallback_color = image_config.get("fallback_color", button_config.get("color", (100, 100, 100)))
        
        # 繪製圓形按鈕
        draw.ellipse([
            center_x - button_size//2,
            center_y - button_size//2,
            center_x + button_size//2,
            center_y + button_size//2
        ], fill=fallback_color)
        
        # 添加文字
        text = button_config.get("text", "")
        if text:
            settings = self.button_image_mapping.get("image_settings", {})
            self._add_button_text(draw, text, button_img.width, button_img.height, 
                                center_y, button_size, settings)
        
        return button_img
    
    def _add_button_text(self, draw: ImageDraw.Draw, text: str, img_width: int, img_height: int, 
                        center_y: int, button_size: int, settings: Dict):
        """添加按鈕文字"""
        # 字體設定
        font_size = 48
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                font = ImageFont.load_default()
        
        # 計算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (img_width - text_width) // 2
        
        # 根據設定決定文字位置
        text_position = settings.get("text_position", "bottom")
        if text_position == "bottom":
            text_y = center_y + button_size//2 + 20
        elif text_position == "top":
            text_y = center_y - button_size//2 - text_height - 20
        else:  # center
            text_y = center_y - text_height // 2
        
        # 添加文字陰影
        if settings.get("add_text_shadow", True):
            shadow_offsets = [(3, 3), (2, 2), (1, 1)]
            shadow_colors = [(0, 0, 0, 200), (50, 50, 50, 150), (100, 100, 100, 100)]
            
            for (dx, dy), shadow_color in zip(shadow_offsets, shadow_colors):
                draw.text((text_x + dx, text_y + dy), text, font=font, fill=shadow_color)
        
        # 繪製主要文字
        text_color = (255, 255, 255, 255)
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    def generate_rich_menu_image(self, button_configs: List[Dict], 
                                output_path: str = "rich_menu_images/image_based_menu.png") -> str:
        """
        生成基於圖片的 Rich Menu
        
        Args:
            button_configs: 按鈕配置列表
            output_path: 輸出圖片路徑
            
        Returns:
            str: 生成的圖片路徑
        """
        # 創建星空背景
        background = self.create_starry_background()
        
        # 處理每個按鈕
        for button_config in button_configs:
            button_name = button_config.get("name", "")
            
            # 創建按鈕圖片
            button_img = self.create_image_button(button_name, button_config)
            
            # 計算按鈕位置
            x = button_config.get("x", 0)
            y = button_config.get("y", 0)
            
            # 將按鈕貼到背景上
            paste_x = x - button_img.width // 2
            paste_y = y - button_img.height // 2
            
            # 確保位置在有效範圍內
            paste_x = max(0, min(paste_x, self.width - button_img.width))
            paste_y = max(0, min(paste_y, self.height - button_img.height))
            
            background.paste(button_img, (paste_x, paste_y), button_img)
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存圖片
        background.save(output_path, "PNG")
        
        return output_path
    
    def get_button_areas(self, button_configs: List[Dict]) -> List[Dict]:
        """
        獲取按鈕區域配置
        
        Args:
            button_configs: 按鈕配置列表
            
        Returns:
            List[Dict]: 按鈕區域配置
        """
        areas = []
        
        for button_config in button_configs:
            # 按鈕尺寸
            size = button_config.get("size", 200)
            button_width = int(size * 2.0)
            button_height = int(size * 2.0)
            
            # 按鈕區域
            area = {
                "bounds": {
                    "x": button_config.get("x", 0) - button_width // 2,
                    "y": button_config.get("y", 0) - button_height // 2,
                    "width": button_width,
                    "height": button_height
                },
                "action": {
                    "type": "message",
                    "text": button_config.get("action_text", button_config.get("text", ""))
                }
            }
            areas.append(area)
        
        return areas


def generate_image_based_rich_menu(user_level: str = "member", 
                                  output_path: str = None) -> Tuple[str, List[Dict]]:
    """
    生成基於圖片的 Rich Menu
    
    Args:
        user_level: 用戶等級 ("member" 或 "admin")
        output_path: 輸出路徑
        
    Returns:
        Tuple[str, List[Dict]]: (圖片路徑, 按鈕區域配置)
    """
    generator = ImageBasedRichMenuGenerator()
    
    # 根據用戶等級選擇按鈕配置
    if user_level == "admin":
        button_configs = LineBotConfig.ADMIN_RICH_MENU_BUTTONS
        default_output = "rich_menu_images/image_based_admin_menu.png"
    else:
        button_configs = LineBotConfig.MEMBER_RICH_MENU_BUTTONS
        default_output = "rich_menu_images/image_based_member_menu.png"
    
    output_path = output_path or default_output
    
    # 生成圖片
    image_path = generator.generate_rich_menu_image(button_configs, output_path)
    
    # 獲取按鈕區域
    button_areas = generator.get_button_areas(button_configs)
    
    return image_path, button_areas 