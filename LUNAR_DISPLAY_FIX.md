# 農曆顯示問題修正

## 問題描述

在命盤中央區域的農曆顯示存在兩個問題：

1. **農曆格式問題**: 農曆顯示包含了西元年份，應該只顯示月份和日期
2. **排盤時間農曆錯誤**: 排盤時間的農曆日期顯示的是本命盤的農曆日期，應該是當前時間的農曆日期

## 修正方案

### 1. 農曆顯示格式修正

**修正前**:
```
農曆 2024年 十一月 廿八
```

**修正後**:
```
農曆 十一月 廿八
```

### 2. 排盤時間農曆數據修正

**修正前**: 使用本命盤的農曆數據
```javascript
// 使用 chartData.lunar_data（本命盤數據）
農曆 {chartData.lunar_data.month} {chartData.lunar_data.day}
```

**修正後**: 使用當前時間的農曆數據
```javascript
// 使用 currentGanZhi.lunar（當前時間數據）
農曆 {currentGanZhi.lunar.month} {currentGanZhi.lunar.day}
```

### 3. 天干地支數據修正

**修正前**: 排盤時間的年月日時使用本命盤數據，只有分鐘使用當前時間
```javascript
// 混合使用本命盤和當前時間數據
年: chartData.lunar_data.year_gan_zhi
月: chartData.lunar_data.month_gan_zhi
日: chartData.lunar_data.day_gan_zhi
時: chartData.lunar_data.hour_gan_zhi
分: getMinuteGanZhi(currentTime.minute)
```

**修正後**: 排盤時間完全使用當前時間計算的天干地支
```javascript
// 完全使用當前時間數據
年: currentGanZhi.year
月: currentGanZhi.month
日: currentGanZhi.day
時: currentGanZhi.hour
分: currentGanZhi.minute
```

## 技術實現

### 1. 導入時間計算工具
```javascript
import { getCurrentGanZhi } from '../utils/timeCalculator';
```

### 2. 獲取當前時間的完整天干地支信息
```javascript
const [currentGanZhi] = useState(() => getCurrentGanZhi());
```

### 3. 使用當前時間數據
- 農曆日期: `currentGanZhi.lunar.month`, `currentGanZhi.lunar.day`
- 天干地支: `currentGanZhi.year`, `currentGanZhi.month`, `currentGanZhi.day`, `currentGanZhi.hour`, `currentGanZhi.minute`

## 顯示效果

### 本命盤區域
- **標題**: 本命盤（黃色）
- **西元時間**: 使用 `chartData.birth_info` 的出生時間
- **農曆時間**: 只顯示月份和日期，去掉年份
- **天干地支**: 使用本命盤的精確農曆轉換數據

### 排盤時間區域
- **標題**: 排盤時間（青色）
- **西元時間**: 使用當前時間 `currentTime`
- **農曆時間**: 使用當前時間的農曆轉換 `currentGanZhi.lunar`
- **天干地支**: 使用當前時間計算的完整天干地支 `currentGanZhi`

## 數據一致性

修正後確保了：
1. **本命盤數據**: 完全基於用戶輸入的出生時間
2. **排盤時間數據**: 完全基於當前時間（排盤當下）
3. **農曆格式**: 統一只顯示月份和日期
4. **天干地支**: 各自使用對應時間的正確計算結果

## 代碼清理

同時清理了：
- 移除未使用的 `getMinuteGanZhi` 函數
- 修正 `timeCalculator.ts` 中的未使用變數警告
- 確保編譯無警告 