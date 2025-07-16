# Carousel 功能選單自定義指南

## 概述

新的 Carousel 功能選單採用分頁式設計，用戶可以左右滑動查看不同的功能區域。每個分頁都有自己的主題色彩和視覺效果。

## 功能特色

### 🌌 分頁式設計
- **基本功能分頁**: 免費用戶可訪問
- **進階功能分頁**: 付費會員和管理員可訪問
- **管理功能分頁**: 僅管理員可訪問

### 🎨 星空主題
- 深夜藍背景色 (`#1A1A2E`)
- 星光金強調色 (`#FFD700`)
- 漸變卡片背景
- 星星和皇冠等級指示器

### 🔒 權限控制
- 根據用戶等級動態顯示可用分頁
- 權限不足的功能會顯示為灰色禁用狀態
- 智能提示升級訊息

## 自定義背景圖片

### 1. 準備背景圖片

創建或獲取星空主題的背景圖片：

```bash
# 創建背景圖片目錄
mkdir -p static/images/backgrounds

# 推薦尺寸：800x400 像素
# 格式：PNG 或 JPG
# 主題：星空、宇宙、夜空等
```

### 2. 圖片規格建議

| 分頁類型 | 主題色調 | 建議元素 | 尺寸 |
|---------|---------|---------|------|
| 基本功能 | 深藍 + 金色 | 星空、水晶球 | 800x400 |
| 進階功能 | 紫色 + 橙色 | 星雲、行星 | 800x400 |
| 管理功能 | 深紅 + 金色 | 皇冠、權杖 | 800x400 |

### 3. 修改背景圖片 URL

編輯 `app/utils/flex_carousel_control_panel.py`：

```python
# 在 __init__ 方法中修改背景圖片 URL
self.background_images = {
    "basic": "https://your-domain.com/static/images/basic_bg.png",
    "premium": "https://your-domain.com/static/images/premium_bg.png", 
    "admin": "https://your-domain.com/static/images/admin_bg.png"
}
```

### 4. 使用本地靜態資源

如果要使用本地圖片資源：

```python
# 設置靜態資源服務
# 在 main.py 或相應的 FastAPI 設定中
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

# 然後更新圖片 URL
self.background_images = {
    "basic": f"{BASE_URL}/static/images/basic_bg.png",
    "premium": f"{BASE_URL}/static/images/premium_bg.png",
    "admin": f"{BASE_URL}/static/images/admin_bg.png"
}
```

## 自定義色彩主題

### 1. 修改色彩配置

在 `FlexCarouselControlPanelGenerator` 類別中：

```python
def __init__(self):
    self.colors = {
        "primary": "#4A90E2",        # 主要藍色
        "secondary": "#FFD700",      # 星光金
        "accent": "#9B59B6",         # 深紫色
        "premium": "#E67E22",        # 橙色
        "admin": "#E74C3C",          # 管理員紅
        "background": "#1A1A2E",     # 深夜藍背景
        "card_bg": "#16213E",        # 卡片背景
        # ... 其他顏色
    }
```

### 2. 色彩主題範例

#### 🌙 深藍夜空主題（預設）
```python
colors = {
    "primary": "#4A90E2",     # 星空藍
    "secondary": "#FFD700",   # 星光金
    "background": "#1A1A2E",  # 深夜藍
}
```

#### 🌸 櫻花粉主題
```python
colors = {
    "primary": "#FF69B4",     # 粉紅色
    "secondary": "#FFB6C1",   # 淺粉色
    "background": "#2F1B2C",  # 深紫背景
}
```

#### 🍃 森林綠主題
```python
colors = {
    "primary": "#228B22",     # 森林綠
    "secondary": "#90EE90",   # 淺綠色
    "background": "#1F2F1F",  # 深綠背景
}
```

## 新增自定義分頁

### 1. 擴展分頁類型

```python
def _get_available_pages(self, is_admin: bool, is_premium: bool) -> List[str]:
    pages = ["basic"]  # 基本功能
    
    if is_premium or is_admin:
        pages.append("premium")  # 進階功能
        
    if is_admin:
        pages.append("admin")    # 管理功能
        pages.append("super")    # 超級管理功能（新增）
        
    return pages
```

### 2. 創建新分頁 Bubble

```python
def _create_super_page_bubble(self) -> FlexBubble:
    """創建超級管理功能分頁"""
    return FlexBubble(
        size="giga",
        body=FlexBox(
            layout="vertical",
            contents=[
                self._create_page_header("⚡ 超級功能", "超級管理員專用", "#FF0000"),
                # ... 其他內容
            ]
        )
    )
```

## 測試和部署

### 1. 本地測試

```bash
# 運行測試腳本
python scripts/test_carousel_panel.py

# 測試特定用戶類型
python -c "
from app.utils.flex_carousel_control_panel import FlexCarouselControlPanelGenerator
generator = FlexCarouselControlPanelGenerator()
panel = generator.generate_carousel_control_panel({
    'user_info': {'is_admin': True},
    'membership_info': {'is_premium': True}
})
print('測試成功!' if panel else '測試失敗!')
"
```

### 2. 部署檢查清單

- [ ] 背景圖片已上傳到靜態資源目錄
- [ ] 靜態資源服務已正確配置
- [ ] 色彩主題已測試在不同設備上的顯示效果
- [ ] 權限控制邏輯已測試
- [ ] JSON 輸出格式已驗證

## 最佳實踐

### 1. 圖片優化
- 使用 WebP 格式以減少檔案大小
- 提供 2x 版本支援高解析度螢幕
- 添加適當的 alt 文字

### 2. 色彩無障礙
- 確保文字與背景有足夠的對比度
- 測試色盲友善度
- 提供高對比模式選項

### 3. 效能考量
- 合理使用快取機制
- 圖片延遲載入
- 減少不必要的 DOM 元素

## 疑難排解

### 常見問題

**Q: 分頁沒有正確顯示？**
A: 檢查用戶權限設定和 `_get_available_pages` 邏輯

**Q: 背景圖片無法載入？**
A: 確認圖片 URL 可訪問和靜態資源配置

**Q: 色彩顯示不正確？**
A: 檢查 CSS 色彩值格式和 LINE 平台相容性

**Q: JSON 轉換失敗？**
A: 確認所有 FlexBox 元素都有必要的屬性

## 參考資源

- [LINE Flex Message 官方文檔](https://developers.line.biz/en/docs/messaging-api/flex-message-elements/)
- [色彩搭配工具](https://coolors.co/)
- [星空圖片資源](https://unsplash.com/s/photos/starry-sky)
- [無障礙設計指南](https://webaim.org/articles/contrast/) 