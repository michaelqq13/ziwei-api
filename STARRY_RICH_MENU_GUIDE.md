# 星空主題圖文選單使用指南

## 概述

本系統現在支援美麗的星空主題圖文選單，以星空為背景，使用星點作為按鈕，為用戶提供更具視覺吸引力的操作體驗。

## 星空主題特色

### 🌌 視覺特效
- **深藍漸變背景**：從深藍色漸變到黑色，營造星空氛圍
- **隨機小星星**：200-300個隨機分佈的小星星作為背景裝飾
- **多樣化按鈕**：5種不同形狀的天體按鈕（星形、太陽、月亮、星球、水晶）
- **超大字體顯示**：48px 超大字體，極其清晰易讀
- **幾何布局**：正五邊形和正三角形的對稱布局，視覺效果更佳
- **大尺寸點擊區域**：每個按鈕都有大型圓形點擊區域，半徑105-120px

### 📱 雙選單系統

#### 主選單（已綁定用戶） - 正五邊形布局
```
⭐ 頂部星形 - 🔮 本週占卜
💎 右上水晶 - 📊 我的命盤  
🪐 右下星球 - ⚙️ 設定
🌙 左下月亮 - 🌙 流月運勢
☀️ 左上太陽 - 📅 流年運勢
```

#### 未綁定用戶選單 - 正三角形布局
```
⭐ 頂部星形 - 🔮 本週占卜
🪐 右下星球 - 🌐 前往網站
💎 左下水晶 - ❓ 使用說明
```

## 技術實現

### 核心組件

1. **StarryRichMenuGenerator** (`app/utils/starry_rich_menu_generator.py`)
   - 星空背景生成
   - 多種按鈕形狀繪製（星形、太陽、月亮、星球、水晶）
   - 大字體文字標籤處理
   - 無連線乾淨設計

2. **StarryRichMenuManager** (`app/utils/starry_rich_menu_manager.py`)
   - 圖文選單創建
   - 圓形點擊區域定義
   - 圖片上傳管理
   - 選單設置和綁定

3. **DynamicRichMenuManager** (`app/utils/dynamic_rich_menu.py`)
   - 智能選單切換
   - 優先載入星空主題
   - 用戶狀態檢測

### 圖片規格

- **尺寸**：2500 x 1686 像素
- **格式**：PNG
- **檔案大小**：約 38-55KB
- **字體**：STHeiti Medium（macOS中文字體）

### 點擊區域設計

雖然 Line Bot API 只支援矩形點擊區域，但我們通過以下方式實現了圓形按鈕的效果：

```python
def _create_circular_area(self, center_x, center_y, radius, action):
    """創建圓形點擊區域"""
    return RichMenuArea(
        bounds=RichMenuBounds(
            x=center_x - radius,
            y=center_y - radius, 
            width=radius * 2,
            height=radius * 2
        ),
        action=action
    )
```

## 使用方法

### 設置星空主題選單

```bash
# 設置星空主題圖文選單
python setup_starry_rich_menu.py setup

# 測試圖片生成
python setup_starry_rich_menu.py test

# 預覽選單結構
python setup_starry_rich_menu.py preview

# 刪除所有圖文選單
python setup_starry_rich_menu.py delete

# 顯示幫助
python setup_starry_rich_menu.py help
```

### 自動化流程

1. **圖片生成**：自動創建星空背景和星形按鈕
2. **選單創建**：在 Line 平台創建圖文選單
3. **圖片上傳**：將生成的圖片上傳到對應選單
4. **默認設置**：設置為默認圖文選單
5. **ID保存**：保存選單ID到 `starry_rich_menu_ids.txt`

### 智能切換

系統會根據用戶綁定狀態自動顯示合適的星空主題選單：

- **用戶關注時**：檢查綁定狀態，設置對應選單
- **完成綁定時**：自動切換到主選單
- **解除綁定時**：切換回未綁定用戶選單

## 文件結構

```
rich_menu_images/
├── starry_main_rich_menu.png      # 星空主選單圖片
└── starry_unbound_rich_menu.png   # 星空未綁定用戶選單圖片

starry_rich_menu_ids.txt            # 星空主題選單ID
setup_starry_rich_menu.py           # 星空主題設置腳本

app/utils/
├── starry_rich_menu_generator.py   # 星空圖片生成器
├── starry_rich_menu_manager.py     # 星空選單管理器
└── dynamic_rich_menu.py            # 動態選單管理器（已更新）
```

## 優勢對比

### 星空主題 vs 傳統方塊

| 特色 | 星空主題 | 傳統方塊 |
|------|----------|----------|
| 視覺吸引力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 點擊精確度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 主題一致性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 用戶體驗 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 技術複雜度 | ⭐⭐⭐⭐ | ⭐⭐ |

## 故障排除

### 常見問題

1. **星點沒有文字**
   - 檢查 STHeiti 字體是否可用
   - 確認圖片生成過程中的字體載入日誌

2. **點擊區域不準確**
   - 確認星點位置與點擊區域坐標一致
   - 檢查圓形區域半徑設置

3. **圖片載入失敗**
   - 確認 `rich_menu_images` 目錄存在
   - 檢查圖片檔案權限

4. **選單ID載入失敗**
   - 確認 `starry_rich_menu_ids.txt` 文件存在
   - 檢查檔案格式和內容

### 重新設置

如果遇到問題，可以完全重新設置：

```bash
# 1. 刪除所有現有選單
python setup_starry_rich_menu.py delete

# 2. 重新設置星空主題
python setup_starry_rich_menu.py setup

# 3. 驗證設置
python setup_starry_rich_menu.py preview
```

## 自訂選項

### 修改星點位置

在 `starry_rich_menu_generator.py` 中修改 `star_configs` 配置：

```python
star_configs = [
    {"pos": (x, y), "size": size, "label": "文字"},
    # 添加更多星點...
]
```

### 調整視覺效果

- **背景顏色**：修改 `create_starry_background()` 中的漸變顏色
- **星星數量**：調整 `_add_background_stars()` 中的 `num_stars`
- **按鈕形狀**：在 `generate_starry_rich_menu()` 中更改 `button_type`
- **字體大小**：調整 `__init__()` 中的 `font_size_large` 等參數

### 更改點擊區域

在 `starry_rich_menu_manager.py` 中調整圓形區域半徑：

```python
{"center": (x, y), "radius": radius, "action": "action_name"}
```

## 總結

星空主題圖文選單為紫微斗數系統提供了更符合占星主題的視覺體驗。通過結合美觀的星空背景和精確的點擊區域，我們成功實現了既美觀又實用的圖文選單系統。

用戶現在可以通過點擊美麗的星點來訪問各種功能，使整個占卜體驗更加神秘和吸引人。 