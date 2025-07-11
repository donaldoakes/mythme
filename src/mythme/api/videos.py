import os
import shutil
from fastapi import APIRouter, Request, HTTPException
from mythme.data.recordings import RecordingsData
from mythme.data.videos import VideoData
from mythme.model.api import MessageResponse
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
from mythme.utils.mythtv import get_storage_group_dirs

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


@router.post("/video-files", response_model_exclude_none=True)
def post_video_file(
    source: str, category: str, recording: Recording
) -> MessageResponse:
    if not source == "recording":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video file source: {source}",
        )

    """Copy recording file to Videos storage group"""
    video_data = VideoData()

    _file, ext = os.path.splitext(recording.file)
    medium = ext[1:].upper()

    if video_data.get_video_file(recording.title, category, medium):
        raise HTTPException(
            status_code=409,
            detail=f"{category} video file already exists: {recording.title}",
        )

    recording_file = RecordingsData().get_recording_file(recording)
    if recording_file is None:
        raise HTTPException(
            status_code=404,
            detail=f"Recording file not found in '{recording.group}' storage group: {recording.file}",
        )

    sg_dirs = get_storage_group_dirs("Videos")
    if sg_dirs is None or len(sg_dirs) == 0:
        raise HTTPException(
            status_code=404,
            detail="Videos storage group directories not found",
        )

    video_file = video_data.get_filepath(recording.title, category, medium)
    if video_file is None:
        raise HTTPException(
            status_code=404,
            detail=f"Category directory not found for: {category}",
        )

    for sg_dir in sg_dirs:
        video_path = f"{sg_dir}/{video_file}"
        # copies to first existing sg subdir
        if os.path.isdir(os.path.dirname(video_path)):
            shutil.copy(recording_file, video_path)
            return MessageResponse(
                message=f"Recording '{recording.title}' copied to Videos storage group under {category} category"
            )

    raise HTTPException(
        status_code=404,
        detail=f"Storage group subdirectory not found for category: {category}",
    )
