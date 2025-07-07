# 🚀 Railway 部署 LINE Webhook 簽名驗證修復指南

## 📋 問題總結

**問題**: LINE webhook 簽名驗證在 Railway 生產環境中失敗，原因是 `LINE_CHANNEL_SECRET` 環境變數未正確載入。

**錯誤日誌**:
```
2025-07-07 05:10:52,620 - ERROR - LINE簽名驗證失敗
2025-07-07 05:11:02,072 - WARNING - LINE 簽名驗證失敗 - 預期: 4Rho2M/Ukc..., 實際: 6G6j+7+C1q...
```

**根本原因**: 
- 本地開發使用 `config.env` 檔案載入環境變數
- Railway 生產環境中 `config.env` 檔案不可用
- 應用程式使用預設值 `"your_channel_secret_here"` 而非正確的 Channel Secret

## 🔧 解決方案

### 步驟 1: 在 Railway 設定環境變數

1. **登入 Railway Dashboard**
   - 前往: https://railway.app/dashboard
   - 選擇您的專案

2. **進入環境變數設定**
   - 點擊專案
   - 選擇 "Variables" 標籤

3. **添加必要的環境變數**
   ```
   變數名稱: LINE_CHANNEL_SECRET
   變數值: 611969a2b460d46e71648a2c3a6d54fb
   
   變數名稱: LINE_CHANNEL_ACCESS_TOKEN  
   變數值: AjXjeHlVLV4/wFDEcERkXK2YL7ncFQqlxNQJ29wm6aHcbYdMbEvqf9dZZHCckzaPSYpkO+WKOV6KUFVvMwW85dJl+KDV95sn3VIBphhItS3F5veXYAgZqhzzJcNw5FpnJjqGcorKhue0I26XxJMX2AdB04t89/1O/w1cDnyilFU=
   ```

4. **儲存並重新部署**
   - 點擊 "Save"
   - Railway 會自動觸發重新部署

### 步驟 2: 驗證修復

#### 方法 1: 檢查應用程式日誌
1. 在 Railway Dashboard 中查看 "Logs" 標籤
2. 尋找以下成功訊息:
   ```
   ✅ LINE_CHANNEL_SECRET 已設定: 611969a2...
   ✅ LINE_CHANNEL_ACCESS_TOKEN 已設定: AjXjeHlVLV4/wFDEcERk...
   ```

#### 方法 2: 測試 LINE Webhook
1. 透過 LINE Bot 發送訊息
2. 檢查是否收到回應
3. 查看日誌中是否出現 `✅ LINE 簽名驗證成功`

### 步驟 3: 本地測試驗證

使用提供的檢查腳本驗證配置：
```bash
python check_env_config.py
```

預期輸出應顯示所有檢查通過。

## 🔍 技術改進詳情

### 1. 強化環境變數載入機制

**之前**: 
```python
load_dotenv("config.env")
```

**現在**:
```python
def load_environment_variables():
    # 1. 嘗試載入 .env 檔案
    if os.path.exists(".env"):
        load_dotenv(".env")
    
    # 2. 嘗試載入 config.env 檔案  
    if os.path.exists("config.env"):
        load_dotenv("config.env")
    
    # 3. 記錄載入狀態
    # ...詳細的日誌記錄
```

### 2. 改進簽名驗證函數

**新增功能**:
- 詳細的配置驗證和日誌記錄
- 明確的錯誤訊息和修復指導
- 自動檢測常見配置問題

**範例輸出**:
```
❌ LINE_CHANNEL_SECRET 仍為預設值，簽名驗證將失敗
正確的 Channel Secret 應為: 611969a2b460d46e71648a2c3a6d54fb
請在 Railway 專案設定中添加環境變數：
變數名: LINE_CHANNEL_SECRET
變數值: 611969a2b460d46e71648a2c3a6d54fb
```

### 3. 添加配置檢查工具

創建了 `check_env_config.py` 腳本，提供：
- 環境配置檔案檢查
- LINE Bot 配置驗證
- 簽名驗證功能測試
- Railway 設定指南生成

## 🚨 常見問題排除

### Q1: 重新部署後仍然失敗
**解決方案**:
1. 確認環境變數值沒有多餘空格
2. 確認沒有包含引號
3. 檢查 Variable 名稱拼寫正確
4. 嘗試刪除並重新添加環境變數

### Q2: 本地可以但 Railway 不行
**檢查項目**:
1. Railway 環境變數是否正確設定
2. `config.env` 是否被包含在 `.gitignore` 中
3. 專案是否正確部署

### Q3: 如何確認環境變數已載入
**方法**:
1. 查看應用程式啟動日誌
2. 尋找配置驗證訊息
3. 使用檢查腳本本地測試

## 📋 部署檢查清單

部署前確認：
- [ ] Railway 環境變數已正確設定
- [ ] `LINE_CHANNEL_SECRET` = `611969a2b460d46e71648a2c3a6d54fb`
- [ ] `LINE_CHANNEL_ACCESS_TOKEN` 為完整的 Token
- [ ] 沒有多餘的空格或引號

部署後確認：
- [ ] 應用程式成功啟動
- [ ] 日誌顯示配置驗證成功
- [ ] LINE Webhook 測試成功
- [ ] 收到 `✅ LINE 簽名驗證成功` 日誌

## 🔄 後續維護

### 定期檢查
- 監控 LINE Webhook 錯誤率
- 定期檢查環境變數設定
- 關注 Railway 平台更新

### 日誌監控
關鍵字監控：
- `❌ LINE 簽名驗證失敗`
- `LINE_CHANNEL_SECRET 未正確設定`
- `Invalid signature`

### 備用方案
如遇到持續問題：
1. 檢查 LINE Developers Console 設定
2. 重新生成 Channel Secret（如必要）
3. 聯繫 Railway 技術支援

---

**修復總結**: 透過在 Railway 正確設定環境變數並改進應用程式的配置載入機制，LINE webhook 簽名驗證問題已獲得解決。強化的日誌記錄有助於快速診斷未來的配置問題。 