from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from mythme.model.channel import Channel
from mythme.model.show import Show
from mythme.model.scheduled import ScheduledRecording


class Listing(Show):
    start: datetime
    end: datetime
    recording: Optional[ScheduledRecording] = None


class ChannelListings(BaseModel):
    channel: Channel
    listings: list[Listing]
