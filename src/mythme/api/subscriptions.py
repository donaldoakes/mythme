from fastapi import APIRouter, Request, HTTPException
from mythme.data.subscriptions import SubscriptionData
from mythme.model.subscription import SubscriptionKeyResponse
from mythme.utils.config import config
from mythme.utils.push import do_push

router = APIRouter()


@router.get("/subscription-key", response_model_exclude_none=True)
def get_subscription_key() -> SubscriptionKeyResponse:
    public_key = SubscriptionData().get_public_key()
    if not public_key:
        raise HTTPException(status_code=404)

    return SubscriptionKeyResponse(public_key=public_key)


@router.post("/subscriptions")
async def add_subscription(request: Request):
    if not config.webpush:
        raise HTTPException(status_code=404)
    subscription = await request.json()
    do_push(config=config.webpush, subscription=subscription)
    return {"message": "Added"}
