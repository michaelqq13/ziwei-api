# Railway 部署步驟

## 1. 安裝 Railway CLI
```bash
npm install -g @railway/cli
```

## 2. 登入 Railway
```bash
railway login
```

## 3. 初始化項目
```bash
cd ganzhi-service
railway init
```

## 4. 設置環境變數
```bash
# 使用與主服務相同的資料庫
railway variables set DATABASE_URL="postgresql://postgres:XXX@XXX.railway.app:5432/railway"
```

## 5. 部署
```bash
railway up
```

## 6. 獲取服務 URL
```bash
railway domain
```

## 7. 更新主服務環境變數
在主服務的 Railway 項目中設置：
```bash
railway variables set GANZHI_SERVICE_URL="https://your-ganzhi-service.railway.app"
```

## 測試
```bash
# 測試微服務
curl https://your-ganzhi-service.railway.app/health

# 測試干支查詢
curl "https://your-ganzhi-service.railway.app/ganzhi?ts=2025-07-03%2014:30:00&timezone_offset=8"
``` 