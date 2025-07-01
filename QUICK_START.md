# 🚀 Line Bot 快速啟動指南

## 🎯 當前狀況
✅ **您的Line Bot服務已經完全準備就緒！**

- **Bot名稱**: Guide.with.stars ⭐
- **服務器**: 正在運行 http://localhost:8000
- **Webhook**: `/api/linebot/webhook` 已配置完成
- **只差最後一步**: 將本地服務暴露到公網

## 🌐 三個簡單方案（選一個即可）

### 🥇 方案1: Serveo（最簡單）
在新的終端窗口運行：
```bash
ssh -R 80:localhost:8000 serveo.net
```
- 會顯示類似: `Forwarding HTTP traffic from https://abc123.serveo.net`
- **複製這個URL！**

### 🥈 方案2: 檢查Localtunnel（已運行）
查看之前的終端輸出，尋找：
```
your url is: https://xxxxx.loca.lt
```
- **複製這個URL！**

### 🥉 方案3: 註冊ngrok（最穩定）
1. 訪問 https://dashboard.ngrok.com/signup 註冊
2. 複製您的authtoken
3. 運行: `ngrok config add-authtoken YOUR_TOKEN`
4. 運行: `ngrok http 8000`
5. **複製顯示的https URL！**

## 📱 設置Line Webhook（3分鐘）

1. **訪問**: https://developers.line.biz/console/
2. **找到您的Bot**: Channel ID `2007286218`
3. **點擊進入 → Messaging API**
4. **找到 Webhook settings → Edit**
5. **輸入**: `https://您的URL/api/linebot/webhook`
   
   例如:
   - `https://abc123.serveo.net/api/linebot/webhook`
   - `https://xxxxx.loca.lt/api/linebot/webhook`
   - `https://xxxxx.ngrok.io/api/linebot/webhook`

6. **重要設置**:
   - ✅ 開啟 "Use webhook"
   - ✅ 關閉 "Auto-reply messages"
   - ✅ 點擊 "Verify" 測試連接

## 🎉 開始使用！

**掃描您的Bot QR Code或搜尋 "Guide.with.stars"**

您會看到：
- 🌌 美麗的星空主題歡迎畫面
- 🔮 "開始命盤分析" 按鈕
- 完全無需打字的選單操作體驗

## 🆘 遇到問題？

### 問題1: 找不到隧道URL
```bash
# 重新啟動serveo
ssh -R 80:localhost:8000 serveo.net
# 或重新啟動localtunnel
npx localtunnel --port 8000
```

### 問題2: Bot沒有回應
1. 確認webhook URL是否正確（包含 `/api/linebot/webhook`）
2. 確認"Use webhook"已啟用
3. 檢查隧道是否還在運行

### 問題3: 服務器停止
```bash
# 重新啟動服務器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🌟 功能預覽

成功後，用戶體驗包括：
- 📅 **零輸入生辰資訊收集**: 全按鈕選擇年月日時辰
- 🎨 **星空美學設計**: 深藍背景+星座裝飾
- 📊 **四種專業分析**:
  - ⭐ 基本命盤分析
  - 🎯 流年運勢查詢  
  - 🌙 流月運勢預測
  - ⏳ 大限運勢分析

---
**最重要的一步**: 獲取隧道URL → 設置Line Webhook → 開始使用！ 🚀 