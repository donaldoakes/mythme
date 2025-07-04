from typing import Optional
from pydantic import BaseModel

from mythme.model.credit import Credit


class Video(BaseModel):
    id: int
    title: str
    file: str
    subtitle: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    credits: Optional[list[Credit]] = None
    poster: Optional[str] = None
    webref: Optional[str] = None


class VideosResponse(BaseModel):
    videos: list[Video]
    total: int
