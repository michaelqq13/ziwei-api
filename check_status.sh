#!/bin/bash

echo "🔍 紫微斗數系統狀態檢查"
echo "=" * 40

# 檢查前端服務器
echo "📱 前端服務器 (端口3000):"
if lsof -i :3000 >/dev/null 2>&1; then
    echo "✅ 前端服務器正在運行"
    echo "   訪問地址: http://localhost:3000"
else
    echo "❌ 前端服務器未運行"
    echo "   啟動命令: cd ziwei-frontend && npm start"
fi

echo ""

# 檢查後端服務器
echo "🔧 後端服務器 (端口8000):"
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ 後端服務器正在運行"
    echo "   API地址: http://localhost:8000"
    echo "   文檔地址: http://localhost:8000/docs"
else
    echo "❌ 後端服務器未運行"
    echo "   啟動命令: python -m uvicorn app.main:app --reload --port 8000"
fi

echo ""

# 測試API連接
echo "🧪 API連接測試:"
if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
    echo "✅ 後端API可訪問"
else
    echo "❌ 後端API無法訪問"
fi

if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ 前端應用可訪問"
else
    echo "❌ 前端應用無法訪問"
fi

echo ""
echo "=" * 40
echo "💡 Safari連接建議:"
echo "1. 嘗試 http://localhost:3000"
echo "2. 嘗試 http://127.0.0.1:3000"
echo "3. 清除Safari緩存並重啟"
echo "4. 使用Chrome或Firefox測試" 