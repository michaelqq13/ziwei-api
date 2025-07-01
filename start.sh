#!/bin/bash

# 設置默認端口
if [ -z "$PORT" ]; then
    export PORT=8000
fi

echo "Starting application on port $PORT"

# 運行數據庫遷移
echo "Running database migrations..."
alembic upgrade head

# 啟動應用
echo "Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT 