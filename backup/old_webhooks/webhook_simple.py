"""
簡化版 LINE Bot Webhook
重構後的乾淨實現
"""
import os
import json
import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, PostbackEvent, FollowEvent, UnfollowEvent
)

from ..config.linebot_config import LineBotConfig
from ..models.linebot_models import LineBotUser, DivinationHistory
from ..db.database import get_db
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化 LINE Bot SDK
configuration = Configuration(access_token=LineBotConfig.CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
parser = WebhookParser(LineBotConfig.CHANNEL_SECRET)

def reply_text(reply_token: str, text: str):
    """發送純文字回覆訊息"""
    try:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )
    except Exception as e:
        logger.error(f"回覆文字訊息失敗: {e}")

async def get_user_by_line_id(line_user_id: str, db) -> LineBotUser:
    """根據 LINE 用戶 ID 獲取用戶"""
    return db.query(LineBotUser).filter(LineBotUser.line_user_id == line_user_id).first()

async def create_user_if_not_exists(user_id: str, db):
    """創建用戶如果不存在"""
    user = await get_user_by_line_id(user_id, db)
    if not user:
        user = LineBotUser(
            line_user_id=user_id,
            display_name="LINE用戶",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"自動創建新用戶: {user_id}")
    return user

def perform_simple_divination(gender: str) -> dict:
    """簡化版占卜功能"""
    from datetime import datetime
    import random
    
    # 簡化的占卜邏輯
    current_time = datetime.now()
    minute_dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"][current_time.minute % 12]
    
    # 簡化的四化結果
    transformations = ["化祿", "化權", "化科", "化忌"]
    stars = ["紫微", "天機", "太陽", "武曲", "天同", "廉貞"]
    palaces = ["命宮", "財帛宮", "官祿宮", "田宅宮", "福德宮", "父母宮"]
    
    results = []
    for i, trans in enumerate(transformations):
        results.append({
            "star": random.choice(stars),
            "transformation": trans,
            "palace": random.choice(palaces),
            "meaning": f"這週在{random.choice(['工作', '財運', '感情', '健康'])}方面會有{random.choice(['順利', '挑戰', '機會', '轉變'])}"
        })
    
    return {
        "success": True,
        "divination_time": current_time.isoformat(),
        "gender": gender,
        "minute_dizhi": minute_dizhi,
        "taichi_palace": f"{minute_dizhi}宮",
        "results": results
    }

@router.post("/webhook-simple", include_in_schema=False)
async def line_bot_webhook_simple(request: Request, db: Session = Depends(get_db)):
    """簡化版 LINE Bot Webhook 端點"""
    try:
        signature = request.headers.get("X-Line-Signature")
        body = await request.body()
        events = parser.parse(body.decode(), signature)
    except InvalidSignatureError:
        logger.error("無效的 LINE Signature")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    except Exception as e:
        logger.error(f"解析 LINE 事件失敗: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="事件解析失敗")

    for event in events:
        try:
            user_id = event.source.user_id
            
            if isinstance(event, FollowEvent):
                reply_token = event.reply_token
                reply_text(reply_token, "🌟 歡迎使用星空紫微斗數！\n\n輸入「占卜」開始占卜\n輸入「占卜男」或「占卜女」指定性別")

            elif isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                text = event.message.text.strip()
                reply_token = event.reply_token
                
                if text in ["占卜", "占卜男", "占卜女", "本週占卜"]:
                    # 確保用戶存在
                    await create_user_if_not_exists(user_id, db)
                    
                    # 確定性別
                    if "男" in text:
                        gender = "M"
                    elif "女" in text:
                        gender = "F"
                    else:
                        reply_text(reply_token, "請指定性別：\n輸入「占卜男」或「占卜女」")
                        continue
                    
                    # 執行占卜
                    result = perform_simple_divination(gender)
                    
                    if result["success"]:
                        # 格式化結果
                        result_text = f"""🔮 本週占卜結果

⏰ 占卜時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
👤 性別：{'男性' if gender == 'M' else '女性'}
🎯 太極宮：{result['taichi_palace']}

✨ 四化解析：
"""
                        for i, r in enumerate(result["results"], 1):
                            result_text += f"{i}. {r['star']}{r['transformation']}在{r['palace']} - {r['meaning']}\n"
                        
                        result_text += "\n💫 祝您本週順利！"
                        
                        reply_text(reply_token, result_text)
                        
                        # 保存記錄（簡化版）
                        try:
                            user = await get_user_by_line_id(user_id, db)
                            if user:
                                record = DivinationHistory(
                                    user_id=user.id,
                                    gender=gender,
                                    divination_time=datetime.utcnow(),
                                    taichi_palace=result['taichi_palace'],
                                    minute_dizhi=result['minute_dizhi'],
                                    sihua_results=json.dumps(result['results']),
                                    taichi_palace_mapping="{}",
                                    taichi_chart_data="{}"
                                )
                                db.add(record)
                                db.commit()
                        except Exception as e:
                            logger.warning(f"保存記錄失敗: {e}")
                    else:
                        reply_text(reply_token, "占卜失敗，請稍後再試")
                
                elif text == "功能選單":
                    reply_text(reply_token, """🌌 功能選單

🔮 占卜功能：
• 輸入「占卜男」- 男性占卜
• 輸入「占卜女」- 女性占卜

📱 其他功能正在開發中""")
                
                else:
                    reply_text(reply_token, "請輸入「占卜男」、「占卜女」或「功能選單」")

            elif isinstance(event, PostbackEvent):
                data = event.postback.data
                reply_token = event.reply_token
                
                if data == "action=weekly_fortune":
                    reply_text(reply_token, "請輸入「占卜男」或「占卜女」開始占卜")
                else:
                    reply_text(reply_token, "功能開發中，請輸入「占卜男」或「占卜女」進行占卜")

        except Exception as e:
            logger.error(f"處理事件時發生錯誤: {e}")
            try:
                if 'reply_token' in locals() and reply_token:
                    reply_text(reply_token, "處理您的請求時發生錯誤，請稍後再試")
            except:
                pass

    return {"status": "ok"} 