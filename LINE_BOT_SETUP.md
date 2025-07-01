# 🌌 紫微斗數 Line Bot 設置指南

## ✅ 當前狀態
您的Line Bot已經成功配置並可以使用！

- **Bot名稱**: Guide.with.stars ⭐
- **Channel ID**: 2007286218
- **狀態**: ✅ 連接測試成功
- **Webhook端點**: ✅ 正常響應
- **API文檔**: http://localhost:8000/docs

## 🚀 快速啟動

### 1. 使用啟動腳本（推薦）
```bash
./start_linebot.sh
```

### 2. 手動啟動
```bash
# 激活虛擬環境
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 測試連接
python test_linebot.py

# 啟動服務器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 公網訪問設置

### 方案1: 使用 ngrok（推薦）
```bash
# 安裝ngrok
brew install ngrok  # macOS
# 或下載: https://ngrok.com/download

# 啟動隧道
ngrok http 8000
```

複製ngrok提供的https URL，例如：`https://abc123.ngrok.io`

### 方案2: 使用其他工具
- **localtunnel**: `npx localtunnel --port 8000`
- **serveo**: `ssh -R 80:localhost:8000 serveo.net`

## 📱 Line Developers Console 設置

1. 訪問 [Line Developers Console](https://developers.line.biz/console/)
2. 選擇您的Channel (Channel ID: 2007286218)
3. 進入 **Messaging API** 設定
4. 設置 **Webhook URL**:
   ```
   https://your-ngrok-url.ngrok.io/api/linebot/webhook
   ```
   例如: `https://abc123.ngrok.io/api/linebot/webhook`

5. 確認以下設置：
   - ✅ **Use webhook**: 啟用
   - ✅ **Allow bot to join group chats**: 依需求
   - ✅ **Auto-reply messages**: 停用（避免衝突）
   - ✅ **Greeting messages**: 依需求

## 🧪 測試步驟

### 1. 確認服務運行
訪問：http://localhost:8000/docs 應該看到API文檔

### 2. 測試Webhook
使用您的Line Bot QR Code或搜尋Bot名稱加入

### 3. 發送測試訊息
發送任何訊息應該收到星空主題的歡迎選單

## 🎨 Line Bot功能特色

### 🌟 零文字輸入設計
- 所有操作都通過美麗的選單按鈕完成
- 無需輸入任何文字，只需點擊

### 🌌 星空主題美化
- 深空藍背景色調
- 星座與時辰生肖設計
- 紫微斗數專業色彩系統

### 📊 完整命理分析
- 基本命盤分析
- 流年運勢查詢
- 流月運勢預測
- 大限運勢分析

## 🛠️ 問題排解

### Line Bot無回應
1. 檢查Webhook URL是否正確設置
2. 確認ngrok隧道是否正常運行
3. 查看服務器日誌是否有錯誤

### 服務器錯誤
```bash
# 查看詳細錯誤日誌
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

### 重新測試連接
```bash
python test_linebot.py
```

## 📁 相關文件
- `config.env` - 環境變數配置
- `test_linebot.py` - 連接測試腳本
- `start_linebot.sh` - 啟動腳本
- `app/routes/linebot_routes.py` - Line Bot路由
- `app/utils/linebot_*` - Line Bot核心組件

## 🎯 下一步
1. 設置ngrok隧道
2. 配置Line Developers Console的Webhook URL
3. 用手機掃描QR Code測試Line Bot
4. 享受星空主題的紫微斗數分析體驗！

---
**提示**: 如果遇到任何問題，請檢查`config.env`文件中的憑證是否正確，並確保網路連接正常。 