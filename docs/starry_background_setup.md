# 星空背景圖片設定指南

## 概要

本系統的 Flex Message 已全面支援背景圖片，並採用星空主題設計，提供一致且美觀的視覺體驗。

## 背景圖片支援

### LINE Flex Message 背景圖片規格

- **格式支援**: JPEG, PNG
- **最大尺寸**: 寬度最大 1040px，高度最大 3120px
- **檔案大小限制**: 10MB
- **URL 要求**: 必須是 HTTPS 格式
- **屬性支援**: 
  - `background_image`: 圖片 URL
  - `background_size`: cover, contain, auto
  - `background_position`: center, top, bottom 等

### 目前使用的星空圖片

#### 1. Carousel 控制面板
- **基本功能頁**: 深藍星空 (1040x600)
- **進階功能頁**: 紫色星雲 (1040x600)  
- **管理功能頁**: 金色星空 (1040x600)

#### 2. 占卜結果 Flex Message
- **免費用戶**: 深藍星空背景
- **付費會員**: 紫色星雲背景
- **管理員**: 金色星空背景

#### 3. 時間選擇器
- **時間選擇介面**: 紫色星雲背景 (1040x400)

## 自定義背景圖片

### 1. 修改 Carousel 控制面板背景

**檔案位置**: `app/utils/flex_carousel_control_panel.py`

```python
# 修改這個部分的 background_images
self.background_images = {
    "basic": "你的基本功能背景圖片 URL",
    "premium": "你的進階功能背景圖片 URL", 
    "admin": "你的管理功能背景圖片 URL"
}

# 同時修改備用圖片（當主要圖片無法載入時使用）
self.fallback_images = {
    "basic": "你的基本功能備用圖片 URL",
    "premium": "你的進階功能備用圖片 URL",
    "admin": "你的管理功能備用圖片 URL"
}
```

### 2. 修改占卜結果背景

**檔案位置**: `app/utils/divination_flex_message.py`

```python
# 修改 __init__ 方法中的 background_images
self.background_images = {
    "basic": "你的免費用戶背景圖片 URL",
    "premium": "你的付費會員背景圖片 URL",
    "admin": "你的管理員背景圖片 URL"
}

self.fallback_images = {
    "basic": "你的免費用戶備用圖片 URL",
    "premium": "你的付費會員備用圖片 URL", 
    "admin": "你的管理員備用圖片 URL"
}
```

### 3. 修改時間選擇器背景

**檔案位置**: `app/utils/time_picker_flex_message.py`

```python
# 修改 __init__ 方法中的 background_images
self.background_images = {
    "time_picker": "你的時間選擇器背景圖片 URL"
}

self.fallback_images = {
    "time_picker": "你的時間選擇器備用圖片 URL"
}
```

## 半透明遮罩效果

所有背景圖片都使用半透明遮罩來確保文字可讀性：

```python
# 在 FlexBox 中加入 background_color 屬性
background_color="#1A1A2ECC"  # CC = 80% 透明度
```

遮罩顏色說明：
- `#1A1A2ECC`: 深夜藍 80% 透明度（基本功能）
- `#2C3E50CC`: 深石板藍 80% 透明度（進階功能）
- `#8B0000CC`: 深紅色 80% 透明度（管理功能）

## 推薦的圖片來源

### 1. Unsplash (免費高品質圖片)
- **網址**: https://unsplash.com/
- **搜尋關鍵字**: "starry night", "galaxy", "nebula", "space"
- **URL 格式**: `https://images.unsplash.com/photo-[ID]?ixlib=rb-4.0.3&auto=format&fit=crop&w=1040&h=600&q=80`

### 2. 其他來源
- **Pexels**: https://www.pexels.com/
- **Pixabay**: https://pixabay.com/
- **NASA Image Gallery**: https://images.nasa.gov/

### 3. 圖片優化建議
- 使用較暗的圖片確保文字清晰
- 避免過於複雜的圖案
- 建議使用星空、星雲、宇宙相關主題
- 調整對比度和飽和度以配合 UI 設計

## 測試你的背景圖片

修改完背景圖片後，執行測試腳本確認一切正常：

```bash
python scripts/test_starry_theme.py
```

測試內容包括：
- ✅ 背景圖片 URL 有效性
- ✅ Flex Message 生成正常
- ✅ 不同用戶類型顯示正確
- ✅ 色彩主題一致性

## 故障排除

### 常見問題

1. **圖片無法顯示**
   - 檢查 URL 是否為 HTTPS
   - 確認圖片檔案大小 < 10MB
   - 驗證圖片格式為 JPEG/PNG

2. **文字難以閱讀**
   - 調整半透明遮罩的透明度
   - 選擇較暗的背景圖片
   - 修改文字顏色對比

3. **圖片載入緩慢**
   - 使用 CDN 加速的圖片服務
   - 壓縮圖片檔案大小
   - 選擇地理位置較近的圖片服務

### 備用機制

系統設計了完整的備用機制：
1. **主要圖片**: Unsplash 高品質星空圖片
2. **備用圖片**: Placeholder 服務生成的簡化圖片
3. **無圖片模式**: 純色背景 + 文字 Emoji

## 進階自定義

### 動態圖片選擇

你可以根據時間、用戶偏好等條件動態選擇背景圖片：

```python
def get_dynamic_background(user_type: str, time_of_day: str) -> str:
    """根據用戶類型和時間動態選擇背景"""
    if time_of_day == "night":
        return self.night_backgrounds.get(user_type)
    elif time_of_day == "dawn":
        return self.dawn_backgrounds.get(user_type)
    else:
        return self.day_backgrounds.get(user_type)
```

### 季節主題

可以根據季節調整背景圖片：

```python
import datetime

def get_seasonal_background(base_type: str) -> str:
    """根據季節選擇背景"""
    month = datetime.datetime.now().month
    
    if month in [12, 1, 2]:  # 冬季
        return self.winter_backgrounds.get(base_type)
    elif month in [3, 4, 5]:  # 春季
        return self.spring_backgrounds.get(base_type)
    # ... 其他季節
```

## 總結

透過統一的星空主題背景圖片設計，系統現在提供：

✨ **視覺一致性**: 所有 Flex Message 都使用相同的星空主題

🎨 **用戶差異化**: 不同等級用戶看到不同風格的背景

🔧 **易於維護**: 集中化的圖片管理和備用機制

🚀 **高效能**: 優化的圖片載入和緩存策略

立即體驗全新的星空主題介面設計！ 