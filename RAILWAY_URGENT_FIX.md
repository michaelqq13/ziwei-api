# 🚨 Railway LINE Webhook 緊急修復指南

## ⚡ 緊急狀態分析

**當前問題**: Railway 生產環境中 LINE Webhook 簽名驗證持續失敗

**最新錯誤日誌** (2025-07-07 10:02):
```
WARNING - LINE 簽名驗證失敗 - 預期: K8dDJWQWIX..., 實際: rVxy+ciRs2...
ERROR - LINE簽名驗證失敗
HTTP 500 錯誤來自 IP: 147.92.149.168 (LINE 伺服器)
```

**問題診斷**:
1. ❌ Railway 環境變數未正確設定
2. ❌ 可能程式碼更新尚未部署到生產環境
3. ❌ LINE_CHANNEL_SECRET 仍使用預設值

## 🚀 立即行動步驟

### 步驟 1: 檢查 Railway 部署狀態
1. 登入 Railway Dashboard: https://railway.app/dashboard
2. 進入您的專案
3. 檢查 "Deployments" 標籤，確認最新程式碼已部署

### 步驟 2: 設定環境變數 (最關鍵)
1. 點擊 "Variables" 標籤
2. 添加或更新以下環境變數：

```
變數名: LINE_CHANNEL_SECRET
變數值: 611969a2b460d46e71648a2c3a6d54fb

變數名: LINE_CHANNEL_ACCESS_TOKEN
變數值: AjXjeHlVLV4/wFDEcERkXK2YL7ncFQqlxNQJ29wm6aHcbYdMbEvqf9dZZHCckzaPSYpkO+WKOV6KUFVvMwW85dJl+KDV95sn3VIBphhItS3F5veXYAgZqhzzJcNw5FpnJjqGcorKhue0I26XxJMX2AdB04t89/1O/w1cDnyilFU=
```

⚠️  **重要提醒**:
- 不要包含引號
- 確保沒有前後空格
- 完整複製貼上，不要遺漏任何字符

### 步驟 3: 強制重新部署
1. 在 Railway 專案中，點擊 "Settings"
2. 找到 "Redeploy" 選項並點擊
3. 或者推送任何小的程式碼變更觸發重新部署

### 步驟 4: 監控部署結果
1. 前往 "Logs" 標籤
2. 等待部署完成 (通常 2-3 分鐘)
3. 尋找以下成功訊息：
   ```
   ✅ LINE_CHANNEL_SECRET 已設定: 611969a2...
   === LINE Bot 配置驗證 ===
   ```

### 步驟 5: 測試修復結果
1. 透過 LINE Bot 發送測試訊息
2. 觀察日誌中是否出現：
   ```
   ✅ LINE 簽名驗證成功
   ```
3. 確認不再出現 HTTP 500 錯誤

## 🔍 如何確認問題已解決

### 成功指標:
- ✅ Railway 日誌顯示 `✅ LINE_CHANNEL_SECRET 已設定`
- ✅ LINE 訊息能正常收發
- ✅ 日誌顯示 `✅ LINE 簽名驗證成功`
- ✅ 不再出現 HTTP 500 錯誤

### 失敗指標:
- ❌ 仍然看到 `WARNING - LINE 簽名驗證失敗`
- ❌ 日誌顯示 `❌ LINE_CHANNEL_SECRET 仍為預設值`
- ❌ 持續收到 HTTP 500 錯誤

## 💡 故障排除

### 問題 1: 環境變數設定後仍然失敗
**解決方案**:
```bash
# 確認變數值正確
變數名稱檢查: LINE_CHANNEL_SECRET (注意大小寫)
變數值檢查: 611969a2b460d46e71648a2c3a6d54fb (32位十六進制字符)
```

### 問題 2: 部署沒有自動觸發
**解決方案**:
1. 手動點擊 "Redeploy"
2. 或推送小變更到 Git repository

### 問題 3: 仍然看到舊版錯誤訊息格式
**解決方案**:
```bash
# 確認程式碼已推送到 Railway
git push origin main
# 等待自動部署完成
```

## 📞 緊急聯繫資訊

如果上述步驟無法解決問題：

1. **立即檢查 Railway 服務狀態**: https://status.railway.app/
2. **查看 Railway 文档**: https://docs.railway.app/
3. **檢查 LINE Developers Console**: https://developers.line.biz/

## 📋 修復檢查清單

完成修復後，請確認：
- [ ] Railway 環境變數已正確設定
- [ ] 最新程式碼已部署到生產環境  
- [ ] 日誌顯示配置驗證成功
- [ ] LINE Webhook 測試通過
- [ ] 不再出現 HTTP 500 錯誤
- [ ] LINE Bot 功能正常運作

---

**預估修復時間**: 5-10 分鐘  
**關鍵步驟**: 設定 Railway 環境變數並重新部署  
**驗證方法**: 檢查 Railway 日誌和 LINE Bot 功能 