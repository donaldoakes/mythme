from typing import Optional
from fastapi import APIRouter
from mythme.model.listing import ChannelListings
from mythme.data.listings import ListingsData
from mythme.api.programs import recordings_data

router = APIRouter()


@router.get("/listings")
def get_listings(
    channel_group: Optional[str] = None, end_dt: Optional[str] = None
) -> list[ChannelListings]:
    listings = ListingsData().get_listings(channel_group, end_dt)
    for cl in listings:
        for listing in cl.listings:
            listing.recording = recordings_data.find_scheduled_recording(
                cl.channel.id, listing.start
            )
    return listings
