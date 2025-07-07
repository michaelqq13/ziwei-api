#!/usr/bin/env python3
"""
強制 Railway 重新部署腳本
用於確保最新的程式碼和環境變數配置生效
"""

import os
import subprocess
import datetime
import json

def check_git_status():
    """檢查 Git 狀態"""
    print("🔍 檢查 Git 狀態...")
    
    try:
        # 檢查是否有未提交的變更
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  發現未提交的變更:")
            print(result.stdout)
            return False
        else:
            print("✅ 工作目錄乾淨，無未提交變更")
            return True
            
    except Exception as e:
        print(f"❌ 檢查 Git 狀態失敗: {e}")
        return False

def get_current_commit():
    """獲取當前 commit 資訊"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True)
        commit_hash = result.stdout.strip()[:8]
        
        result = subprocess.run(['git', 'log', '-1', '--pretty=format:%s'], 
                              capture_output=True, text=True)
        commit_message = result.stdout.strip()
        
        return commit_hash, commit_message
    except Exception as e:
        print(f"❌ 獲取 commit 資訊失敗: {e}")
        return None, None

def force_deploy_trigger():
    """觸發強制部署"""
    print("\n🚀 強制觸發 Railway 重新部署...")
    
    # 方法 1: 創建一個小的變更觸發部署
    timestamp = datetime.datetime.now().isoformat()
    deploy_trigger_file = "railway_deploy_trigger.txt"
    
    try:
        with open(deploy_trigger_file, "w") as f:
            f.write(f"Last deploy trigger: {timestamp}\n")
            f.write("This file is used to force Railway redeployment\n")
            f.write("Safe to delete after deployment\n")
        
        print(f"✅ 創建部署觸發檔案: {deploy_trigger_file}")
        
        # 提交變更
        subprocess.run(['git', 'add', deploy_trigger_file], check=True)
        subprocess.run(['git', 'commit', '-m', f'Force Railway redeploy - {timestamp}'], check=True)
        
        print("✅ 已提交觸發變更")
        return True
        
    except Exception as e:
        print(f"❌ 創建部署觸發失敗: {e}")
        return False

def push_to_remote():
    """推送到遠端倉庫"""
    print("\n📤 推送到遠端倉庫...")
    
    try:
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 成功推送到遠端倉庫")
            print("🔄 Railway 應該會自動開始重新部署")
            return True
        else:
            print(f"❌ 推送失敗: {result.stderr}")
            
            # 嘗試其他分支名稱
            result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 成功推送到遠端倉庫 (master 分支)")
                return True
            else:
                print(f"❌ 推送到 master 分支也失敗: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ 推送過程發生錯誤: {e}")
        return False

def generate_deployment_checklist():
    """生成部署檢查清單"""
    checklist = {
        "timestamp": datetime.datetime.now().isoformat(),
        "railway_setup_steps": [
            "1. 登入 Railway Dashboard: https://railway.app/dashboard",
            "2. 進入專案設定",
            "3. 點擊 'Variables' 標籤",
            "4. 添加環境變數:",
            "   - 變數名: LINE_CHANNEL_SECRET",
            "   - 變數值: 611969a2b460d46e71648a2c3a6d54fb",
            "   - 變數名: LINE_CHANNEL_ACCESS_TOKEN", 
            "   - 變數值: [完整的 access token]",
            "5. 儲存變數設定",
            "6. 等待自動重新部署，或手動點擊 'Redeploy'",
            "7. 監控 'Logs' 標籤中的部署進度",
            "8. 確認看到 '✅ LINE_CHANNEL_SECRET 已設定' 訊息"
        ],
        "verification_steps": [
            "1. 檢查 Railway Logs 是否顯示配置成功",
            "2. 測試 LINE Bot 是否能正常回應",
            "3. 確認不再出現 HTTP 500 錯誤",
            "4. 監控錯誤日誌是否消失"
        ]
    }
    
    with open("railway_deployment_checklist.json", "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)
    
    print("📋 部署檢查清單已儲存至: railway_deployment_checklist.json")

def main():
    print("🚀 Railway 強制重新部署工具")
    print("=" * 50)
    
    # 檢查 Git 狀態
    is_clean = check_git_status()
    
    # 獲取當前 commit 資訊
    commit_hash, commit_message = get_current_commit()
    if commit_hash:
        print(f"📝 當前 commit: {commit_hash} - {commit_message}")
    
    print("\n" + "=" * 50)
    print("📋 強制部署選項:")
    print("1. 自動觸發部署 (推薦)")
    print("2. 手動設定指導")
    print("3. 生成檢查清單")
    
    choice = input("\n請選擇操作 (1-3): ").strip()
    
    if choice == "1":
        if force_deploy_trigger():
            if push_to_remote():
                print("\n✅ 強制部署觸發成功！")
                print("⏰ 請等待 2-3 分鐘，然後檢查 Railway Logs")
                print("🔍 尋找以下成功訊息:")
                print("   - ✅ LINE_CHANNEL_SECRET 已設定")
                print("   - ✅ LINE 簽名驗證成功")
            else:
                print("\n❌ 推送失敗，請手動推送或檢查 Git 設定")
    
    elif choice == "2":
        print("\n📖 手動設定 Railway 環境變數:")
        print("1. 前往 Railway Dashboard")
        print("2. Variables 標籤添加:")
        print("   LINE_CHANNEL_SECRET = 611969a2b460d46e71648a2c3a6d54fb")
        print("3. 等待自動重新部署")
        
    elif choice == "3":
        generate_deployment_checklist()
        print("✅ 檢查清單已生成")
    
    else:
        print("❌ 無效選擇")
    
    print("\n🎯 關鍵提醒:")
    print("✅ 確保 Railway 環境變數正確設定")
    print("✅ 監控部署日誌直到看到成功訊息")
    print("✅ 測試 LINE Bot 功能確認修復")

if __name__ == "__main__":
    main() 