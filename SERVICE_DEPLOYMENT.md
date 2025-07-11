# 星語引路人服務頁面部署說明

## 部署狀態
✅ **已成功部署並公開**

## 訪問地址

### 主要地址（公開可用）
- **服務頁面**: https://web-production-c5424.up.railway.app/service
- **API主頁**: https://web-production-c5424.up.railway.app/

## 頁面內容
- 服務說明與聯絡資訊
- LINE 官方帳號連結
- 聯絡電話與信箱
- 金流平台安全說明

## 自定義域名配置（可選）

如果您想要使用自定義域名（例如: `service.yourcompany.com`），您可以：

### 1. 通過 Railway 控制台配置
1. 登入 [Railway 控制台](https://railway.app)
2. 選擇項目 "hearty-appreciation"
3. 進入 "Settings" > "Domains"
4. 添加自定義域名
5. 按照指示設置 DNS 記錄

### 2. DNS 配置示例
```
CNAME: service.yourcompany.com -> web-production-c5424.up.railway.app
```

## 技術細節
- **框架**: FastAPI
- **響應類型**: HTMLResponse
- **部署平台**: Railway
- **安全特性**: 
  - 速率限制 (10次/分鐘)
  - 安全標頭
  - CORS 保護

## 金流申請相關
此服務頁面滿足以下需求：
- ✅ 公開可訪問的網站
- ✅ 清楚的聯絡資訊
- ✅ 服務說明
- ✅ 安全的HTTPS連接
- ✅ 金流平台安全聲明

## 維護說明
- 服務頁面內容直接嵌入在 `app/main.py` 中
- 修改內容後需要重新部署
- 自動部署已配置（push 到 main 分支即可）

## 聯絡資訊驗證
請確認以下資訊是否正確：
- LINE 官方帳號: https://page.line.me/@087qwiyx
- 聯絡信箱: michaelqq13@gmail.com  
- 聯絡電話: 0988163594

如需修改任何資訊，請編輯 `app/main.py` 中的 HTML 內容。 