#!/usr/bin/env python3
"""
Webhook 調試腳本 - 模擬Line事件處理
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.linebot_config import linebot_config, line_bot_api
from app.utils.linebot_helpers import LineBotHelpers
from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent, Source

def test_reply_message():
    """測試回覆訊息功能"""
    print("=== 回覆訊息測試 ===")
    
    try:
        # 創建測試用的reply token (實際使用中這個會是無效的)
        test_reply_token = "test-reply-token-12345"
        
        # 創建歡迎選單
        helpers = LineBotHelpers()
        welcome_menu = helpers.create_welcome_menu()
        
        # 測試reply_message的API v3調用方式
        print("準備測試 reply_message API...")
        
        # 在API v3中，需要使用ReplyMessageRequest
        reply_request = ReplyMessageRequest(
            reply_token=test_reply_token,
            messages=[welcome_menu]
        )
        
        print(f"Reply request 類型: {type(reply_request)}")
        print(f"Reply token: {reply_request.reply_token}")
        print(f"Messages 長度: {len(reply_request.messages)}")
        print("✅ ReplyMessageRequest 創建成功")
        
        # 注意：實際發送會失敗因為reply_token是無效的，但我們可以看到API調用是否正確
        print("模擬 reply_message 調用...")
        # line_bot_api.reply_message(reply_request)  # 不實際調用，避免錯誤
        
    except Exception as e:
        print(f"❌ 回覆訊息測試失敗: {e}")
        import traceback
        traceback.print_exc()
    print()

def test_message_event_handling():
    """測試訊息事件處理"""
    print("=== 訊息事件處理測試 ===")
    
    try:
        # 模擬創建MessageEvent
        from linebot.v3.webhooks import UserSource
        
        # 創建測試用戶來源
        user_source = UserSource(user_id="test-user-123")
        
        # 創建測試文字訊息
        text_message = TextMessageContent(text="hello")
        
        # 模擬事件處理
        print("模擬文字訊息事件處理...")
        print(f"用戶ID: {user_source.user_id}")
        print(f"訊息內容: {text_message.text}")
        print("✅ 事件處理模擬成功")
        
    except Exception as e:
        print(f"❌ 事件處理測試失敗: {e}")
        import traceback
        traceback.print_exc()
    print()

def check_api_v3_usage():
    """檢查API v3使用方式"""
    print("=== API v3 使用方式檢查 ===")
    
    try:
        from linebot.v3.messaging import ReplyMessageRequest
        print("✅ ReplyMessageRequest 導入成功")
        
        # 檢查line_bot_api的reply_message方法簽名
        import inspect
        reply_method = getattr(line_bot_api, 'reply_message')
        sig = inspect.signature(reply_method)
        print(f"reply_message 方法簽名: {sig}")
        
    except Exception as e:
        print(f"❌ API v3 檢查失敗: {e}")
        import traceback
        traceback.print_exc()
    print()

if __name__ == "__main__":
    test_reply_message()
    test_message_event_handling() 
    check_api_v3_usage()
    print("=== 調試完成 ===") 