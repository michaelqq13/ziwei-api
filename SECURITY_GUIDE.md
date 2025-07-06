# 🔒 API 安全配置指南

## 📋 概述

本指南說明如何正確配置 Purple Star Astrology API 的安全設定，確保生產環境的安全性。

## 🛡️ 已實施的安全措施

### 1. 速率限制 (Rate Limiting)
- **全域限制**: 使用 `slowapi` 實現速率限制
- **端點限制**: 
  - 首頁: 10 次/分鐘
  - 測試端點: 5 次/分鐘  
  - LINE Webhook: 100 次/分鐘
- **用戶限制**: 基於 IP 地址的限制

### 2. CORS 設定
- **限制來源**: 只允許特定域名訪問
- **限制方法**: 只允許 GET, POST, PUT, DELETE
- **預檢快取**: 1 小時快取時間

### 3. 請求大小限制
- **最大請求大小**: 2MB
- **適用方法**: POST, PUT, PATCH

### 4. 安全標頭
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

### 5. LINE Webhook 安全
- **簽名驗證**: 實現完整的 HMAC-SHA256 簽名驗證
- **IP 白名單**: 可選的 LINE 官方 IP 範圍檢查
- **速率限制**: 防止 webhook 濫用

### 6. 可疑請求檢測
- **SQL 注入檢測**: 檢查常見的 SQL 注入模式
- **XSS 檢測**: 檢查跨站腳本攻擊模式
- **路徑遍歷檢測**: 檢查目錄遍歷攻擊
- **可疑 User-Agent**: 檢查自動化工具和爬蟲

### 7. 管理員功能保護
- **IP 白名單**: 管理員功能僅限特定 IP 訪問
- **密鑰驗證**: 管理員操作需要密鑰驗證

## 🔧 環境變數配置

### 必要設定
```bash
# 基本安全設定
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# LINE Bot 設定
LINE_CHANNEL_SECRET=your-line-channel-secret
LINE_CHANNEL_ACCESS_TOKEN=your-line-access-token

# 管理員設定
ADMIN_IP_WHITELIST=your-admin-ip-1,your-admin-ip-2
ADMIN_TEST_KEY=your-secure-admin-test-key
ADMIN_INIT_SECRET=your-secure-admin-init-secret
```

### 可選設定
```bash
# 啟用 LINE IP 檢查（生產環境建議開啟）
ENABLE_LINE_IP_CHECK=true

# 數據庫設定
DATABASE_URL=your-database-url
```

## 🚀 部署安全檢查清單

### 部署前檢查
- [ ] 設定正確的 `ALLOWED_HOSTS` 和 `ALLOWED_ORIGINS`
- [ ] 配置強密碼的 `ADMIN_TEST_KEY` 和 `ADMIN_INIT_SECRET`
- [ ] 設定管理員 IP 白名單 `ADMIN_IP_WHITELIST`
- [ ] 確認 LINE Channel Secret 正確設定
- [ ] 啟用 HTTPS（生產環境必須）

### 部署後檢查
- [ ] 測試速率限制是否正常工作
- [ ] 驗證 CORS 設定是否正確
- [ ] 確認安全標頭是否正確添加
- [ ] 測試 LINE Webhook 簽名驗證
- [ ] 檢查可疑請求是否被正確攔截

## 🔍 監控和日誌

### 安全日誌
- **請求日誌**: 記錄所有 API 請求
- **可疑請求**: 記錄被攔截的可疑請求
- **失敗驗證**: 記錄簽名驗證失敗
- **速率限制**: 記錄被限制的請求

### 監控指標
- API 請求頻率
- 錯誤率統計
- 可疑請求統計
- 用戶訪問模式

## 🛠️ 進階安全配置

### 1. 反向代理設定 (Nginx)
```nginx
# 限制請求大小
client_max_body_size 2M;

# 隱藏服務器信息
server_tokens off;

# 安全標頭
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
```

### 2. 防火牆設定
- 只開放必要的端口 (80, 443)
- 限制管理員 IP 訪問
- 配置 DDoS 防護

### 3. SSL/TLS 設定
- 使用 TLS 1.2 或更高版本
- 配置強密碼套件
- 定期更新 SSL 憑證

## 🚨 安全事件響應

### 發現可疑活動時
1. 檢查安全日誌
2. 分析攻擊模式
3. 更新安全規則
4. 通知相關人員

### 常見攻擊類型
- **SQL 注入**: 檢查數據庫查詢日誌
- **XSS 攻擊**: 檢查輸入驗證
- **DDoS 攻擊**: 檢查流量模式
- **暴力破解**: 檢查登錄嘗試

## 📞 支援和更新

### 定期安全檢查
- 每月檢查依賴套件更新
- 每季度審查安全配置
- 每半年進行滲透測試

### 聯絡方式
如發現安全問題，請立即聯絡開發團隊。

---

**重要提醒**: 安全是一個持續的過程，請定期檢查和更新安全配置。 