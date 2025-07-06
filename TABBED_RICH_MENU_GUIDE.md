# 分頁式 Rich Menu 使用指南

## 📋 概述

分頁式 Rich Menu 系統提供了一個強大且靈活的選單解決方案，支援三個分頁和用戶等級權限控制。

### 🎯 主要特色

- **三個分頁設計**：基本功能、運勢、進階選項
- **用戶等級權限**：免費、付費、管理員三種等級
- **圖片資源整合**：使用您自訂的圖片資源
- **星空背景**：美麗的星空背景效果
- **智能緩存**：自動緩存管理，提升性能

## 🗂️ 分頁結構

### 第一分頁：基本功能
- **可用用戶**：所有用戶（免費、付費、管理員）
- **按鈕配置**：
  - 🌙 **會員資訊**（左）
  - 🔮 **本週占卜**（中）
  - 🛰️ **命盤綁定**（右）
- **按鈕排列**：水平並排，中央對齊，適當間距

### 第二分頁：運勢
- **可用用戶**：付費會員、管理員
- **按鈕配置**：
  - 🌍 **流年運勢**（左）
  - 🪐 **流月運勢**（中）
  - ☀️ **流日運勢**（右）
- **按鈕排列**：水平並排，中央對齊，適當間距

### 第三分頁：進階選項
- **可用用戶**：僅管理員
- **按鈕配置**：
  - ⏰ **指定時間占卜**（中央）
- **擴展性**：可日後新增更多管理功能

## 🔐 用戶權限系統

| 用戶等級 | 基本功能 | 運勢 | 進階選項 |
|----------|----------|------|----------|
| 免費會員 | ✅ | ❌ | ❌ |
| 付費會員 | ✅ | ✅ | ❌ |
| 管理員   | ✅ | ✅ | ✅ |

## 🚀 快速開始

### 1. 測試系統
```bash
# 運行測試腳本
python test_tabbed_rich_menu.py
```

### 2. 查看狀態
```bash
# 檢查當前狀態
python manage_tabbed_rich_menu.py --status
```

### 3. 設定默認選單
```bash
# 設定免費會員默認選單
python manage_tabbed_rich_menu.py --default free

# 設定付費會員默認選單
python manage_tabbed_rich_menu.py --default premium

# 設定管理員默認選單
python manage_tabbed_rich_menu.py --default admin
```

## 🛠️ 管理工具使用

### 基本命令

```bash
# 顯示狀態
python manage_tabbed_rich_menu.py --status

# 設定分頁選單
python manage_tabbed_rich_menu.py --setup premium:fortune

# 預覽選單
python manage_tabbed_rich_menu.py --preview admin:admin

# 比較分頁
python manage_tabbed_rich_menu.py --compare premium

# 清理舊選單
python manage_tabbed_rich_menu.py --cleanup

# 強制重建
python manage_tabbed_rich_menu.py --setup free:basic --force
```

### 參數說明

- **用戶等級**：`free`, `premium`, `admin`
- **分頁類型**：`basic`, `fortune`, `admin`
- **--force**：強制重新創建選單
- **--status**：顯示當前狀態
- **--cleanup**：清理舊的非分頁選單

## 💻 程式中使用

### 基本使用

```python
from app.utils.rich_menu_manager import rich_menu_manager

# 設定用戶分頁選單
rich_menu_id = rich_menu_manager.setup_user_tabbed_rich_menu(
    user_id="U1234567890",
    user_level="premium",
    active_tab="fortune"
)

# 切換用戶分頁
success = rich_menu_manager.switch_user_tab(
    user_id="U1234567890",
    user_level="premium",
    new_tab="basic"
)
```

### 進階使用

```python
from app.utils.tabbed_rich_menu_generator import generate_tabbed_rich_menu

# 直接生成分頁選單
image_path, button_areas = generate_tabbed_rich_menu("fortune", "premium")

# 檢查生成結果
if image_path and os.path.exists(image_path):
    print(f"選單生成成功：{image_path}")
    print(f"按鈕數量：{len(button_areas)}")
```

## 🎨 自訂圖片資源

分頁式選單使用 `user_images/` 目錄中的圖片資源：

### 按鈕圖片映射

| 功能 | 圖片文件 | 分頁 |
|------|----------|------|
| 會員資訊 | `moon.png` | 基本功能 |
| 本週占卜 | `crystal_ball.png` | 基本功能 |
| 命盤綁定 | `satellite.png` | 基本功能 |
| 流年運勢 | `earth.png` | 運勢 |
| 流月運勢 | `saturn.png` | 運勢 |
| 流日運勢 | `sun.png` | 運勢 |
| 指定時間占卜 | `clock.png` | 進階選項 |

### 圖片要求

- **格式**：PNG（支援透明背景）或 JPG
- **尺寸**：建議 200x200 到 1000x1000 像素
- **背景**：透明背景效果最佳
- **品質**：高品質圖片以確保清晰度

## 🌟 視覺效果

### 背景設計
- **星空漸變**：深藍到黑色的自然漸變
- **星星效果**：150個小星星 + 30個大星星
- **輕微星雲**：極其輕微的彩色星雲效果
- **分頁標籤**：150px 高度的分頁標籤區域

### 按鈕設計
- **圓形按鈕**：使用您的圖片資源
- **透明背景**：無圓圈背景效果
- **適當間距**：按鈕間有足夠的操作空間
- **中央對齊**：按鈕在內容區域中央對齊

## 🔧 配置說明

### 分頁配置

```python
# 在 tabbed_rich_menu_generator.py 中
def _get_tab_configs(self, user_level: str):
    # 根據用戶等級返回可用分頁
    # 支援動態權限控制
```

### 按鈕配置

```python
# 在 tabbed_rich_menu_generator.py 中
def _get_button_configs(self):
    # 返回各分頁的按鈕配置
    # 包含圖片映射和動作設定
```

## 📊 性能優化

### 緩存機制
- **選單緩存**：自動緩存生成的選單
- **圖片緩存**：重複使用相同的圖片資源
- **智能更新**：僅在必要時重新生成

### 檔案大小
- **基本功能分頁**：約 180-190 KB
- **運勢分頁**：約 150-160 KB
- **進階選項分頁**：約 140-150 KB

## 🚨 故障排除

### 常見問題

1. **選單生成失敗**
   - 檢查圖片文件是否存在
   - 確認用戶等級和分頁權限
   - 查看錯誤日誌

2. **按鈕顯示異常**
   - 確認圖片格式正確
   - 檢查圖片尺寸
   - 驗證配置文件

3. **權限問題**
   - 確認用戶等級設定
   - 檢查分頁權限配置
   - 驗證 LINE Bot 權限

### 調試命令

```bash
# 檢查系統狀態
python manage_tabbed_rich_menu.py --status

# 強制重建測試
python manage_tabbed_rich_menu.py --setup free:basic --force

# 比較所有分頁
python manage_tabbed_rich_menu.py --compare admin
```

## 🎯 最佳實踐

### 1. 用戶體驗
- 保持按鈕功能的一致性
- 提供清晰的分頁標籤
- 確保適當的按鈕間距

### 2. 性能優化
- 使用適當尺寸的圖片
- 避免頻繁重建選單
- 利用緩存機制

### 3. 維護管理
- 定期清理舊選單
- 監控選單使用情況
- 及時更新圖片資源

## 🔮 未來擴展

### 計劃功能
- 動態分頁數量
- 自訂分頁配置
- 更多視覺效果
- 進階權限控制

### 擴展建議
- 添加更多管理功能到進階選項分頁
- 支援季節性主題切換
- 實現用戶偏好設定
- 添加統計和分析功能

---

## 📞 支援

如需協助或有任何問題，請：

1. 查看錯誤日誌
2. 運行診斷命令
3. 檢查配置文件
4. 聯繫技術支援

**祝您使用愉快！** 🌟 