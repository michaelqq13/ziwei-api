# 🌟 環境變數設定範例

## 📋 基本設定檔案

請將以下內容複製到您的 `config.env` 或 `.env` 文件中：

```bash
# =================================
# 🌟 Purple Star Astrology API 環境變數
# =================================

# ===============================
# LINE Bot 設定
# ===============================
LINE_CHANNEL_ID=2007286218
LINE_CHANNEL_SECRET=611969a2b460d46e71648a2c3a6d54fb
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token

# ===============================
# API 基本設定
# ===============================
API_BASE_URL=http://localhost:8000

# ===============================
# 🔒 安全設定
# ===============================

# CORS 和主機限制
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://yourdomain.com

# 管理員安全設定
ADMIN_IP_WHITELIST=127.0.0.1,localhost,::1
ADMIN_TEST_KEY=secure-admin-test-key-2025-change-me
ADMIN_INIT_SECRET=secure-admin-init-secret-2025-change-me

# LINE 安全設定
ENABLE_LINE_IP_CHECK=false

# ===============================
# 數據庫設定
# ===============================
DATABASE_URL=sqlite:///./ziwei.db

# ===============================
# 可選設定
# ===============================
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
```

## 🔧 設定說明

### LINE Bot 設定
- `LINE_CHANNEL_ID`: LINE 頻道 ID
- `LINE_CHANNEL_SECRET`: LINE 頻道密鑰 (已確認: 611969a2b460d46e71648a2c3a6d54fb)
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE 頻道存取權杖

### 安全設定
- `ALLOWED_HOSTS`: 允許的主機名稱
- `ALLOWED_ORIGINS`: 允許的 CORS 來源
- `ADMIN_IP_WHITELIST`: 管理員 IP 白名單
- `ADMIN_TEST_KEY`: 管理員測試密鑰
- `ADMIN_INIT_SECRET`: 管理員初始化密鑰
- `ENABLE_LINE_IP_CHECK`: 是否啟用 LINE IP 檢查

## 🚀 環境別設定

### 開發環境
```bash
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENABLE_LINE_IP_CHECK=false
DATABASE_URL=sqlite:///./ziwei.db
```

### 生產環境
```bash
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ENABLE_LINE_IP_CHECK=true
DATABASE_URL=postgresql://user:password@host:port/database
ADMIN_IP_WHITELIST=your-admin-ip-1,your-admin-ip-2
```

## ⚠️ 安全注意事項

1. **絕對不要將 `.env` 或 `config.env` 提交到版本控制**
2. **生產環境請使用強密碼**
3. **定期更新 API 密鑰**
4. **限制管理員 IP 白名單**
5. **啟用 HTTPS**

## 🧪 測試您的設定

運行以下命令測試環境變數是否正確載入：

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv('config.env')
print('LINE_CHANNEL_SECRET:', '✅ 已設定' if os.getenv('LINE_CHANNEL_SECRET') else '❌ 未設定')
print('ADMIN_TEST_KEY:', '✅ 已設定' if os.getenv('ADMIN_TEST_KEY') else '❌ 未設定')
"
``` 