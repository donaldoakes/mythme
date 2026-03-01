from typing import Optional
from mythme.utils.config import config


class SubscriptionData:
    public_key: Optional[str] = None

    def get_public_key(self) -> Optional[str]:
        if not config.webpush:
            return None

        if not SubscriptionData.public_key:
            with open(config.webpush.public_keyfile, "r", encoding="utf-8") as f:
                SubscriptionData.public_key = f.read()

        return SubscriptionData.public_key
