# 🌐 Line Bot Webhook 公網設置指南

## ✅ 當前狀態
- **服務器**: ✅ 運行在 http://localhost:8000
- **Webhook端點**: `/api/linebot/webhook`
- **需要**: 將本地服務暴露到公網

## 🚀 快速解決方案

### 方案1: Serveo (推薦 - 無需註冊)
```bash
ssh -R 80:localhost:8000 serveo.net
```
- ✅ 無需註冊
- ✅ 立即可用
- ✅ 會顯示類似: `Forwarding HTTP traffic from https://xxxx.serveo.net`

### 方案2: Localtunnel (已啟動)
```bash
npx localtunnel --port 8000
```
- ✅ 無需註冊
- ✅ 已在後台運行
- 📱 查看終端輸出獲取URL: `your url is: https://xxxx.loca.lt`

### 方案3: ngrok (需要註冊)
如果您想使用ngrok：
1. 訪問: https://dashboard.ngrok.com/signup
2. 註冊免費帳號
3. 獲取authtoken
4. 運行: `ngrok config add-authtoken YOUR_TOKEN`
5. 啟動: `ngrok http 8000`

### 方案4: bore
```bash
npx bore 8000
```

## 📱 Line Developers Console 設置

1. **訪問**: https://developers.line.biz/console/
2. **選擇您的Channel**: Channel ID 2007286218
3. **進入 Messaging API 設定**
4. **設置 Webhook URL**:
   ```
   https://your-tunnel-url/api/linebot/webhook
   ```
   例如:
   - Serveo: `https://xxxx.serveo.net/api/linebot/webhook`
   - Localtunnel: `https://xxxx.loca.lt/api/linebot/webhook`
   - ngrok: `https://xxxx.ngrok.io/api/linebot/webhook`

5. **重要設置**:
   - ✅ 啟用 "Use webhook"
   - ✅ 停用 "Auto-reply messages" (避免衝突)
   - ✅ 可選擇啟用 "Greeting messages"

## 🧪 測試步驟

### 1. 確認隧道URL
根據您選擇的方案，確認獲得HTTPS URL

### 2. 測試webhook端點
```bash
curl -X POST https://your-tunnel-url/api/linebot/webhook \
  -H "Content-Type: application/json" \
  -H "X-Line-Signature: test" \
  -d '{"events":[]}'
```
應該返回: `{"detail":"Invalid signature"}` (這是正常的)

### 3. 加入Line Bot
- 掃描Bot QR Code
- 或搜尋 "Guide.with.stars"
- 發送任何訊息測試

## 🎯 預期體驗

用戶加入Bot後會看到：
- 🌌 星空主題歡迎選單
- 🔮 "開始命盤分析" 按鈕
- 完全零文字輸入的操作流程

## 🛠️ 故障排除

### 隧道無法連接
```bash
# 重新啟動服務器
pkill -f uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 嘗試不同的隧道服務
ssh -R 80:localhost:8000 serveo.net
```

### Line Bot無回應
1. 檢查webhook URL是否正確
2. 確認啟用了 "Use webhook"
3. 檢查隧道是否仍在運行
4. 查看服務器日誌

### 獲取服務器日誌
```bash
# 查看當前運行的python進程
ps aux | grep uvicorn

# 如果需要，在前台運行查看詳細日誌
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 🌟 成功指標

當一切正常時，您會看到：
- Line Bot立即回應用戶訊息
- 美麗的星空主題Flex Message
- 流暢的按鈕選擇體驗
- 專業的紫微斗數分析結果

---
**提示**: 如果使用免費隧道服務，URL可能會定期變更，需要重新設置webhook URL。生產環境建議使用固定域名。 