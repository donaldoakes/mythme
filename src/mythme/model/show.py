from typing import Literal, Optional, Union
from datetime import datetime
from pydantic import BaseModel
from mythme.model.credit import Credit

ShowType = Literal["", "movie", "series", "sports", "tvshow"]


class Show(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    type: ShowType
    category: str
    year: Optional[int] = None
    rating: float
    """ rating: 0 to 5 (mythtv stars has eighths)"""
    season: Optional[int] = None
    episode: Optional[int] = None
    aired: Optional[datetime] = None
    genre: Optional[str] = None
    credits: Union[int, list[Credit]] = 0
