import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
    RichMenuSize,
    PostbackAction,
    RichMenuSwitchAction,
    URIAction,
)

def main():
    """
    本腳本用於創建一個新的 LINE Rich Menu 並設置為預設。
    它會讀取 .env 檔案中的 LINE CHANNEL ACCESS TOKEN，
    定義 Rich Menu 的佈局和行為，然後上傳圖片並應用它。
    
    新版本：究極混搭方案 - 4按鈕固定式 Rich Menu
    - 會員資訊：個人化功能入口
    - 功能選單：所有功能的總入口 (Flex 控制面板)
    - 本週占卜：主要賣點功能
    - 使用說明：新用戶引導
    """
    # --- 專案路徑設定 ---
    # 將專案根目錄加到 sys.path，以便讀取 config.env
    # 腳本位置: /scripts/set_rich_menu.py -> 專案根目錄: /
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    print(f"Project root added to path: {project_root}")

    # --- 環境變數載入 ---
    env_path = project_root / 'config.env'
    if not env_path.exists():
        print(f"Error: Environment file not found at {env_path}")
        sys.exit(1)
        
    load_dotenv(dotenv_path=env_path)
    print("Environment variables loaded.")

    access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not access_token:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN not found in environment variables.")
        sys.exit(1)

    # --- Rich Menu 定義 ---
    # 究極混搭方案：2500x843 尺寸，4個核心功能按鈕
    rich_menu_to_create = RichMenuRequest(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name="ziwei-ultimate-hybrid-v1",
        chat_bar_text="查看功能",
        areas=[
            # 1. 會員資訊 (最左) - 個人化功能入口
            RichMenuArea(
                bounds=RichMenuBounds(x=201, y=201, width=319, height=363),
                action=PostbackAction(
                    label="會員資訊",
                    data="action=show_member_info",
                    display_text="會員資訊"
                )
            ),
            # 2. 功能選單 (左中) - 所有功能的總入口，觸發 Flex 控制面板
            RichMenuArea(
                bounds=RichMenuBounds(x=800, y=201, width=355, height=363),
                action=PostbackAction(
                    label="功能選單",
                    data="action=show_control_panel",
                    display_text="功能選單"
                )
            ),
            # 3. 本週占卜 (右中) - 主要賣點功能，直接釘選在選單上
            RichMenuArea(
                bounds=RichMenuBounds(x=1398, y=201, width=305, height=363),
                action=PostbackAction(
                    label="本週占卜",
                    data="action=weekly_fortune",
                    display_text="本週占卜"
                )
            ),
            # 4. 使用說明 (最右) - 新用戶引導，減少客服壓力
            RichMenuArea(
                bounds=RichMenuBounds(x=1998, y=201, width=340, height=363),
                action=PostbackAction(
                    label="使用說明",
                    data="action=show_instructions",
                    display_text="使用說明"
                )
            )
        ]
    )

    # --- LINE API 操作 ---
    configuration = Configuration(access_token=access_token)
    
    try:
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api_blob = MessagingApiBlob(api_client)
            
            # 1. 創建 Rich Menu 物件並取得 richMenuId
            print("Creating rich menu object...")
            rich_menu_id = messaging_api.create_rich_menu(
                rich_menu_request=rich_menu_to_create
            ).rich_menu_id
            print(f"Rich menu object created successfully. ID: {rich_menu_id}")

            # 2. 上傳對應的圖片 (使用 requests 手動上傳)
            image_path = project_root / 'richmenu_final.png'
            if not image_path.exists():
                print(f"Error: Rich menu image not found at {image_path}")
                messaging_api.delete_rich_menu(rich_menu_id)
                print(f"Cleaned up rich menu object {rich_menu_id}.")
                sys.exit(1)

            print(f"Uploading rich menu image from {image_path} using requests...")
            
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
                print("Rich menu image uploaded successfully via requests.")
            else:
                print(f"Error uploading image: {upload_response.status_code}")
                print(upload_response.text)
                messaging_api.delete_rich_menu(rich_menu_id)
                print(f"Cleaned up rich menu object {rich_menu_id}.")
                sys.exit(1)


            # 3. 將此 Rich Menu 設為預設
            print("Setting this rich menu as the default for all users...")
            messaging_api.set_default_rich_menu(rich_menu_id)
            print("Successfully set as default rich menu.")
            
            # 4. (可選) 驗證預設 Rich Menu ID
            default_rich_menu_id = messaging_api.get_default_rich_menu_id()
            print(f"Verified default rich menu ID: {default_rich_menu_id.rich_menu_id}")
            if default_rich_menu_id.rich_menu_id == rich_menu_id:
                print("Verification successful!")
            else:
                print("Warning: Verification failed. The default rich menu ID does not match the created one.")

    except Exception as e:
        print(f"An error occurred: {e}")
        # 如果在過程中發生錯誤，可以考慮在這裡加入清理程式碼
        # 例如，如果 rich_menu_id 已創建但後續步驟失敗，可以刪除它
        # if 'rich_menu_id' in locals():
        #     try:
        #         messaging_api.delete_rich_menu(rich_menu_id)
        #         print(f"Cleaned up rich menu object {rich_menu_id} due to an error.")
        #     except Exception as cleanup_e:
        #         print(f"Error during cleanup: {cleanup_e}")

if __name__ == "__main__":
    main() 