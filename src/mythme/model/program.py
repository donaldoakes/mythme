from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel
from mythme.model.channel import Channel
from mythme.model.query import DbQuery
from mythme.model.recording import ScheduledRecording

ProgramType = Literal["", "movie", "series", "sports", "tvshow"]


class Program(BaseModel):
    channel: Channel
    title: str
    subtitle: Optional[str] = None
    start: datetime
    end: datetime
    description: Optional[str] = None
    type: ProgramType
    category: str
    year: Optional[int] = None
    rating: float
    """ rating: 0 to 5 (mythtv stars has eighths)"""
    season: Optional[int] = None
    episode: Optional[int] = None
    aired: Optional[datetime] = None
    recording: Optional[ScheduledRecording] = None
    genre: Optional[str] = None
    credits: Optional[int] = None


class ProgramsResponse(BaseModel):
    programs: list[Program]
    total: int
    query: Optional[DbQuery] = None
