from typing import Optional
from fastapi import APIRouter
from mythme.model.listing import ChannelListings
from mythme.data.listings import ListingsData

router = APIRouter()


@router.get("/listings")
def get_listings(channel_group: Optional[str] = None) -> list[ChannelListings]:
    return ListingsData().get_listings(channel_group)
