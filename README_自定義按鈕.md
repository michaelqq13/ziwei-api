# 🎨 自定義按鈕生成器

> 將您的圖片轉換為專業的 LINE Rich Menu 按鈕

## 📋 功能概述

這個工具可以讓您：
- ✅ 使用自己的圖片創建 LINE Rich Menu 按鈕
- ✅ 自動調整圖片大小並保持比例
- ✅ 添加專業的視覺效果（星空背景、發光、邊框）
- ✅ 批量處理多張圖片
- ✅ 生成完整的 Rich Menu 圖片
- ✅ 與現有系統無縫整合

## 🚀 快速開始

### 1. 準備圖片
```bash
# 創建圖片資料夾
mkdir user_images

# 將您的圖片放入資料夾
# 支援格式: PNG, JPG, JPEG, GIF
# 建議大小: 200x200 像素以上
```

### 2. 執行示範
```bash
# 運行示範腳本
python demo_custom_buttons.py

# 或者直接創建示範圖片
python -c "from demo_custom_buttons import create_sample_images; create_sample_images()"
```

### 3. 查看結果
- 生成的按鈕: `demo_output/` 資料夾
- 完整 Rich Menu: `rich_menu_images/` 資料夾
- 預覽頁面: `custom_button_preview.html`

## 💻 程式使用方法

### 基本使用
```python
from app.utils.custom_button_generator import CustomButtonGenerator

# 創建生成器
generator = CustomButtonGenerator()

# 配置按鈕
configs = [
    {
        'image_path': 'user_images/my_icon.png',
        'button_text': '我的功能',
        'text_color': (255, 255, 255),
        'add_background': True,
        'add_shadow': True
    }
]

# 生成按鈕
button_paths = generator.create_button_set_from_images(configs)

# 整合到 Rich Menu
button_configs = [
    {"action": {"type": "message", "text": "我的功能被點擊"}}
]

menu_path, button_areas = generator.integrate_with_rich_menu(
    button_paths, button_configs, "my_custom_menu"
)
```

### 進階配置
```python
# 進階配置選項
advanced_config = {
    'image_path': 'user_images/special_icon.png',
    'button_text': '特殊功能',
    'button_size': (250, 250),          # 自定義尺寸
    'text_color': (255, 215, 0),        # 金色文字
    'add_background': True,              # 星空背景
    'add_border': True,                  # 邊框效果
    'add_shadow': True                   # 發光陰影
}

# 簡約風格
minimal_config = {
    'image_path': 'user_images/simple_icon.png',
    'button_text': '簡約風格',
    'add_background': False,             # 無背景
    'add_border': False,                 # 無邊框
    'add_shadow': False                  # 無特效
}
```

## 🎛️ 配置選項

### 按鈕配置參數
| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `image_path` | str | 必填 | 圖片檔案路徑 |
| `button_text` | str | 必填 | 按鈕文字 |
| `button_size` | tuple | (200, 200) | 按鈕尺寸 |
| `text_color` | tuple | (255, 255, 255) | 文字顏色 RGB |
| `add_background` | bool | True | 是否添加星空背景 |
| `add_border` | bool | True | 是否添加邊框 |
| `add_shadow` | bool | True | 是否添加發光效果 |

### 支援的圖片格式
- PNG (推薦，支援透明度)
- JPG / JPEG
- GIF
- 其他 PIL 支援的格式

### 按鈕佈局
- **1-3 個按鈕**: 水平排列
- **4-6 個按鈕**: 2x3 網格
- **7-9 個按鈕**: 3x3 網格

## 🌟 功能特色

### 🎨 智能圖片處理
- 自動調整圖片大小，保持最佳比例
- 增強對比度和亮度
- 支援透明度處理
- 確保在 Rich Menu 中完美顯示

### ✨ 專業特效
- **星空背景**: 漸變星空效果
- **發光效果**: 多層發光圓圈
- **邊框裝飾**: 雙層邊框設計
- **文字陰影**: 提升文字可讀性

### 🎯 靈活配置
- 自定義按鈕尺寸
- 多種文字顏色選擇
- 特效開關控制
- 批量處理支援

### 📱 完美適配
- 符合 LINE Rich Menu 規格
- 自動計算按鈕位置
- 生成完整的按鈕區域配置
- 可直接上傳使用

## 📁 檔案結構

```
ziwei-api/
├── app/utils/
│   └── custom_button_generator.py     # 主要生成器
├── demo_custom_buttons.py             # 示範腳本
├── custom_button_preview.html         # 預覽頁面
├── user_images/                       # 用戶圖片資料夾
│   ├── heart.png                      # 示範圖片
│   ├── star.png
│   └── diamond.png
├── demo_output/                       # 生成的按鈕
│   ├── custom_button_1.png
│   ├── custom_button_2.png
│   └── custom_button_3.png
└── rich_menu_images/                  # Rich Menu 圖片
    └── custom_user_custom_menu.png    # 完整選單
```

## 🔧 進階使用

### 與現有系統整合
```python
# 整合到分頁選單系統
from app.utils.tabbed_rich_menu_generator import TabbedRichMenuGenerator
from app.utils.custom_button_generator import CustomButtonGenerator

# 創建自定義按鈕
custom_generator = CustomButtonGenerator()
button_paths = custom_generator.create_button_set_from_images(configs)

# 整合到分頁系統
tabbed_generator = TabbedRichMenuGenerator()
# ... 進一步整合邏輯
```

### 批量處理
```python
# 批量處理多種風格
batch_configs = [
    {
        'image_path': f'user_images/icon_{i}.png',
        'button_text': f'功能{i}',
        'text_color': (255, 255, 255),
        'button_size': (200, 200)
    }
    for i in range(1, 7)  # 6個按鈕
]

button_paths = generator.create_button_set_from_images(
    batch_configs, 
    output_dir="batch_output"
)
```

### 自定義樣式
```python
# 不同主題的按鈕
themes = {
    'gold': {
        'text_color': (255, 215, 0),
        'add_background': True,
        'add_border': True,
        'add_shadow': True
    },
    'minimal': {
        'text_color': (255, 255, 255),
        'add_background': False,
        'add_border': False,
        'add_shadow': False
    },
    'neon': {
        'text_color': (0, 255, 255),
        'add_background': True,
        'add_border': True,
        'add_shadow': True
    }
}
```

## 🛠️ 故障排除

### 常見問題

**Q: 圖片載入失敗怎麼辦？**
A: 系統會自動生成備用按鈕（問號圖示），檢查圖片路徑和格式是否正確。

**Q: 生成的按鈕太小或太大？**
A: 調整 `button_size` 參數，建議保持在 (150, 150) 到 (300, 300) 之間。

**Q: 文字顯示不清楚？**
A: 嘗試調整 `text_color` 或啟用 `add_shadow` 來增加對比度。

**Q: 如何關閉特效？**
A: 設定 `add_background=False`, `add_border=False`, `add_shadow=False`。

### 效能優化

```python
# 大批量處理時的優化
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

def process_single_button(config):
    generator = CustomButtonGenerator()
    return generator.create_button_from_image(**config)

# 並行處理
with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    results = list(executor.map(process_single_button, configs))
```

## 📊 範例展示

### 生成結果
- **原始圖片**: 心形、星形、菱形 (1KB 以下)
- **處理後按鈕**: 加入特效後 (5-6KB)
- **完整 Rich Menu**: 整合所有按鈕 (92KB)

### 效果對比
| 項目 | 原始圖片 | 處理後按鈕 | 提升效果 |
|------|----------|------------|----------|
| 視覺效果 | 簡單圖形 | 專業按鈕 | ⭐⭐⭐⭐⭐ |
| 檔案大小 | < 1KB | 5-6KB | 適中 |
| 使用便利性 | 需手動處理 | 自動化 | ⭐⭐⭐⭐⭐ |

## 🎉 總結

這個自定義按鈕生成器讓您可以：
1. **輕鬆使用**: 只需提供圖片和簡單配置
2. **專業效果**: 自動添加視覺特效
3. **批量處理**: 一次處理多張圖片
4. **完美整合**: 直接生成 Rich Menu
5. **高度自定義**: 豐富的配置選項

現在您可以完全按照自己的需求創建個性化的 LINE Rich Menu 按鈕了！

## 🔗 相關檔案
- [自定義按鈕生成器](app/utils/custom_button_generator.py)
- [示範腳本](demo_custom_buttons.py)
- [預覽頁面](custom_button_preview.html)
- [分頁選單系統](app/utils/tabbed_rich_menu_generator.py) 