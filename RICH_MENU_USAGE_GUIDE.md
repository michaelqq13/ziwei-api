# Rich Menu 圖片資源型生成器使用指南

## 🎯 概述

您的 LINE Bot 現在支援兩種 Rich Menu 生成模式：
1. **圖片資源型**：使用您提供的圖片文件
2. **程式生成型**：使用程式繪製的圖案（原有方式）

## 🚀 快速開始

### 1. 準備您的圖片
將您的按鈕圖片放入 `user_images/` 目錄中：
```
user_images/
├── crystal_ball.png     # 本週占卜（水晶球）
├── rocket.png          # 流年運勢
├── saturn.png          # 流月運勢
├── ufo.png             # 流日運勢
├── earth.png           # 命盤綁定
├── moon.png            # 會員資訊
└── clock.png           # 指定時間占卜（管理員專用）
```

### 2. 圖片建議規格
- **尺寸**：200x200 到 400x400 像素
- **格式**：PNG（推薦，支援透明背景）或 JPG
- **風格**：清晰、簡潔的圖案
- **背景**：透明背景效果最佳

### 3. 配置按鈕映射
編輯 `user_images/button_image_config.json`：
```json
{
  "button_images": {
    "weekly_divination": {
      "image_file": "crystal_ball.png",
      "text": "本週占卜",
      "fallback_color": [200, 150, 200],
      "description": "水晶球圖片 - 用於本週占卜功能"
    }
  }
}
```

## 🛠️ 使用方法

### 方法 1：使用管理腳本（推薦）
```bash
# 查看當前狀態
python manage_rich_menu_mode.py --status

# 使用圖片資源型生成會員選單
python manage_rich_menu_mode.py --mode image --level member --force

# 使用圖片資源型生成管理員選單
python manage_rich_menu_mode.py --mode image --level admin --force

# 比較兩種生成模式
python manage_rich_menu_mode.py --compare

# 設定圖片資源
python manage_rich_menu_mode.py --setup

# 清理舊選單
python manage_rich_menu_mode.py --cleanup
```

### 方法 2：在程式中使用
```python
from app.utils.rich_menu_manager import RichMenuManager

# 使用圖片資源型生成器
manager = RichMenuManager(use_image_based=True)

# 生成會員選單
member_menu_id = manager.setup_complete_rich_menu(force_recreate=True)

# 生成管理員選單
admin_menu_id = manager.setup_admin_rich_menu(force_recreate=True)

# 切換生成模式
manager.switch_generation_mode(use_image_based=False)  # 切換到程式生成型
```

### 方法 3：使用全域函數
```python
from app.utils.rich_menu_manager import setup_rich_menu, update_user_rich_menu

# 設定圖片資源型選單
menu_id = setup_rich_menu(force_recreate=True, use_image_based=True)

# 更新用戶選單
success = update_user_rich_menu(user_id, is_admin=False, use_image_based=True)
```

## 🎨 自訂圖片

### 替換水晶球圖片
1. 準備您的水晶球圖片（建議 PNG 格式，透明背景）
2. 將圖片命名為 `crystal_ball.png`
3. 放入 `user_images/` 目錄
4. 重新生成選單：
   ```bash
   python manage_rich_menu_mode.py --mode image --level member --force
   ```

### 添加新按鈕圖片
1. 將圖片放入 `user_images/` 目錄
2. 編輯 `user_images/button_image_config.json`
3. 添加新的按鈕配置：
   ```json
   "new_button": {
     "image_file": "new_image.png",
     "text": "新按鈕",
     "fallback_color": [255, 255, 255],
     "description": "新按鈕的描述"
   }
   ```

## 🔧 進階設定

### 圖片處理設定
在 `button_image_config.json` 中調整 `image_settings`：
```json
{
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

### 按鈕映射
目前支援的按鈕類型：
- `weekly_divination`: 本週占卜
- `yearly_fortune`: 流年運勢
- `monthly_fortune`: 流月運勢
- `daily_fortune`: 流日運勢
- `chart_binding`: 命盤綁定
- `member_info`: 會員資訊
- `scheduled_divination`: 指定時間占卜（管理員專用）

## 🚨 故障排除

### 圖片不顯示
1. 檢查圖片文件是否存在於 `user_images/` 目錄
2. 檢查 `button_image_config.json` 中的文件名是否正確
3. 確認圖片格式是否支援（PNG、JPG）
4. 查看系統會使用 `fallback_color` 生成純色按鈕

### 選單生成失敗
1. 檢查 LINE Bot 設定是否正確
2. 確認網路連線正常
3. 查看錯誤日誌
4. 嘗試使用 `--force` 參數強制重新生成

### 切換模式
```bash
# 切換回程式生成型
python manage_rich_menu_mode.py --mode programmatic --level member --force

# 切換到圖片資源型
python manage_rich_menu_mode.py --mode image --level member --force
```

## 📊 比較兩種模式

| 特性 | 圖片資源型 | 程式生成型 |
|------|------------|------------|
| 圖片品質 | 高（使用原始圖片） | 中（程式繪製） |
| 自訂彈性 | 高（可使用任何圖片） | 低（固定樣式） |
| 檔案大小 | 較大 | 較小 |
| 設定複雜度 | 中（需要準備圖片） | 低（自動生成） |
| 視覺效果 | 專業 | 程式化 |

## 🎯 建議使用場景

### 使用圖片資源型當：
- 您有專業設計的圖片
- 需要品牌一致性
- 要求高品質視覺效果
- 有特定的圖片需求

### 使用程式生成型當：
- 快速原型開發
- 不需要特定圖片
- 希望保持檔案大小較小
- 偏好程式化的一致風格

## 📝 注意事項

1. **圖片版權**：確保您使用的圖片有適當的使用權限
2. **檔案大小**：大型圖片會增加選單載入時間
3. **透明背景**：PNG 格式的透明背景效果最佳
4. **備份**：建議備份您的圖片文件和配置
5. **測試**：在正式使用前先測試生成效果

## 🔄 更新流程

1. 準備新圖片
2. 更新配置文件
3. 測試生成效果
4. 部署到正式環境
5. 清理舊選單

現在您可以完全控制 Rich Menu 的視覺效果了！🎉 