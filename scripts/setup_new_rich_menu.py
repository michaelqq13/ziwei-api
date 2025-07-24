#!/usr/bin/env python3
"""
全新 Rich Menu 設定腳本
使用用戶提供的 richmenu_final.png
四個按鈕：會員資訊、功能選單、本週占卜、使用說明
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    RichMenuRequest, RichMenuArea, RichMenuBounds, RichMenuSize,
    PostbackAction
)

def setup_rich_menu():
    """設定全新的 Rich Menu"""
    print("🚀 開始設定全新的 Rich Menu...")
    
    # 載入環境變數
    env_path = project_root / 'config.env'
    if not env_path.exists():
        print(f"❌ 找不到環境檔案: {env_path}")
        return False
        
    load_dotenv(dotenv_path=env_path)
    access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not access_token:
        print("❌ 找不到 LINE_CHANNEL_ACCESS_TOKEN")
        return False

    # Rich Menu 定義 - 四個按鈕配置
    rich_menu_request = RichMenuRequest(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name="ziwei-new-simple-menu",
        chat_bar_text="點擊查看功能",
        areas=[
            # 1. 會員資訊 (最左)
            RichMenuArea(
                bounds=RichMenuBounds(x=201, y=201, width=319, height=363),
                action=PostbackAction(
                    label="會員資訊",
                    data="action=member_info",
                    display_text="查看會員資訊"
                )
            ),
            # 2. 功能選單 (左中) - 顯示功能選單
            RichMenuArea(
                bounds=RichMenuBounds(x=800, y=201, width=355, height=363),
                action=PostbackAction(
                    label="功能選單",
                    data="action=function_menu",
                    display_text="功能選單"
                )
            ),
            # 3. 本週占卜 (右中)
            RichMenuArea(
                bounds=RichMenuBounds(x=1398, y=201, width=305, height=363),
                action=PostbackAction(
                    label="本週占卜",
                    data="action=weekly_divination",
                    display_text="本週占卜"
                )
            ),
            # 4. 使用說明 (最右)
            RichMenuArea(
                bounds=RichMenuBounds(x=1998, y=201, width=340, height=363),
                action=PostbackAction(
                    label="使用說明",
                    data="action=instructions",
                    display_text="使用說明"
                )
            )
        ]
    )

    try:
        configuration = Configuration(access_token=access_token)
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            # 清除現有的 Rich Menu
            print("🧹 清除現有的 Rich Menu...")
            try:
                rich_menu_list = messaging_api.get_rich_menu_list()
                for menu in rich_menu_list.richmenus:
                    print(f"   刪除: {menu.name} ({menu.rich_menu_id})")
                    messaging_api.delete_rich_menu(menu.rich_menu_id)
            except Exception as e:
                print(f"⚠️ 清除選單時出現問題: {e}")

            # 創建新的 Rich Menu
            print("📋 創建新的 Rich Menu...")
            create_response = messaging_api.create_rich_menu(rich_menu_request=rich_menu_request)
            rich_menu_id = create_response.rich_menu_id
            print(f"✅ Rich Menu 創建成功: {rich_menu_id}")

            # 上傳圖片
            image_path = project_root / 'richmenu_final.png'
            if not image_path.exists():
                print(f"❌ 找不到圖片檔案: {image_path}")
                messaging_api.delete_rich_menu(rich_menu_id)
                return False

            print("🖼️ 上傳 Rich Menu 圖片...")
            
            # 使用 requests 上傳圖片
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'image/png'
            }
            
            with open(image_path, 'rb') as f:
                upload_response = requests.post(
                    f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content',
                    headers=headers,
                    data=f.read()
                )

            if upload_response.status_code == 200:
                print("✅ Rich Menu 圖片上傳成功")
            else:
                print(f"❌ 圖片上傳失敗: {upload_response.status_code}")
                print(upload_response.text)
                messaging_api.delete_rich_menu(rich_menu_id)
                return False

            # 設為預設選單
            print("⚙️ 設定為預設 Rich Menu...")
            messaging_api.set_default_rich_menu(rich_menu_id)
            print("✅ 預設 Rich Menu 設定完成")

            print(f"\n🎉 Rich Menu 設定完成！")
            print(f"   Rich Menu ID: {rich_menu_id}")
            print(f"   按鈕配置:")
            print(f"     左1: 會員資訊")
            print(f"     左2: 功能選單")
            print(f"     右1: 本週占卜")
            print(f"     右2: 使用說明")
            
            return True

    except Exception as e:
        print(f"❌ 設定 Rich Menu 失敗: {e}")
        return False

def main():
    """主函數"""
    success = setup_rich_menu()
    if success:
        print("\n✅ Rich Menu 設定完成！")
    else:
        print("\n❌ Rich Menu 設定失敗！")
        sys.exit(1)

if __name__ == "__main__":
    main() 