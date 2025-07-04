# 干支查詢微服務

專門處理時間戳到干支轉換的獨立 FastAPI 服務，**支援直接連接您的完整時間資料庫**。

## 🌟 主要特色

- **資料庫整合**：直接連接您的 PostgreSQL 時間資料庫，使用與主服務相同的準確數據
- **多重回退機制**：資料庫 → 本地數據文件 → 算法計算
- **高性能**：本地服務調用，延遲 1-5ms
- **容錯設計**：多層錯誤處理，確保服務穩定性
- **RESTful API**：標準 HTTP 接口，易於集成

## 📦 安裝和運行

### 1. 安裝依賴

```bash
cd ganzhi-service
pip install -r requirements.txt
```

### 2. 配置資料庫連接

**方法一：環境變數**
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ziwei"
```

**方法二：.env 文件**
```bash
# 創建 .env 文件
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ziwei" > .env
```

### 3. 啟動服務

```bash
python main.py
```

服務將在 `http://127.0.0.1:8001` 啟動

## 🔌 API 接口

### 基本資訊

```bash
# 服務狀態
GET http://127.0.0.1:8001/

# 健康檢查
GET http://127.0.0.1:8001/health

# 詳細資訊
GET http://127.0.0.1:8001/info
```

### 干支查詢

```bash
GET http://127.0.0.1:8001/ganzhi?ts=2025-07-03 14:30:00&timezone_offset=8
```

**參數說明：**
- `ts`: 時間戳（必填）
  - 支援格式：`YYYY-MM-DD HH:MM:SS`、`YYYY-MM-DD HH:MM`、ISO 8601 等
- `timezone_offset`: 時區偏移小時（可選，默認 +8）

**回應範例：**
```json
{
  "success": true,
  "timestamp": "2025-07-03T14:30:00+08:00",
  "timezone": "+08:00",
  "year_ganzhi": "乙巳",
  "month_ganzhi": "壬午",
  "day_ganzhi": "癸酉",
  "hour_ganzhi": "辛酉",
  "minute_ganzhi": "己未",
  "solar_term": "夏至",
  "lunar_year": "乙巳",
  "lunar_month": "六月",
  "lunar_day": "初八",
  "data_source": "database"
}
```

## 🗄️ 數據來源優先級

### 1. 資料庫模式（最推薦）
- 直接連接您的 PostgreSQL 時間資料庫
- 使用與主服務相同的 `calendar_data` 資料表
- 提供最高準確性的干支計算

### 2. 本地數據文件模式
如果無法連接資料庫，服務會嘗試加載本地數據文件：

```
ganzhi-service/data/
├── complete_ganzhi_data.json      # 優先級最高
├── lunar_calendar_data.json       # 次優先級
└── 節氣農曆干支數據.json           # 第三優先級
```

**數據文件格式範例：**
```json
{
  "2025-07-03 14:00:00": {
    "year_ganzhi": "乙巳",
    "month_ganzhi": "壬午",
    "day_ganzhi": "癸酉",
    "hour_ganzhi": "辛酉",
    "lunar_year": "乙巳",
    "lunar_month": "六月",
    "lunar_day": "初八"
  }
}
```

### 3. 算法計算模式（備用）
- 當無法取得資料庫或本地數據時啟用
- 使用簡化算法提供基本干支計算
- 適合測試和開發環境

## 🔧 主服務集成

在主服務中使用干支查詢微服務：

```python
from app.services.ganzhi_service import GanzhiService

# 初始化服務
ganzhi_service = GanzhiService()

# 查詢干支信息
result = await ganzhi_service.get_ganzhi_with_fallback(
    year=2025, month=7, day=3, hour=14, minute=30
)

print(result["day_ganzhi"])  # 癸酉
```

## 📊 服務監控

### 檢查數據來源
```bash
curl http://127.0.0.1:8001/info
```

**回應包含：**
- `database_connected`: 是否成功連接資料庫
- `data_records`: 資料庫中的記錄數量
- `data_source`: 當前使用的數據來源（database/file/algorithm）

### 健康檢查
```bash
curl http://127.0.0.1:8001/health
```

## ⚡ 性能指標

- **本地服務調用**：1-5ms 延遲
- **資料庫查詢**：O(1) 複雜度（索引優化）
- **內存佔用**：<50MB（無數據緩存時）
- **並發處理**：支援多個同時請求

## 🚀 部署建議

### 開發環境
```bash
# 與主服務在同一台機器
python main.py  # 端口 8001
```

### 生產環境
```bash
# 使用 uvicorn 部署
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🔍 故障排除

### 常見問題

1. **資料庫連接失敗**
   ```
   ERROR: 資料庫連接失敗，切換到文件模式
   ```
   - 檢查資料庫是否運行
   - 確認 `DATABASE_URL` 環境變數正確
   - 驗證資料庫用戶權限

2. **找不到數據**
   ```
   WARNING: 資料庫中找不到記錄，回退到算法計算
   ```
   - 檢查資料庫中是否有對應日期的數據
   - 確認 `calendar_data` 資料表存在且有數據

3. **服務無法啟動**
   - 確認端口 8001 未被佔用
   - 檢查依賴是否正確安裝

### 偵錯模式
```bash
# 啟用詳細日誌
export LOG_LEVEL=debug
python main.py
```

## 🤝 與紫微斗數系統集成

此微服務是紫微斗數 LINE Bot 系統的一部分，專門負責：

1. **時間計算解耦**：將複雜的時間轉換邏輯獨立出來
2. **準確性提升**：使用完整的時間資料庫確保計算準確
3. **系統擴展**：支援未來的分散式部署和負載均衡
4. **維護簡化**：時間計算邏輯可獨立測試和更新

---

**技術架構**：FastAPI + SQLAlchemy + PostgreSQL  
**適用場景**：紫微斗數排盤、占卜系統、農曆轉換應用 