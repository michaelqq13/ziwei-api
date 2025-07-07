#!/usr/bin/env python3
"""
Railway LINE Webhook 簽名驗證修復腳本
用於診斷和修復 Railway 部署中的 LINE Webhook 簽名驗證問題
"""
import os
import sys
import json
import hmac
import hashlib
import base64
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主修復流程"""
    print("🔧 Railway LINE Webhook 簽名驗證修復工具")
    print("=" * 60)
    
    # 步驟 1: 問題診斷
    print("\n📋 步驟 1: 問題診斷")
    diagnose_problem()
    
    # 步驟 2: 環境變數檢查
    print("\n📋 步驟 2: 環境變數檢查")
    env_status = check_environment_variables()
    
    # 步驟 3: 簽名驗證測試
    print("\n📋 步驟 3: 簽名驗證測試")
    test_signature_verification()
    
    # 步驟 4: 提供解決方案
    print("\n📋 步驟 4: 解決方案指南")
    if not env_status:
        provide_railway_solution()
    else:
        print("✅ 環境變數配置正確，如仍有問題請檢查其他因素")
    
    # 步驟 5: 生成修復報告
    print("\n📋 步驟 5: 生成修復報告")
    generate_fix_report(env_status)

def diagnose_problem():
    """診斷問題"""
    print("🔍 分析 LINE Webhook 簽名驗證問題...")
    
    print("""
📊 常見問題分析:

1. ❌ 環境變數未設定
   - Railway 環境變數中缺少 LINE_CHANNEL_SECRET
   - 應用程式使用預設值導致簽名不匹配

2. ❌ 環境變數值錯誤
   - 包含多餘空格或引號
   - 複製時遺漏部分內容

3. ❌ 配置載入失敗
   - config.env 檔案在生產環境中不可用
   - 環境變數載入機制需要改進

4. ❌ 部署配置問題
   - Railway 專案配置錯誤
   - 重新部署未生效
""")

def check_environment_variables():
    """檢查環境變數配置"""
    print("🔍 檢查環境變數配置...")
    
    # 預期的正確值
    expected_secret = "611969a2b460d46e71648a2c3a6d54fb"
    expected_token_prefix = "AjXjeHlVLV4/wFDEcERk"
    
    # 獲取環境變數
    line_secret = os.getenv("LINE_CHANNEL_SECRET")
    line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    print(f"LINE_CHANNEL_SECRET: {line_secret[:8] + '...' if line_secret else 'None'}")
    print(f"LINE_CHANNEL_ACCESS_TOKEN: {line_token[:20] + '...' if line_token else 'None'}")
    
    # 檢查結果
    secret_ok = line_secret == expected_secret
    token_ok = line_token and line_token.startswith(expected_token_prefix)
    
    if secret_ok and token_ok:
        print("✅ 環境變數配置正確")
        return True
    else:
        print("❌ 環境變數配置有問題")
        if not secret_ok:
            print(f"   - LINE_CHANNEL_SECRET 不正確，應為: {expected_secret}")
        if not token_ok:
            print(f"   - LINE_CHANNEL_ACCESS_TOKEN 不正確或缺失")
        return False

def test_signature_verification():
    """測試簽名驗證"""
    print("🔍 測試簽名驗證功能...")
    
    # 測試資料
    test_body = b'{"events":[],"destination":"test"}'
    correct_secret = "611969a2b460d46e71648a2c3a6d54fb"
    
    # 計算正確簽名
    correct_signature = base64.b64encode(
        hmac.new(
            correct_secret.encode('utf-8'),
            test_body,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    print(f"測試資料: {test_body.decode()}")
    print(f"正確簽名: {correct_signature}")
    
    # 使用當前環境變數測試
    current_secret = os.getenv("LINE_CHANNEL_SECRET", "your_channel_secret_here")
    
    if current_secret == correct_secret:
        print("✅ 當前環境變數可以產生正確簽名")
        return True
    else:
        current_signature = base64.b64encode(
            hmac.new(
                current_secret.encode('utf-8'),
                test_body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        print(f"❌ 當前環境變數產生錯誤簽名: {current_signature}")
        print(f"   使用的 secret: {current_secret[:8]}...")
        return False

def provide_railway_solution():
    """提供 Railway 解決方案"""
    print("🚀 Railway 環境變數設定解決方案:")
    
    print("""
📋 詳細設定步驟:

1. 🌐 登入 Railway Dashboard
   - 網址: https://railway.app/dashboard
   - 使用您的帳號登入

2. 📁 選擇專案
   - 找到您的 LINE Bot 專案
   - 點擊進入專案頁面

3. ⚙️  進入環境變數設定
   - 點擊專案名稱
   - 選擇 "Variables" 標籤

4. ➕ 添加環境變數
   複製以下內容，注意不要包含引號:

   變數名: LINE_CHANNEL_SECRET
   變數值: 611969a2b460d46e71648a2c3a6d54fb

   變數名: LINE_CHANNEL_ACCESS_TOKEN
   變數值: AjXjeHlVLV4/wFDEcERkXK2YL7ncFQqlxNQJ29wm6aHcbYdMbEvqf9dZZHCckzaPSYpkO+WKOV6KUFVvMwW85dJl+KDV95sn3VIBphhItS3F5veXYAgZqhzzJcNw5FpnJjqGcorKhue0I26XxJMX2AdB04t89/1O/w1cDnyilFU=

5. 💾 儲存並重新部署
   - 點擊 "Add" 按鈕
   - Railway 會自動觸發重新部署
   - 等待部署完成 (通常需要 2-3 分鐘)

6. 🔍 驗證修復
   - 查看 "Logs" 標籤
   - 尋找成功訊息: "✅ LINE_CHANNEL_SECRET 已設定"
   - 透過 LINE Bot 發送測試訊息
""")

def generate_fix_report(env_status):
    """生成修復報告"""
    print("📄 生成修復報告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment_status": "OK" if env_status else "FAILED",
        "line_channel_secret": os.getenv("LINE_CHANNEL_SECRET", "NOT_SET")[:8] + "..." if os.getenv("LINE_CHANNEL_SECRET") else "NOT_SET",
        "line_channel_access_token": "SET" if os.getenv("LINE_CHANNEL_ACCESS_TOKEN") else "NOT_SET",
        "recommendations": []
    }
    
    if not env_status:
        report["recommendations"].extend([
            "在 Railway Dashboard 中設定正確的環境變數",
            "確保變數值沒有多餘空格或引號",
            "重新部署應用程式並檢查日誌"
        ])
    else:
        report["recommendations"].extend([
            "環境變數配置正確",
            "如仍有問題，請檢查 LINE Developers Console 設定",
            "監控應用程式日誌以確認簽名驗證成功"
        ])
    
    # 儲存報告
    with open("webhook_fix_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 修復報告已儲存至: webhook_fix_report.json")
    
    # 顯示總結
    print("\n" + "=" * 60)
    print("🎯 修復總結:")
    if env_status:
        print("✅ 環境變數配置正確，簽名驗證應該可以正常工作")
        print("📝 如果仍有問題，請檢查:")
        print("   - LINE Developers Console Webhook URL 設定")
        print("   - 網路連接和防火牆設定")
        print("   - Railway 應用程式部署狀態")
    else:
        print("❌ 需要在 Railway 中設定正確的環境變數")
        print("📝 請按照上述指南設定環境變數後重新部署")
        print("🔄 設定完成後，可重新執行此腳本驗證修復結果")

def create_test_webhook_payload():
    """創建測試用的 webhook 負載"""
    return {
        "destination": "test",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "test-message-id",
                    "text": "test"
                },
                "timestamp": 1234567890000,
                "source": {
                    "type": "user", 
                    "userId": "test-user-id"
                },
                "replyToken": "test-reply-token",
                "mode": "active"
            }
        ]
    }

if __name__ == "__main__":
    try:
        # 載入環境變數
        from dotenv import load_dotenv
        if os.path.exists("config.env"):
            load_dotenv("config.env")
        if os.path.exists(".env"):
            load_dotenv(".env")
        
        main()
        
    except KeyboardInterrupt:
        print("\n⚠️  操作已取消")
        sys.exit(1)
    except Exception as e:
        logger.error(f"修復腳本執行錯誤: {e}")
        sys.exit(1) 