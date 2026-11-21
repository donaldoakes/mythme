from typing import Optional
from pydantic import BaseModel
from mythme.model.credit import Credit


class MovieInfo(BaseModel):
    title: str
    year: int
    genre: str
    rating: Optional[float] = None
    credits: list[Credit]


class MovieInfoResponse(BaseModel):
    movie: MovieInfo
    details: str
    """Markdown-formatted content."""
