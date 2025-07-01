#!/bin/bash

echo "🌐 正在檢查公網隧道狀態..."
echo "=================================="

# 檢查服務器狀態
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ FastAPI服務器運行正常 (http://localhost:8000)"
else
    echo "❌ FastAPI服務器未運行"
    exit 1
fi

# 檢查localtunnel進程
if pgrep -f "localtunnel" > /dev/null; then
    echo "✅ Localtunnel隧道已啟動"
    
    # 等待隧道完全啟動
    echo "⏳ 等待隧道URL生成..."
    sleep 5
    
    echo ""
    echo "🚀 使用以下方法獲取您的公網URL："
    echo ""
    echo "方法1: 檢查終端輸出"
    echo "   查看localtunnel終端窗口，尋找類似以下的輸出："
    echo "   'your url is: https://xxxxxx.loca.lt'"
    echo ""
    echo "方法2: 或使用以下替代隧道服務："
    echo "   serveo: ssh -R 80:localhost:8000 serveo.net"
    echo "   bore: npx bore 8000"
    echo ""
    echo "⚠️  重要提醒："
    echo "   1. 複製獲得的https URL"
    echo "   2. 在Line Developers Console設置Webhook:"
    echo "      https://your-tunnel-url.loca.lt/api/linebot/webhook"
    echo "   3. 確保啟用 'Use webhook' 選項"
    echo ""
else
    echo "❌ Localtunnel未運行，正在重新啟動..."
    echo "npx localtunnel --port 8000"
fi

echo "🔧 如果遇到問題，可以使用以下替代方案："
echo "   1. 註冊ngrok帳號: https://dashboard.ngrok.com/signup"
echo "   2. 使用serveo: ssh -R 80:localhost:8000 serveo.net"
echo "   3. 使用bore: npx bore 8000" 