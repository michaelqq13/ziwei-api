#!/usr/bin/env python3
"""
直接測試webhook處理
"""
import json
import hmac
import hashlib
import base64
import requests
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.linebot_config import linebot_config

def create_line_signature(body: str, channel_secret: str) -> str:
    """創建Line的簽名"""
    signature = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def test_webhook_with_text_message():
    """測試文字訊息webhook"""
    # 創建測試事件
    test_event = {
        "destination": "test",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "test-message-123",
                    "text": "hello",
                    "quoteToken": "test-quote-token"
                },
                "timestamp": 1234567890000,
                "source": {
                    "type": "user",
                    "userId": "test-user-123"
                },
                "replyToken": "test-reply-token-12345",
                "mode": "active"
            }
        ]
    }
    
    body = json.dumps(test_event)
    signature = create_line_signature(body, linebot_config.channel_secret)
    
    print("=== 測試文字訊息Webhook ===")
    print(f"Body: {body}")
    print(f"Signature: {signature}")
    
    # 發送請求到本地webhook
    try:
        response = requests.post(
            "http://localhost:8000/api/linebot/webhook",
            headers={
                "Content-Type": "application/json",
                "X-Line-Signature": signature
            },
            data=body
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook處理成功!")
        else:
            print("❌ Webhook處理失敗!")
            
    except Exception as e:
        print(f"❌ 請求發送失敗: {e}")

def test_webhook_with_follow_event():
    """測試關注事件webhook"""
    test_event = {
        "destination": "test",
        "events": [
            {
                "type": "follow",
                "timestamp": 1234567890000,
                "source": {
                    "type": "user",
                    "userId": "test-user-123"
                },
                "replyToken": "test-reply-token-12345",
                "mode": "active"
            }
        ]
    }
    
    body = json.dumps(test_event)
    signature = create_line_signature(body, linebot_config.channel_secret)
    
    print("\n=== 測試關注事件Webhook ===")
    print(f"Body: {body}")
    print(f"Signature: {signature}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/linebot/webhook",
            headers={
                "Content-Type": "application/json",
                "X-Line-Signature": signature
            },
            data=body
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook處理成功!")
        else:
            print("❌ Webhook處理失敗!")
            
    except Exception as e:
        print(f"❌ 請求發送失敗: {e}")

if __name__ == "__main__":
    test_webhook_with_text_message()
    test_webhook_with_follow_event()
    print("\n=== 測試完成 ===") 