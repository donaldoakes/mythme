from fastapi import APIRouter, Request, HTTPException
from mythme.data.videos import VideoData
from mythme.model.video import Video, VideosResponse
from mythme.query.queries import parse_params

router = APIRouter()


@router.get("/videos", response_model_exclude_none=True)
def get_videos(request: Request) -> VideosResponse:
    query = parse_params(dict(request.query_params))
    return VideoData().get_videos(query)


@router.get("/videos/{id}", response_model_exclude_none=True)
def get_video(id: int) -> Video:
    video = VideoData().get_video(id)
    if video is None:
        raise HTTPException(status_code=404, detail=f"Video not found: {id}")
    return video
