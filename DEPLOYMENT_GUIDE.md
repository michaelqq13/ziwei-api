# LINE Bot 紫微斗數占卜系統 - 部署指南

## 🚀 快速部署

### 1. 環境配置

創建 `.env` 文件並添加以下配置：

```bash
# LINE Bot 配置
LINE_CHANNEL_SECRET=611969a2b460d46e71648a2c3a6d54fb
LINE_CHANNEL_ACCESS_TOKEN=AjXjeHlVLV4/wFDEcERkXK2YL7ncFQqlxNQJ29wm6aHcbYdMbEvqf9dZZHCckzaPSYpkO+WKOV6KUFVvMwW85dJl+KDV95sn3VIBphhItS3F5veXYAgZqhzzJcNw5FpnJjqGcorKhue0I26XxJMX2AdB04t89/1O/w1cDnyilFU=

# 管理員配置
ADMIN_SECRET_PHRASE=紫微斗數管理
ADMIN_PASSWORD=admin123

# 數據庫配置
DATABASE_URL=sqlite:///./app.db

# 其他配置
DEBUG=False
```

### 2. 啟動服務

#### 本地開發
```bash
# 設置環境變數
export LINE_CHANNEL_SECRET="611969a2b460d46e71648a2c3a6d54fb"
export LINE_CHANNEL_ACCESS_TOKEN="AjXjeHlVLV4/wFDEcERkXK2YL7ncFQqlxNQJ29wm6aHcbYdMbEvqf9dZZHCckzaPSYpkO+WKOV6KUFVvMwW85dJl+KDV95sn3VIBphhItS3F5veXYAgZqhzzJcNw5FpnJjqGcorKhue0I26XxJMX2AdB04t89/1O/w1cDnyilFU="

# 啟動服務器
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生產環境
```bash
# 使用 Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或直接使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Webhook 設定

#### 使用 ngrok (本地測試)
```bash
# 安裝 ngrok
brew install ngrok  # macOS
# 或從官網下載: https://ngrok.com/

# 啟動 ngrok
ngrok http 8000

# 複製 https URL，例如: https://abc123.ngrok.io
```

#### LINE Developers Console 設定
1. 登入 [LINE Developers Console](https://developers.line.biz/)
2. 選擇你的 Bot 頻道
3. 在 "Messaging API" 頁面中：
   - **Webhook URL**: `https://your-domain.com/webhook` 或 `https://abc123.ngrok.io/webhook`
   - **Use webhook**: 啟用
   - **Auto-reply messages**: 停用
   - **Greeting messages**: 可選擇啟用

### 4. 功能測試

運行測試腳本確認所有功能正常：
```bash
python test_linebot_features.py
```

## 📋 系統資訊

### Bot 資訊
- **Bot 名稱**: Guide.with.stars
- **Bot ID**: Ud6420eb8d2381617797ad740d637981c
- **Channel Secret**: 611969a2b460d46e71648a2c3a6d54fb

### 主要功能
1. **🔮 占卜功能**
   - 免費會員每週一次
   - 基於當下時間和性別起盤
   - 提供運勢分析和四化解釋

2. **📊 個人運勢**
   - 需綁定個人命盤
   - 付費會員功能
   - 流年/流月/流日運勢查詢

3. **👤 會員制度**
   - 免費會員：基本占卜
   - 付費會員：完整功能
   - 管理員：無限制使用

4. **🔧 管理員功能**
   - 用戶管理
   - 系統統計
   - 權限管理

### 管理員認證
- **密語**: 紫微斗數管理
- **密碼**: admin123

## 🛠️ 維護指南

### 日誌監控
```bash
# 查看應用日誌
tail -f app.log

# 查看系統資源使用
htop
```

### 數據庫備份
```bash
# 備份 SQLite 數據庫
cp app.db app_backup_$(date +%Y%m%d).db
```

### 更新部署
```bash
# 拉取最新代碼
git pull origin main

# 重啟服務
# 如果使用 systemd
sudo systemctl restart linebot-service

# 如果使用 PM2
pm2 restart linebot
```

## 🔧 故障排除

### 常見問題

1. **Webhook 連接失敗**
   - 檢查防火牆設定
   - 確認 URL 可從外部訪問
   - 檢查 SSL 憑證

2. **Token 錯誤**
   - 確認 Channel Access Token 正確
   - 檢查 Channel Secret 設定

3. **數據庫錯誤**
   - 檢查數據庫文件權限
   - 確認數據庫連接字符串

### 調試模式
```bash
# 啟用調試模式
export DEBUG=True
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📈 性能優化

### 建議配置
- **CPU**: 2核心以上
- **RAM**: 2GB 以上
- **磁盤**: 10GB 以上
- **網路**: 穩定的網路連接

### 擴展選項
- 使用 Redis 做會話存儲
- 使用 PostgreSQL 替代 SQLite
- 添加負載均衡器
- 實施 CDN 加速

## 🔐 安全注意事項

1. **環境變數保護**
   - 不要將 `.env` 文件提交到版本控制
   - 使用強密碼和定期更換

2. **HTTPS 部署**
   - 生產環境必須使用 HTTPS
   - 定期更新 SSL 憑證

3. **訪問控制**
   - 限制管理員功能訪問
   - 實施速率限制

## 📞 支援聯絡

如有任何問題，請參考：
- `LINEBOT_USAGE_GUIDE.md` - 使用指南
- `LINEBOT_IMPLEMENTATION_SUMMARY.md` - 實現總結
- 或聯繫開發團隊 