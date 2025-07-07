# 按鈕圖片資源說明

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
