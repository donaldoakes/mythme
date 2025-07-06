from typing import Optional, Union
from pydantic import BaseModel

from mythme.model.credit import Credit


class WebRef(BaseModel):
    site: str
    ref: str


class Video(BaseModel):
    """Similar to Oakesville movie model"""

    id: Union[int, str]
    title: str
    category: Optional[str] = None
    """ Oakesville movie category (ignored -- lookup is by file path) """
    file: str = ""
    subtitle: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    credits: Optional[list[Credit]] = None
    """ Full-path poster file """
    poster: Optional[str] = None
    webref: Optional[WebRef] = None


class VideosResponse(BaseModel):
    videos: list[Video]
    total: int


class VideoSyncRequest(BaseModel):
    videos: list[Video]
