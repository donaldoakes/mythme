from datetime import datetime
from fastapi import APIRouter
from mythme.model.credit import Credit
from mythme.data.credits import CreditsData

router = APIRouter()


@router.get("/credits")
def get_credits(channel_id: int, start: datetime) -> list[Credit]:
    return CreditsData().get_credits(channel_id, start)
