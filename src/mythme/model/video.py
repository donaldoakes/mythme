from typing import Optional
from pydantic import BaseModel

from mythme.model.credit import Credit


class WebRef(BaseModel):
    site: str
    ref: str


class Video(BaseModel):
    """Similar to oakesville movie model"""

    id: int
    title: str
    file: str
    subtitle: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    credits: Optional[list[Credit]] = None
    poster: Optional[str] = None
    webref: Optional[WebRef] = None


class VideosResponse(BaseModel):
    videos: list[Video]
    total: int
