from typing import Optional
from pydantic import BaseModel


class Video(BaseModel):
    id: int
    title: str
    subtitle: Optional[str] = None
    file: str


class VideosResponse(BaseModel):
    videos: list[Video]
    total: int
