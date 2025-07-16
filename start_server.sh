#!/bin/bash

# 停止現有服務
echo "🛑 停止現有服務..."
pkill -f uvicorn

# 等待服務完全停止
sleep 2

# 載入環境變數
echo "🔧 載入環境變數..."
if [ -f "config.env" ]; then
    source config.env
    export $(grep -v '^#' config.env | cut -d= -f1)
    
    # 添加開發模式環境變數
    export DEBUG=true
    export SKIP_LINE_SIGNATURE=true
    
    echo "✅ 環境變數載入成功"
    echo "📋 LINE_CHANNEL_SECRET: ${LINE_CHANNEL_SECRET:0:10}..."
    echo "📋 LINE_CHANNEL_ACCESS_TOKEN: ${LINE_CHANNEL_ACCESS_TOKEN:0:20}..."
    echo "🛠️ 開發模式: DEBUG=$DEBUG, SKIP_LINE_SIGNATURE=$SKIP_LINE_SIGNATURE"
else
    echo "❌ 找不到 config.env 檔案"
    exit 1
fi

# 啟動服務
echo "🚀 啟動 uvicorn 服務..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &

# 等待服務啟動
sleep 3

# 檢查服務狀態
if pgrep -f uvicorn > /dev/null; then
    echo "✅ 服務啟動成功"
    echo "📍 服務地址: http://localhost:8000"
    echo "🔗 Webhook URL: http://localhost:8000/webhook"
    echo "🛠️ 開發模式啟用：LINE 簽名驗證已跳過"
else
    echo "❌ 服務啟動失敗"
    exit 1
fi 