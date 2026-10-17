from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from mythme.model.program import ProgramType
from mythme.model.channel import Channel
from mythme.model.scheduled import ScheduledRecording


class Listing(BaseModel):
    title: str
    subtitle: Optional[str] = None
    type: ProgramType
    channel: str
    """ channel: callsign"""
    start: datetime
    end: datetime
    year: Optional[int] = None
    rating: float
    """ rating: 0 to 5 (mythtv stars has eighths)"""
    aired: Optional[datetime] = None
    recording: Optional[ScheduledRecording] = None


class ChannelListings(BaseModel):
    channel: Channel
    listings: list[Listing]
