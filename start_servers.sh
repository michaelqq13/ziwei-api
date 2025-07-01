#!/bin/bash

# 紫微斗數排盤系統啟動腳本

echo "🚀 啟動紫微斗數排盤系統..."

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 找不到虛擬環境，請先運行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 檢查前端依賴
if [ ! -d "ziwei-frontend/node_modules" ]; then
    echo "❌ 找不到前端依賴，請先運行: cd ziwei-frontend && npm install"
    exit 1
fi

# 啟動後端服務器
echo "🔧 啟動後端API服務器..."
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 等待後端啟動
sleep 3

# 啟動前端服務器
echo "📱 啟動前端開發服務器..."
cd ziwei-frontend
REACT_APP_API_URL=http://localhost:8000/api npm start &
FRONTEND_PID=$!

echo "✅ 服務器啟動完成！"
echo "📱 前端應用: http://localhost:3000"
echo "🔧 後端API: http://localhost:8000"
echo "📖 API文檔: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服務器"

# 等待用戶中斷
trap "echo '🛑 正在停止服務器...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait 