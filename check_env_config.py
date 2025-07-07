#!/usr/bin/env python3
"""
環境變數配置檢查腳本
用於驗證 LINE Bot 配置是否正確，特別是在生產環境部署時
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_files():
    """檢查環境配置檔案"""
    logger.info("=== 檢查環境配置檔案 ===")
    
    # 檢查 .env 檔案
    env_file = Path(".env")
    if env_file.exists():
        logger.info(f"✅ 找到 .env 檔案: {env_file.absolute()}")
        load_dotenv(".env")
    else:
        logger.warning("⚠️  未找到 .env 檔案")
    
    # 檢查 config.env 檔案
    config_env_file = Path("config.env")
    if config_env_file.exists():
        logger.info(f"✅ 找到 config.env 檔案: {config_env_file.absolute()}")
        load_dotenv("config.env")
    else:
        logger.warning("⚠️  未找到 config.env 檔案")
    
    return env_file.exists() or config_env_file.exists()

def check_line_config():
    """檢查 LINE Bot 配置"""
    logger.info("=== 檢查 LINE Bot 配置 ===")
    
    # 檢查必要的環境變數
    line_secret = os.getenv("LINE_CHANNEL_SECRET")
    line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    # 預期的正確值
    expected_secret = "611969a2b460d46e71648a2c3a6d54fb"
    
    # 檢查 Channel Secret
    if not line_secret:
        logger.error("❌ LINE_CHANNEL_SECRET 環境變數未設定")
        return False
    elif line_secret == "your_channel_secret_here":
        logger.error("❌ LINE_CHANNEL_SECRET 仍為預設值")
        logger.error(f"   正確值應為: {expected_secret}")
        return False
    elif line_secret == expected_secret:
        logger.info("✅ LINE_CHANNEL_SECRET 設定正確")
    else:
        logger.warning(f"⚠️  LINE_CHANNEL_SECRET 值異常: {line_secret[:8]}...")
        logger.warning(f"   預期值: {expected_secret}")
    
    # 檢查 Access Token
    if not line_token:
        logger.error("❌ LINE_CHANNEL_ACCESS_TOKEN 環境變數未設定")
        return False
    elif line_token == "your_channel_access_token_here":
        logger.error("❌ LINE_CHANNEL_ACCESS_TOKEN 仍為預設值")
        return False
    else:
        logger.info(f"✅ LINE_CHANNEL_ACCESS_TOKEN 已設定: {line_token[:20]}...")
    
    return True

def check_other_config():
    """檢查其他重要配置"""
    logger.info("=== 檢查其他配置 ===")
    
    # 檢查資料庫配置
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info(f"✅ DATABASE_URL 已設定: {database_url[:30]}...")
    else:
        logger.info("ℹ️  DATABASE_URL 未設定，將使用預設的 SQLite")
    
    # 檢查安全配置
    admin_ip_whitelist = os.getenv("ADMIN_IP_WHITELIST")
    if admin_ip_whitelist:
        logger.info(f"✅ ADMIN_IP_WHITELIST 已設定: {admin_ip_whitelist}")
    else:
        logger.info("ℹ️  ADMIN_IP_WHITELIST 未設定")
    
    return True

def generate_railway_env_guide():
    """生成 Railway 環境變數設定指南"""
    logger.info("=== Railway 環境變數設定指南 ===")
    
    expected_secret = "611969a2b460d46e71648a2c3a6d54fb"
    expected_token = "AjXjeHlVLV4/wFDEcERkXK2YL7ncFQqlxNQJ29wm6aHcbYdMbEvqf9dZZHCckzaPSYpkO+WKOV6KUFVvMwW85dJl+KDV95sn3VIBphhItS3F5veXYAgZqhzzJcNw5FpnJjqGcorKhue0I26XxJMX2AdB04t89/1O/w1cDnyilFU="
    
    print("""
📋 Railway 環境變數設定步驟：

1. 登入 Railway Dashboard
2. 選擇您的專案
3. 進入 Variables 標籤
4. 添加以下環境變數：

┌─────────────────────────────────────────────────────────────┐
│ 變數名稱                    │ 變數值                        │
├─────────────────────────────┼───────────────────────────────┤
│ LINE_CHANNEL_SECRET         │ 611969a2b460d46e71648a2c3a6d54fb │
├─────────────────────────────┼───────────────────────────────┤
│ LINE_CHANNEL_ACCESS_TOKEN   │ AjXjeHlVLV4/wFDEcERkXK...    │
│                             │ (完整的 Access Token)         │
└─────────────────────────────────────────────────────────────┘

5. 儲存變數並重新部署應用程式

⚠️  注意事項：
- 不要包含引號
- 確保沒有多餘的空格
- ACCESS_TOKEN 是一長串文字，請完整複製
""")

def test_signature_verification():
    """測試簽名驗證功能"""
    logger.info("=== 測試簽名驗證功能 ===")
    
    try:
        # 導入配置
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.config.linebot_config import LineBotConfig
        from app.api.webhook import verify_line_signature
        
        # 測試資料
        test_body = b'{"events":[]}'
        
        # 使用正確的 secret 計算簽名
        import hmac
        import hashlib
        import base64
        
        correct_secret = "611969a2b460d46e71648a2c3a6d54fb"
        correct_signature = base64.b64encode(
            hmac.new(
                correct_secret.encode('utf-8'),
                test_body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        logger.info(f"測試用正確簽名: {correct_signature}")
        
        # 測試驗證
        result = verify_line_signature(test_body, correct_signature)
        if result:
            logger.info("✅ 簽名驗證測試成功")
        else:
            logger.error("❌ 簽名驗證測試失敗")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 簽名驗證測試錯誤: {e}")
        return False

def main():
    """主函數"""
    print("🔍 LINE Bot 環境配置檢查工具")
    print("=" * 50)
    
    # 檢查步驟
    steps = [
        ("檢查環境配置檔案", check_environment_files),
        ("檢查 LINE Bot 配置", check_line_config),
        ("檢查其他配置", check_other_config),
        ("測試簽名驗證", test_signature_verification)
    ]
    
    all_passed = True
    
    for step_name, step_func in steps:
        logger.info(f"\n🔍 {step_name}")
        try:
            result = step_func()
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {step_name}失敗: {e}")
            all_passed = False
    
    # 生成設定指南
    if not all_passed:
        generate_railway_env_guide()
    
    # 總結
    print("\n" + "=" * 50)
    if all_passed:
        logger.info("✅ 所有檢查通過！配置正確。")
    else:
        logger.error("❌ 部分檢查失敗，請參考上述指南修正配置。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 