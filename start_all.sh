#!/bin/bash

# 啟動後端
echo "啟動後端服務..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待後端啟動
sleep 3

# 啟動前端
echo "啟動前端服務..."
cd ziwei-frontend
HOST=0.0.0.0 npm start &
FRONTEND_PID=$!

echo "後端 PID: $BACKEND_PID"
echo "前端 PID: $FRONTEND_PID"
echo "服務已啟動！"
echo "電腦訪問: http://localhost:3000"
echo "手機訪問: http://192.168.50.139:3000"
echo "按 Ctrl+C 停止所有服務"

# 等待用戶中斷
wait
