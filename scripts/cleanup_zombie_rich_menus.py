import os
import sys
import asyncio

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.rich_menu_manager import RichMenuManager
from app.config.linebot_config import LineBotConfig
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """
    Connects to LINE and cleans up Rich Menus that exist but have no associated image.
    """
    LineBotConfig.load_config()
    if not LineBotConfig.LINE_CHANNEL_ACCESS_TOKEN or not LineBotConfig.LINE_CHANNEL_SECRET:
        logging.error("LINE credentials are not configured. Please check your config.env file.")
        return

    manager = RichMenuManager()
    
    logging.info("Fetching all Rich Menus from LINE...")
    all_menus = manager.get_rich_menu_list()

    if not all_menus:
        logging.info("No Rich Menus found on this account.")
        return

    logging.info(f"Found {len(all_menus)} Rich Menus. Checking each one for a valid image...")

    zombie_menus = []
    for menu in all_menus:
        menu_id = menu.get("richMenuId")
        menu_name = menu.get("name", "N/A")
        
        logging.info(f"  - Checking menu '{menu_name}' ({menu_id})...")
        
        has_image = manager.get_rich_menu_image(menu_id)
        
        if not has_image:
            logging.warning(f"    - ZOMBIE DETECTED: Menu '{menu_name}' ({menu_id}) has no image.")
            zombie_menus.append(menu_id)
        else:
            logging.info(f"    - OK: Menu '{menu_name}' ({menu_id}) has an image.")

    if not zombie_menus:
        logging.info("Congratulations! No zombie Rich Menus found.")
        return

    logging.info(f"Found {len(zombie_menus)} zombie Rich Menus. Deleting them now...")

    deleted_count = 0
    for menu_id in zombie_menus:
        try:
            manager.delete_rich_menu(menu_id)
            logging.info(f"  - Deleted zombie menu: {menu_id}")
            deleted_count += 1
        except Exception as e:
            logging.error(f"  - FAILED to delete zombie menu: {menu_id}. Reason: {e}")

    logging.info(f"Cleanup complete. Deleted {deleted_count} of {len(zombie_menus)} zombie menus.")

if __name__ == "__main__":
    asyncio.run(main()) 