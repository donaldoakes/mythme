from fastapi import APIRouter
from mythme.data.movies import get_movie_details
from mythme.model.movie import MovieInfo, MovieInfoResponse

router = APIRouter()


@router.post("/movie-infos", response_model_exclude_none=True)
async def receive_movie_info(movie_info: MovieInfo) -> MovieInfoResponse:
    content = get_movie_details(movie_info.model_dump_json(indent=2))
    return MovieInfoResponse(movie=movie_info, details=content)
