from fastapi import APIRouter, Request, HTTPException
from mythme.data.videos import VideoData
from mythme.model.recording import Recording
from mythme.model.video import (
    DeleteMetadataResponse,
    Video,
    VideoScanRequest,
    VideoScanResponse,
    VideoSyncRequest,
    VideoSyncResponse,
    VideosResponse,
)
from mythme.query.queries import parse_params

router = APIRouter()


@router.get("/videos", response_model_exclude_none=True)
def get_videos(request: Request) -> VideosResponse:
    params = dict(request.query_params)
    params["sort"] = params["sort"] if "sort" in params else "id"
    query = parse_params(params)
    return VideoData().get_videos(query)


@router.get("/videos/{id}", response_model_exclude_none=True)
def get_video(id: int) -> Video:
    video = VideoData().get_video(id)
    if video is None:
        raise HTTPException(status_code=404, detail=f"Video not found: {id}")
    return video


@router.delete("/videos", response_model_exclude_none=True)
def delete_video_metadata() -> DeleteMetadataResponse:
    """Deletes all video metadata from the database.
    Does not delete video files"""
    rows = VideoData().delete_video_metadata()
    return DeleteMetadataResponse(deleted=rows)


@router.patch("/videos", response_model_exclude_none=True)
def sync_videos(sync_request: VideoSyncRequest) -> VideoSyncResponse:
    result = VideoData().sync_video_metadata(sync_request.videos)
    if result is None:
        raise HTTPException(status_code=404, detail="No video storage group dirs found")
    (updated, missing) = result
    return VideoSyncResponse(updated=updated, missing=missing)


@router.post("/video-scan", response_model_exclude_none=True)
def scan_videos(request: VideoScanRequest) -> VideoScanResponse:
    result = VideoData().scan_videos()
    if result is None:
        raise HTTPException(status_code=404, detail="No video storage group dirs found")

    (added, deleted) = result
    return VideoScanResponse(added=added, deleted=deleted)


@router.post("video-files")
def post_video_file(recording: Recording, category: str) -> Video:
    """Copy recording file to video storage group"""
    video_data = VideoData()
    if video_data.get_video_file(category, recording.title):
        raise HTTPException(
            status_code=409,
            detail=f"{category} video file already exists: {recording.title}",
        )

    video = video_data.add_video_from_recording(recording, category)
    return video
