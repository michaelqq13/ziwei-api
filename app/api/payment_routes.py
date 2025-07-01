from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import hashlib
import hmac

from app.db.database import get_db
from app.logic.permission_manager import PermissionManager

logger = logging.getLogger(__name__)

router = APIRouter()

# 金流服務提供商枚舉
class PaymentProvider:
    ECPAY = "ecpay"           # 綠界科技
    NEWEBPAY = "newebpay"     # 藍新金流
    LINEPAY = "linepay"       # Line Pay
    STRIPE = "stripe"         # Stripe (國際)

# 訂閱方案
class SubscriptionPlan(BaseModel):
    plan_id: str
    name: str
    price: int              # 價格（台幣）
    duration_days: int      # 有效天數
    description: str

# 預設訂閱方案
SUBSCRIPTION_PLANS = {
    "monthly": SubscriptionPlan(
        plan_id="monthly",
        name="月費方案",
        price=199,
        duration_days=30,
        description="✨ 完整功能一個月使用權"
    ),
    "quarterly": SubscriptionPlan(
        plan_id="quarterly", 
        name="季費方案",
        price=499,
        duration_days=90,
        description="✨ 完整功能三個月使用權（省100元）"
    ),
    "yearly": SubscriptionPlan(
        plan_id="yearly",
        name="年費方案", 
        price=1599,
        duration_days=365,
        description="✨ 完整功能一年使用權（省790元）"
    )
}

class PaymentRequest(BaseModel):
    user_id: str
    plan_id: str
    provider: str = PaymentProvider.ECPAY
    return_url: Optional[str] = None
    notify_url: Optional[str] = None

class PaymentCallback(BaseModel):
    """金流回調數據模型（根據不同金流服務商調整）"""
    pass

@router.get("/plans")
async def get_subscription_plans():
    """獲取所有訂閱方案"""
    return {
        "plans": list(SUBSCRIPTION_PLANS.values()),
        "currency": "TWD"
    }

@router.post("/create-order")
async def create_payment_order(
    request: PaymentRequest,
    db: Session = Depends(get_db)
):
    """創建付費訂單"""
    try:
        # 驗證方案
        if request.plan_id not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="無效的訂閱方案")
        
        plan = SUBSCRIPTION_PLANS[request.plan_id]
        
        # 檢查用戶是否存在
        user_permissions = PermissionManager.get_or_create_user_permissions(request.user_id, db)
        
        # 根據金流服務商創建訂單
        if request.provider == PaymentProvider.ECPAY:
            payment_data = await _create_ecpay_order(request, plan)
        elif request.provider == PaymentProvider.NEWEBPAY:
            payment_data = await _create_newebpay_order(request, plan)
        elif request.provider == PaymentProvider.LINEPAY:
            payment_data = await _create_linepay_order(request, plan)
        else:
            raise HTTPException(status_code=400, detail="不支援的金流服務商")
        
        return {
            "success": True,
            "payment_data": payment_data,
            "plan": plan,
            "order_info": {
                "user_id": request.user_id,
                "plan_id": request.plan_id,
                "amount": plan.price,
                "currency": "TWD"
            }
        }
        
    except Exception as e:
        logger.error(f"創建付費訂單失敗: {e}")
        raise HTTPException(status_code=500, detail="創建訂單失敗")

@router.post("/callback/{provider}")
async def payment_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """金流回調處理"""
    try:
        body = await request.body()
        
        # 根據不同金流服務商處理回調
        if provider == PaymentProvider.ECPAY:
            result = await _handle_ecpay_callback(body, db)
        elif provider == PaymentProvider.NEWEBPAY:
            result = await _handle_newebpay_callback(body, db)
        elif provider == PaymentProvider.LINEPAY:
            result = await _handle_linepay_callback(body, db)
        else:
            raise HTTPException(status_code=400, detail="不支援的金流服務商")
        
        return result
        
    except Exception as e:
        logger.error(f"處理金流回調失敗: {e}")
        raise HTTPException(status_code=500, detail="處理回調失敗")

@router.get("/status/{user_id}")
async def get_payment_status(user_id: str, db: Session = Depends(get_db)):
    """查詢用戶付費狀態"""
    try:
        status = PermissionManager.get_user_status_summary(user_id, db)
        
        return {
            "user_id": user_id,
            "is_premium": status.get("is_premium", False),
            "subscription_status": status.get("subscription_status", "none"),
            "subscription_end": status.get("subscription_end"),
            "available_plans": list(SUBSCRIPTION_PLANS.values())
        }
        
    except Exception as e:
        logger.error(f"查詢付費狀態失敗: {e}")
        raise HTTPException(status_code=500, detail="查詢狀態失敗")

# 以下是各金流服務商的具體實現（待金流申請完成後填入）

async def _create_ecpay_order(request: PaymentRequest, plan: SubscriptionPlan) -> Dict[str, Any]:
    """創建綠界科技訂單"""
    # TODO: 實現綠界科技API對接
    return {
        "provider": "ecpay",
        "payment_url": "https://payment.ecpay.com.tw/...",
        "order_id": f"ecpay_{request.user_id}_{plan.plan_id}",
        "message": "請前往綠界科技完成付款"
    }

async def _create_newebpay_order(request: PaymentRequest, plan: SubscriptionPlan) -> Dict[str, Any]:
    """創建藍新金流訂單"""
    # TODO: 實現藍新金流API對接
    return {
        "provider": "newebpay", 
        "payment_url": "https://ccore.newebpay.com/...",
        "order_id": f"newebpay_{request.user_id}_{plan.plan_id}",
        "message": "請前往藍新金流完成付款"
    }

async def _create_linepay_order(request: PaymentRequest, plan: SubscriptionPlan) -> Dict[str, Any]:
    """創建Line Pay訂單"""
    # TODO: 實現Line Pay API對接
    return {
        "provider": "linepay",
        "payment_url": "https://api-pay.line.me/...",
        "order_id": f"linepay_{request.user_id}_{plan.plan_id}",
        "message": "請使用Line Pay完成付款"
    }

async def _handle_ecpay_callback(body: bytes, db: Session) -> Dict[str, Any]:
    """處理綠界科技回調"""
    # TODO: 實現綠界科技回調驗證和處理
    # 1. 驗證回調簽名
    # 2. 解析付款結果
    # 3. 更新用戶訂閱狀態
    return {"status": "success"}

async def _handle_newebpay_callback(body: bytes, db: Session) -> Dict[str, Any]:
    """處理藍新金流回調"""
    # TODO: 實現藍新金流回調驗證和處理
    return {"status": "success"}

async def _handle_linepay_callback(body: bytes, db: Session) -> Dict[str, Any]:
    """處理Line Pay回調"""
    # TODO: 實現Line Pay回調驗證和處理
    return {"status": "success"} 