from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from mythme.model.channel import Channel
from mythme.model.credit import Credit
from mythme.model.program import ProgramType


class MovieInfo(BaseModel):
    title: str
    year: int
    genre: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    credits: list[Credit]


class ProgramInfo(BaseModel):
    channel: Channel | str
    title: str
    subtitle: Optional[str]
    start: datetime
    end: datetime
    description: Optional[str] = None
    type: ProgramType
    category: str
    year: Optional[int] = None
    season: int | None = None
    episode: Optional[int] = None
    aired: Optional[datetime] = None
    credits: list[Credit]


class MovieInfoResponse(BaseModel):
    movie: MovieInfo
    details: str
    """Markdown-formatted content."""


class ProgramInfoResponse(BaseModel):
    program: ProgramInfo | MovieInfo
    details: str
    """Markdown-formatted content."""
