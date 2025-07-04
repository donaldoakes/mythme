from fastapi import APIRouter, Request
from mythme.data.videos import VideoData
from mythme.model.video import VideosResponse
from mythme.query.queries import parse_params

router = APIRouter()


@router.get("/videos", response_model_exclude_none=True)
def get_videos(request: Request) -> VideosResponse:
    query = parse_params(dict(request.query_params))
    video_data = VideoData()
    return video_data.get_videos(query)
