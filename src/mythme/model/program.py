from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from mythme.model.show import Show
from mythme.model.channel import Channel
from mythme.model.query import DbQuery
from mythme.model.scheduled import ScheduledRecording


class Program(Show):
    channel: Channel
    start: datetime
    end: datetime
    recording: Optional[ScheduledRecording] = None


class ProgramsResponse(BaseModel):
    programs: list[Program]
    total: int
    query: Optional[DbQuery] = None
