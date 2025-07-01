"""
LINE Bot 配置文件
包含所有 LINE Bot 相關的設定和常數
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv("config.env")

class LineBotConfig:
    """LINE Bot 配置類"""
    
    # ========== LINE Platform 設定 ==========
    CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "your_channel_access_token_here")
    CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "your_channel_secret_here")
    
    # ========== 管理員設定 ==========
    ADMIN_SECRET_PHRASE = "星空紫微"  # 管理員密語
    ADMIN_PASSWORD = "admin2024"     # 管理員密碼
    
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
    
    # 星球按鈕配置 (星空主題) - 優化位置以避免重疊
    RICH_MENU_BUTTONS = [
        {
            "name": "divination",
            "text": "本週占卜", 
            "action_text": "本週占卜",
            "x": 1250,  # 中上方（稍微調整）
            "y": 380,   # 下移一些
            "size": 200,
            "color": "#FFD700",  # 金色 - 太陽
            "planet": "太陽"
        },
        {
            "name": "yearly_fortune", 
            "text": "流年運勢",
            "action_text": "流年運勢", 
            "x": 600,   # 左中（增加間距）
            "y": 700,   # 下移
            "size": 180,
            "color": "#FF6B6B",  # 紅色 - 火星
            "planet": "火星"
        },
        {
            "name": "monthly_fortune",
            "text": "流月運勢", 
            "action_text": "流月運勢",
            "x": 1650,  # 右中（增加間距）
            "y": 800,   # 下移
            "size": 170,
            "color": "#4ECDC4",  # 藍綠色 - 水星
            "planet": "水星"
        },
        {
            "name": "daily_fortune",
            "text": "流日運勢",
            "action_text": "流日運勢", 
            "x": 1050,  # 中下（稍微調整）
            "y": 1250,  # 下移
            "size": 160,
            "color": "#A8E6CF",  # 綠色 - 金星
            "planet": "金星"
        },
        {
            "name": "chart_binding",
            "text": "命盤綁定",
            "action_text": "命盤綁定",
            "x": 1850,  # 右下（增加間距）
            "y": 1450,  # 下移
            "size": 150,
            "color": "#DDA0DD",  # 紫色 - 土星
            "planet": "土星"
        },
        {
            "name": "member_info",
            "text": "會員資訊", 
            "action_text": "會員資訊",
            "x": 350,   # 左下（增加間距）
            "y": 1450,  # 下移
            "size": 140,
            "color": "#87CEEB",  # 天藍色 - 木星
            "planet": "木星"
        }
    ]
    
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