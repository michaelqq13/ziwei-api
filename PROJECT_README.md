# 紫微斗數排盤系統

一個完整的紫微斗數排盤系統，包含後端API和現代化前端界面。

## 🎯 系統特色

### 📊 完整的排盤功能
- ✅ **命宮計算** - 根據生年月日時精確計算命宮位置
- ✅ **十二宮位** - 命宮、財帛、疾厄、遷移、奴僕、官祿、田宅、福德、父母、兄弟、夫妻、子女
- ✅ **身宮計算** - 根據生月日時計算身宮位置
- ✅ **宮干計算** - 根據生年天干確定各宮位天干
- ✅ **主星安放** - 14顆主星（紫微、天機、太陽、武曲、天同、廉貞、天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍）
- ✅ **吉凶星安放** - 28顆星曜（祿存、擎羊、陀羅、天魁、天鉞、左輔、右弼、天馬、文昌、文曲、地空、地劫、紅鸞、天喜等）
- ✅ **四化計算** - 根據生年天干計算化祿、化權、化科、化忌
- ✅ **四化解釋** - 提供詳細的四化現象、心理傾向、可能事件、提示建議

### 🔮 運限計算
- ✅ **大限計算** - 十年運限，根據五行局和陰陽確定順逆行
- ✅ **小限計算** - 一年運限，根據生年地支三合墓庫對沖確定起始位置
- ✅ **流年計算** - 根據當前年份地支確定流年命宮
- ✅ **流月計算** - 根據農曆月份計算流月位置
- ✅ **流日計算** - 根據流月位置計算流日分布

### 🌟 技術架構
- **後端**: Python + FastAPI + SQLite
- **前端**: React + TypeScript + Tailwind CSS
- **響應式設計**: 手機友善優先
- **API文檔**: 自動生成的OpenAPI/Swagger文檔

## 🚀 快速開始

### 方法一：使用啟動腳本（推薦）
```bash
# 確保已安裝依賴
pip install -r requirements.txt
cd ziwei-frontend && npm install && cd ..

# 一鍵啟動前後端
./start_servers.sh
```

### 方法二：分別啟動

#### 啟動後端API
```bash
# 激活虛擬環境
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動API服務器
python -m uvicorn app.main:app --reload --port 8000
```

#### 啟動前端應用
```bash
# 進入前端目錄
cd ziwei-frontend

# 安裝依賴
npm install

# 啟動開發服務器
REACT_APP_API_URL=http://localhost:8000/api npm start
```

### 訪問應用
- 📱 **前端應用**: http://localhost:3000
- 🔧 **後端API**: http://localhost:8000
- 📖 **API文檔**: http://localhost:8000/docs

## 📱 使用說明

### 排盤步驟
1. **輸入生辰資料**
   - 選擇西元年月日時分
   - 選擇性別（男/女）
   - 輸入出生地經緯度（預設台北市）

2. **查看命盤**
   - 4x4網格顯示十二宮位
   - 中央空白，外圍十二宮
   - 每宮顯示宮位名稱、地支、星曜列表
   - 四化星曜特殊顏色標記

3. **閱讀解釋**
   - 四化解釋：詳細的現象分析和建議
   - 宮位詳情：點擊宮位查看詳細資訊

## 🎨 界面設計

### 三區塊布局
- **📝 上方**: 生辰資料輸入表單
- **🎯 中間**: 4x4命盤網格（中央4格空白）
- **📖 下方**: 四化解釋和斷語分析

### 響應式特色
- 完全適配手機、平板、桌面
- 觸控友善的操作體驗
- 優雅的色彩搭配和動畫效果

## 📂 項目結構

```
ziwei-api/
├── app/                     # 後端應用
│   ├── api/                # API路由
│   ├── core/               # 核心邏輯
│   ├── data/               # 數據文件
│   ├── models/             # 數據模型
│   ├── repositories/       # 數據訪問層
│   └── utils/              # 工具函數
├── ziwei-frontend/         # 前端應用
│   ├── src/
│   │   ├── components/     # React組件
│   │   ├── services/       # API服務
│   │   ├── types/          # TypeScript類型
│   │   └── App.tsx         # 主應用
│   └── public/             # 靜態文件
├── database.db            # SQLite數據庫
├── requirements.txt       # Python依賴
└── start_servers.sh       # 啟動腳本
```

## 🔧 API端點

### 命盤相關
- `POST /api/chart` - 獲取命盤資料
- `POST /api/chart/four-transformations-explanations` - 四化解釋

### 運限相關
- `POST /api/chart/major-limits` - 大限計算
- `POST /api/chart/minor-limits` - 小限計算
- `POST /api/chart/annual-fortune` - 流年計算
- `POST /api/chart/monthly-fortune` - 流月計算
- `POST /api/chart/daily-fortune` - 流日計算

## 🎯 測試案例

使用以下測試數據驗證系統功能：

```json
{
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "gender": "M",
  "longitude": 121.5654,
  "latitude": 25.0330
}
```

預期結果：
- 命宮：天同在戌宮
- 身宮：在申宮
- 四化：太陽化祿、武曲化權、太陰化科、天同化忌
- 總計28顆星曜正確安放

## 📄 版本歷史

### v1.0.0 (2024-12)
- ✅ 完整的紫微斗數排盤功能
- ✅ 現代化React前端界面
- ✅ 響應式設計，手機友善
- ✅ 四化解釋功能
- ✅ 運限計算（大限、小限、流年、流月、流日）

## 📜 許可證

僅供學習和研究使用，不可用於商業用途。

## ⚠️ 免責聲明

此系統僅供參考，不可盡信。紫微斗數解釋僅為傳統文化學習之用，不應作為人生重大決策的唯一依據。

---

**開發團隊**: 紫微斗數研究小組  
**技術支持**: FastAPI + React 全棧解決方案  
**最後更新**: 2024年12月 