from typing import Optional
from fastapi import APIRouter, HTTPException
from mythme.model.listing import ChannelListings, Listing
from mythme.data.listings import ListingsData
from mythme.api.programs import recordings_data

router = APIRouter()


@router.get("/listings", response_model_exclude_none=True)
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


@router.get("/listings/{channel}/{start}", response_model_exclude_none=True)
def get_listing(channel: str, start: str) -> Listing:
    listing = ListingsData().get_listing(channel, start)
    if not listing:
        raise HTTPException(status_code=404)
    return listing
