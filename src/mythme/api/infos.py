from fastapi import APIRouter, HTTPException
from mythme.data.movies import get_movie_details
from mythme.data.videos import VideoData
from mythme.model.movie import MovieInfo, MovieInfoResponse

router = APIRouter()


@router.get("/movie-infos/{video_id}", response_model_exclude_none=True)
async def get_movie_info(video_id: str) -> MovieInfoResponse:
    video = VideoData().get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    if not video.year or not video.credits:
        raise HTTPException(
            status_code=400,
            detail=f"Video missing required information: {video_id}",
        )
    movie_info = MovieInfo(
        title=video.title,
        year=video.year or 0,
        genre=video.file.split("/")[0],
        rating=video.rating,
        credits=video.credits or [],
    )
    content = get_movie_details(movie_info.model_dump_json(indent=2))
    return MovieInfoResponse(movie=movie_info, details=content)
