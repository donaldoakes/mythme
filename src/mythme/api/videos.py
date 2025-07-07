from fastapi import APIRouter, Request, HTTPException
from mythme.data.videos import VideoData
from mythme.model.api import MessageResponse
from mythme.model.video import Video, VideoSyncRequest, VideosResponse
from mythme.query.queries import parse_params
from mythme.utils.config import config
from mythme.utils.log import logger

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


@router.delete("/videos", response_model_exclude_none=True)
def delete_video_metadata() -> MessageResponse:
    """Deletes all video metadata from the database.
    Does not delete video files"""
    rows = VideoData().delete_video_metadata()
    return MessageResponse(message=f"Metadata deleted for {rows} videos")


@router.post("/video-scan", response_model_exclude_none=True)
def scan_videos() -> MessageResponse:
    rows = VideoData().scan_videos()
    return MessageResponse(message=f"Scan found {rows} new videos")


@router.patch("/videos", response_model_exclude_none=True)
def sync_videos(sync_request: VideoSyncRequest) -> MessageResponse:
    video_data = VideoData()
    for vid in sync_request.videos:
        cat_path = (
            config.mythtv.categories[vid.category]
            if vid.category in config.mythtv.categories
            else None
        )
        if not cat_path:
            raise HTTPException(
                status_code=404, detail=f"Category not configured: {vid.category}"
            )
        file = f"{cat_path}/{vid.title}.mpg"
        video = video_data.get_video_by_file(file)
        if video:
            vid.id = video.id
            vid.file = video.file
            logger.info(f'Updating {cat_path}: "{video.title}"')
            if not video_data.update_video(vid):
                logger.error(f"Failed to update {cat_path}: {video.title}")

        else:
            # TODO add stub
            logger.info(f'Creating {cat_path} stub: "{vid.title}"')

    return MessageResponse(message="Synced some videos")
