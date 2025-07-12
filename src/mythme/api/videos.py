import os
import shutil
from fastapi import APIRouter, Request, HTTPException, UploadFile
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
from mythme.utils.mythtv import get_myth_hostname, get_storage_group_dirs
from mythme.utils.log import logger

router = APIRouter()


@router.get("/videos", response_model_exclude_none=True)
def get_videos(request: Request) -> VideosResponse:
    params = dict(request.query_params)
    params["sort"] = params["sort"] if "sort" in params else "id"
    query = parse_params(params)
    return VideoData().get_videos(query)


@router.post("/videos", response_model_exclude_none=True)
def create_video_metadata(video: Video) -> Video:
    video_data = VideoData()
    filepath = video_data.get_filepath(video.title, video.category, video.medium)
    if filepath is None:
        raise HTTPException(
            status_code=404,
            detail=f"Storage not found for video category: {video.category}",
        )
    exist_id = video_data.get_db_video_id(filepath)
    if exist_id is not None:
        raise HTTPException(
            status_code=409, detail=f"Video file already exists: {filepath}"
        )
    host = get_myth_hostname()
    if host is None:
        raise HTTPException(status_code=500, detail="Can't figure out MythTV hostname")
    added = video_data.add_video(filepath, host)
    if not added:
        raise HTTPException(status_code=500, detail=f"Error adding video: {filepath}")
    newvid = video_data.get_video_by_file(filepath)
    if not newvid:
        raise HTTPException(status_code=500, detail=f"Error locating video: {filepath}")

    video.id = newvid.id
    video.file = filepath
    updated = video_data.update_video(video)
    if not updated:
        raise HTTPException(status_code=500, detail=f"Error updating video: {filepath}")

    return video


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


@router.post("/video-file", response_model_exclude_none=True)
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

    exist_file = video_data.get_video_file(recording.title, category, medium)
    if exist_file:
        raise HTTPException(
            status_code=409,
            detail=f"Video file already exists: {exist_file}",
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


@router.post("/video-poster")
async def upload_poster(file: UploadFile, category: str) -> MessageResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    if file.filename.split(".")[-1] not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=415, detail="Unsupported video format")
    contents = await file.read()
    poster_path = VideoData().get_poster_path(category, file.filename)
    if poster_path is None:
        raise HTTPException(
            status_code=404, detail=f"Poster path not found for category: {category}"
        )
    if not os.path.isdir(os.path.dirname(poster_path)):
        logger.error(f"Poster storage dir not found to create file: {poster_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Poster storage dir does not exist for category: {category}",
        )
    if os.path.isfile(poster_path):
        raise HTTPException(
            status_code=409,
            detail=f"Poster file already exists for category {category}: {file.filename}",
        )

    with open(poster_path, "wb") as f:
        f.write(contents)

    return MessageResponse(message=f"Poster file saved for category: {category}")
