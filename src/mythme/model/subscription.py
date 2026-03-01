from pydantic import BaseModel


class SubscriptionKeyResponse(BaseModel):
    public_key: str
