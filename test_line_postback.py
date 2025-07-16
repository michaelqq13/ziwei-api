#!/usr/bin/env python3
"""
模擬 LINE Bot Postback 測試腳本
用於測試功能選單在開發環境中的工作情況
"""

import requests
import json
import time

def test_control_panel_actions():
    """測試控制面板各個功能"""
    
    webhook_url = "http://localhost:8000/webhook"
    
    # 測試用的用戶 ID
    test_user_id = "test_user_12345"
    
    # 要測試的控制面板動作
    test_actions = [
        ("control_panel=basic_divination", "基本占卜"),
        ("control_panel=yearly_fortune", "流年運勢"),
        ("control_panel=monthly_fortune", "流月運勢"),
        ("control_panel=daily_fortune", "流日運勢"),
        ("control_panel=member_upgrade", "會員升級"),
        ("action=show_member_info", "會員資訊"),
        ("action=show_instructions", "使用說明"),
        ("admin_action=time_divination_start", "指定時間占卜"),
    ]
    
    print("🧪 測試 LINE Bot 控制面板功能...")
    print("=" * 60)
    
    for action_data, action_name in test_actions:
        print(f"\n📋 測試: {action_name} ({action_data})")
        
        # 構造模擬的 LINE postback 事件
        postback_event = {
            "destination": "test_destination",
            "events": [
                {
                    "type": "postback",
                    "mode": "active",
                    "timestamp": int(time.time() * 1000),
                    "source": {
                        "type": "user",
                        "userId": test_user_id
                    },
                    "postback": {
                        "data": action_data
                    },
                    "replyToken": f"test_reply_token_{int(time.time())}"
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Line-Signature": "test_signature"  # 在開發模式下會被跳過
        }
        
        try:
            response = requests.post(webhook_url, json=postback_event, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ 請求成功: {response.status_code}")
                try:
                    result = response.json()
                    print(f"   📄 回應: {result}")
                except:
                    print(f"   📄 回應: {response.text}")
            else:
                print(f"   ❌ 請求失敗: {response.status_code}")
                print(f"   📄 錯誤: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 連接錯誤: {e}")
        
        # 等待一秒避免請求過快
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🏁 測試完成！")

def test_message_event():
    """測試文字訊息事件"""
    
    webhook_url = "http://localhost:8000/webhook"
    test_user_id = "test_user_12345"
    
    message_event = {
        "destination": "test_destination",
        "events": [
            {
                "type": "message",
                "mode": "active",
                "timestamp": int(time.time() * 1000),
                "source": {
                    "type": "user",
                    "userId": test_user_id
                },
                "message": {
                    "type": "text",
                    "id": "test_message_id",
                    "text": "功能選單"
                },
                "replyToken": f"test_reply_token_{int(time.time())}"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Line-Signature": "test_signature"
    }
    
    print("🧪 測試文字訊息: '功能選單'")
    
    try:
        response = requests.post(webhook_url, json=message_event, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"   ✅ 請求成功: {response.status_code}")
            try:
                result = response.json()
                print(f"   📄 回應: {result}")
            except:
                print(f"   📄 回應: {response.text}")
        else:
            print(f"   ❌ 請求失敗: {response.status_code}")
            print(f"   📄 錯誤: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 連接錯誤: {e}")

if __name__ == "__main__":
    print("🤖 LINE Bot 功能測試")
    print("確保服務已在 http://localhost:8000 運行")
    
    # 先測試文字訊息
    test_message_event()
    
    print("\n" + "=" * 60)
    
    # 再測試 postback 功能
    test_control_panel_actions() 