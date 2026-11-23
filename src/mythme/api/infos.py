from typing import cast

from fastapi import APIRouter, HTTPException
from mythme.data.infos import get_movie_info, get_program_info
from mythme.data.videos import VideoData
from mythme.data.recordings import RecordingsData
from mythme.model.credit import Credit
from mythme.model.info import (
    MovieInfo,
    MovieInfoResponse,
    ProgramInfoResponse,
    ProgramInfo,
)

router = APIRouter()


@router.get("/video-infos/{video_id}", response_model_exclude_none=True)
async def get_video_info(video_id: str) -> MovieInfoResponse:
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
    content = get_movie_info(movie_info.model_dump_json(indent=2))
    return MovieInfoResponse(movie=movie_info, details=content)


@router.get("/rec-infos/{recid}", response_model_exclude_none=True)
async def get_rec_info(recid: int) -> ProgramInfoResponse:
    recording = RecordingsData().get_recording(recid)
    if not recording:
        raise HTTPException(status_code=404, detail=f"Recording not found: {recid}")

    if recording.type == "movie":
        movie_info = MovieInfo(
            title=recording.title,
            year=recording.year or 0,
            genre=recording.category,
            rating=recording.rating,
            credits=cast(list[Credit], recording.credits or []),
        )
        content = get_movie_info(movie_info.model_dump_json(indent=2))
        return ProgramInfoResponse(program=movie_info, details=content)
    else:
        program_info = ProgramInfo(
            channel=recording.channel,
            title=recording.title,
            subtitle=recording.subtitle,
            type=recording.type,
            category=recording.category,
            start=recording.start,
            end=recording.end,
            description=recording.description,
            season=recording.season,
            episode=recording.episode,
            year=recording.year or 0,
            credits=cast(list[Credit], recording.credits or []),
            aired=recording.aired,
        )
        content = get_program_info(program_info.model_dump_json(indent=2))
        return ProgramInfoResponse(program=program_info, details=content)
