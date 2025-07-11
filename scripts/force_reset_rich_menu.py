import logging
import time
import sys
import os

# 將項目根目錄添加到 Python 路徑中
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.utils.driver_view_rich_menu_handler import DriverViewRichMenuHandler
from app.config.linebot_config import LineBotConfig

# 基本日誌設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def force_reset_all_menus():
    """
    強制重置所有駕駛視窗 Rich Menu。
    1. 刪除所有 LINE 平台上的舊選單。
    2. 重新創建所有分頁選單。
    3. 將 'basic' 設為預設選單。
    """
    try:
        logging.info("🚀 開始強制重置所有駕駛視窗 Rich Menu...")
        
        handler = DriverViewRichMenuHandler()
        handler._ensure_manager() # 初始化 manager
        
        # --- 步驟 1: 清理所有在 LINE 上的舊選單 ---
        logging.info("🧹 正在清理所有 LINE 平台上的 Rich Menu...")
        all_menus = handler.manager.get_rich_menu_list()
        if all_menus:
            deleted_count = 0
            for menu in all_menus:
                menu_id = menu.get("richMenuId")
                menu_name = menu.get("name", "")
                logging.info(f"  - 正在刪除選單 '{menu_name}' ({menu_id})...")
                if handler.manager.delete_rich_menu(menu_id):
                    deleted_count += 1
                time.sleep(0.5) # 避免請求過於頻繁
            logging.info(f"✅ 成功刪除 {deleted_count} 個舊選單。")
        else:
            logging.info("✅ LINE 平台上沒有舊選單，無需清理。")

        # --- 步驟 2: 重新創建所有分頁選單 ---
        tabs_to_create = ["basic", "fortune", "advanced"]
        new_menu_ids = {}
        logging.info(f"🎨 正在為 {tabs_to_create} 重新創建選單...")
        
        for tab in tabs_to_create:
            logging.info(f"  - 正在創建 '{tab}' 分頁選單...")
            menu_id = handler.create_tab_rich_menu(tab)
            if menu_id:
                new_menu_ids[tab] = menu_id
                logging.info(f"    ✅ 成功創建 '{tab}' 選單: {menu_id}")
            else:
                logging.error(f"    ❌ 創建 '{tab}' 選單失敗。")
            time.sleep(1) # 給予LINE伺服器處理時間

        if len(new_menu_ids) != len(tabs_to_create):
            logging.critical("❌ 並非所有選單都成功創建，腳本終止。")
            return

        # --- 步驟 3: 將 'basic' 設為預設選單 ---
        logging.info("📌 正在設定 'basic' 為預設選單...")
        basic_menu_id = new_menu_ids.get("basic")
        if basic_menu_id:
            if handler.manager.set_default_rich_menu(basic_menu_id):
                logging.info(f"✅ 成功將 '{basic_menu_id}' 設為預設選單。")
            else:
                logging.error("❌ 設定預設選單失敗。")
        else:
            logging.error("❌ 找不到 'basic' 選單ID，無法設定預設。")
            
        logging.info("🎉 強制重置 Rich Menu 完成！")

    except Exception as e:
        logging.error(f"❌ 執行重置腳本時發生嚴重錯誤: {e}", exc_info=True)

if __name__ == "__main__":
    # 確保環境變數已載入
    if not LineBotConfig.CHANNEL_ACCESS_TOKEN:
        logging.error("LINE_CHANNEL_ACCESS_TOKEN 未設定，請檢查您的 config.env 檔案。")
    else:
        force_reset_all_menus() 