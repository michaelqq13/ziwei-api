"""
LINE Bot 配置文件
包含所有 LINE Bot 相關的設定和常數
"""
import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

# 設置日誌記錄器
logger = logging.getLogger(__name__)

# 改進的環境變數載入機制
def load_environment_variables():
    """載入環境變數，支援本地開發和生產環境"""
    # 1. 首先嘗試載入 .env 檔案（如果存在）
    if os.path.exists(".env"):
        load_dotenv(".env")
        logger.info("已載入 .env 檔案")
    
    # 2. 嘗試載入 config.env 檔案（如果存在）
    if os.path.exists("config.env"):
        load_dotenv("config.env")
        logger.info("已載入 config.env 檔案")
    
    # 3. 記錄環境變數載入狀態
    line_secret = os.getenv("LINE_CHANNEL_SECRET")
    line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    logger.info(f"LINE_CHANNEL_SECRET 狀態: {'已設定' if line_secret and line_secret != 'your_channel_secret_here' else '未設定或為預設值'}")
    logger.info(f"LINE_CHANNEL_ACCESS_TOKEN 狀態: {'已設定' if line_token and line_token != 'your_channel_access_token_here' else '未設定或為預設值'}")
    
    return line_secret, line_token

# 載入環境變數
load_environment_variables()

class LineBotConfig:
    """LINE Bot 配置類"""
    
    # ========== LINE Platform 設定 ==========
    CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "your_channel_access_token_here")
    CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "your_channel_secret_here")
    
    # 在類初始化時進行驗證和日誌記錄
    @classmethod
    def _validate_line_config(cls):
        """驗證 LINE 配置並記錄詳細信息"""
        logger.info("=== LINE Bot 配置驗證 ===")
        
        # 檢查 Channel Secret
        if cls.CHANNEL_SECRET == "your_channel_secret_here":
            logger.error("❌ LINE_CHANNEL_SECRET 未正確設定，使用預設值")
            logger.error("請在生產環境中設定正確的 LINE_CHANNEL_SECRET 環境變數")
        else:
            logger.info(f"✅ LINE_CHANNEL_SECRET 已設定: {cls.CHANNEL_SECRET[:8]}...")
        
        # 檢查 Channel Access Token
        if cls.CHANNEL_ACCESS_TOKEN == "your_channel_access_token_here":
            logger.error("❌ LINE_CHANNEL_ACCESS_TOKEN 未正確設定，使用預設值")
        else:
            logger.info(f"✅ LINE_CHANNEL_ACCESS_TOKEN 已設定: {cls.CHANNEL_ACCESS_TOKEN[:20]}...")
        
        logger.info("========================")
        
        return cls.CHANNEL_SECRET != "your_channel_secret_here"
    
    # ========== 管理員設定 ==========
    ADMIN_SECRET_PHRASE = "星空紫微"  # 管理員密語
    ADMIN_PASSWORD = "admin2025"     # 管理員密碼
    
    # ========== 會員制度設定 ==========
    class MembershipLevel:
        FREE = "free"           # 免費會員
        PREMIUM = "premium"     # 付費會員  
        ADMIN = "admin"         # 管理員
    
    # 免費會員限制
    FREE_DIVINATION_WEEKLY_LIMIT = 1  # 每週占卜次數限制
    
    # ========== Rich Menu 設定 ==========
    RICH_MENU_WIDTH = 2500
    RICH_MENU_HEIGHT = 1686
    
    # 最終選單按鈕配置（根據用戶選擇的元素）
    # 選擇的元素：太陽(S1)、火箭(R1)、土星(C1)、幽浮(C20)
    
    # 一般會員按鈕配置 (6個按鈕)
    MEMBER_RICH_MENU_BUTTONS = [
        {
            "name": "weekly_divination",
            "text": "本週占卜", 
            "action_text": "本週占卜",
            "x": 625,   # 左上
            "y": 562,
            "size": 200,
            "color": (200, 150, 200),  # 紫色調，配合水晶球
            "planet": "水晶球",
            "crystal_ball_style": "classic",  # 經典水晶球
            "icon": "🔮"
        },
        {
            "name": "yearly_fortune", 
            "text": "流年運勢",
            "action_text": "流年運勢", 
            "x": 625,   # 左下
            "y": 1124,
            "size": 180,
            "color": (255, 140, 60),  # 橙色
            "planet": "火箭",
            "rocket_style": "classic",  # R1 - 經典火箭
            "icon": "🚀"
        },
        {
            "name": "monthly_fortune",
            "text": "流月運勢", 
            "action_text": "流月運勢",
            "x": 1250,  # 中上
            "y": 562,
            "size": 170,
            "color": (255, 215, 100),  # 土星色
            "planet": "土星",
            "saturn_style": "classic",  # C1 - 土星
            "icon": "🪐"
        },
        {
            "name": "daily_fortune",
            "text": "流日運勢",
            "action_text": "流日運勢", 
            "x": 1250,  # 中下
            "y": 1124,
            "size": 160,
            "color": (180, 180, 180),  # 銀灰色
            "planet": "幽浮",
            "ufo_style": "classic_with_beam",  # C20 - 帶白色光束幽浮
            "icon": "🛸"
        },
        {
            "name": "chart_binding",
            "text": "命盤綁定",
            "action_text": "命盤綁定",
            "x": 1875,  # 右上
            "y": 562,
            "size": 150,
            "color": (150, 200, 255),  # 藍色
            "planet": "地球",
            "earth_style": "classic",  # 經典地球
            "icon": "🌍"
        },
        {
            "name": "member_info",
            "text": "會員資訊",
            "action_text": "會員資訊",
            "x": 1875,  # 右下
            "y": 1124,
            "size": 140,
            "color": (200, 200, 200),  # 月球色
            "planet": "月球",
            "moon_style": "classic",  # 經典月球
            "icon": "🌙"
        }
    ]
    
    # 管理員按鈕配置 (7個按鈕)
    ADMIN_RICH_MENU_BUTTONS = [
        {
            "name": "weekly_divination",
            "text": "本週占卜", 
            "action_text": "本週占卜",
            "x": 625,   # 左上
            "y": 421,
            "size": 200,
            "color": (200, 150, 200),  # 紫色調，配合水晶球
            "planet": "水晶球",
            "crystal_ball_style": "classic",  # 經典水晶球
            "icon": "🔮"
        },
        {
            "name": "yearly_fortune", 
            "text": "流年運勢",
            "action_text": "流年運勢", 
            "x": 625,   # 左下
            "y": 1265,
            "size": 180,
            "color": (255, 140, 60),  # 橙色
            "planet": "火箭",
            "rocket_style": "classic",  # R1 - 經典火箭
            "icon": "🚀"
        },
        {
            "name": "monthly_fortune",
            "text": "流月運勢", 
            "action_text": "流月運勢",
            "x": 1250,  # 中上
            "y": 421,
            "size": 170,
            "color": (255, 215, 100),  # 土星色
            "planet": "土星",
            "saturn_style": "classic",  # C1 - 土星
            "icon": "🪐"
        },
        {
            "name": "daily_fortune",
            "text": "流日運勢",
            "action_text": "流日運勢", 
            "x": 1250,  # 中下
            "y": 1265,
            "size": 160,
            "color": (180, 180, 180),  # 銀灰色
            "planet": "幽浮",
            "ufo_style": "classic_with_beam",  # C20 - 帶白色光束幽浮
            "icon": "🛸"
        },
        {
            "name": "chart_binding",
            "text": "命盤綁定",
            "action_text": "命盤綁定",
            "x": 1875,  # 右上
            "y": 421,
            "size": 150,
            "color": (150, 200, 255),  # 藍色
            "planet": "地球",
            "earth_style": "classic",  # 經典地球
            "icon": "🌍"
        },
        {
            "name": "member_info",
            "text": "會員資訊",
            "action_text": "會員資訊",
            "x": 1875,  # 右中
            "y": 843,
            "size": 140,
            "color": (200, 200, 200),  # 月球色
            "planet": "月球",
            "moon_style": "classic",  # 經典月球
            "icon": "🌙"
        },
        {
            "name": "scheduled_divination",
            "text": "指定時間",
            "action_text": "指定時間占卜",
            "x": 1875,  # 右下
            "y": 1265,
            "size": 130,
            "color": (255, 100, 255),  # 紫色
            "planet": "時鐘",
            "clock_style": "classic",  # 經典時鐘
            "icon": "⏰"
        }
    ]
    
    # 舊版按鈕配置（保留兼容性）
    RICH_MENU_BUTTONS = MEMBER_RICH_MENU_BUTTONS  # 默認使用會員配置
    
    # ========== 占卜系統設定 ==========
    # 分鐘地支對應表 (每10分鐘一個單位，12個時辰)
    MINUTE_DIZHI_MAPPING = {
        # 子時 23:00-01:00
        0: "子", 10: "丑", 20: "寅", 30: "卯", 40: "辰", 50: "巳",
        # 午時等其他時辰會在邏輯中計算
    }
    
    # 四化星順序 (忌、祿、權、科)
    SIHUA_ORDER = ["忌", "祿", "權", "科"]
    
    # ========== 回應訊息模板 ==========
    class Messages:
        # 歡迎訊息
        WELCOME = """✨ 歡迎來到星空紫微斗數 ✨

🔮 占卜功能：根據當下時間為您預測運勢
⭐ 個人運勢：需綁定命盤後查詢流年/流月/流日
👤 會員制度：免費會員每週可占卜一次

請點選下方星球按鈕開始探索您的命運！"""

        # 權限不足
        PERMISSION_DENIED = """❌ 權限不足

此功能需要付費會員才能使用。
如需升級會員，請聯繫管理員。"""

        # 占卜次數用完
        DIVINATION_LIMIT_REACHED = """🔮 本週占卜次數已用完

免費會員每週只能占卜一次。
如需更多次數，請升級為付費會員。"""

        # 需要命盤綁定
        CHART_BINDING_REQUIRED = """⭐ 需要先綁定命盤

此功能需要您的出生資料。
請先點選「命盤綁定」完成設定。"""

        # 系統錯誤
        SYSTEM_ERROR = """🔧 系統暫時無法使用

請稍後再試，或聯繫管理員。"""

    # ========== 資料庫表名 ==========
    class Tables:
        USERS = "linebot_users"
        DIVINATION_HISTORY = "divination_history" 
        CHART_BINDINGS = "chart_bindings"
        MEMBERSHIP = "user_membership"

# 驗證配置
def validate_config():
    """驗證配置是否完整"""
    errors = []
    
    if LineBotConfig.CHANNEL_ACCESS_TOKEN == "your_channel_access_token_here":
        errors.append("請設定 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
    
    if LineBotConfig.CHANNEL_SECRET == "your_channel_secret_here":
        errors.append("請設定 LINE_CHANNEL_SECRET 環境變數")
    
    if errors:
        raise ValueError("配置錯誤：" + ", ".join(errors))
    
    return True

# 導出配置
__all__ = ["LineBotConfig", "validate_config"] 