from typing import cast
from fastapi import APIRouter, HTTPException
from mythme.data.programs import ProgramData
from mythme.model.credit import Credit
from mythme.model.info import (
    MovieInfo,
    ProgramInfo,
    MovieInfoResponse,
    ProgramInfoResponse,
)
from mythme.data.infos import get_movie_info, get_program_info
from mythme.data.videos import VideoData
from mythme.data.recordings import RecordingsData
from mythme.model.program import Program

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

    return get_program_info_response(recording)


@router.get("/show-infos/{channel}/{start}", response_model_exclude_none=True)
async def get_show_info(channel: str, start: str) -> ProgramInfoResponse:
    program = ProgramData().get_program(channel, start)
    if not program:
        raise HTTPException(
            status_code=404, detail=f"Program not found: {channel} {start}"
        )

    return get_program_info_response(program)


def get_program_info_response(program: Program) -> ProgramInfoResponse:
    if program.type == "movie":
        movie_info = MovieInfo(
            title=program.title,
            year=program.year or 0,
            genre=program.category,
            rating=program.rating,
            credits=cast(list[Credit], program.credits or []),
        )
        content = get_movie_info(movie_info.model_dump_json(indent=2))
        return ProgramInfoResponse(program=movie_info, details=content)
    else:
        program_info = ProgramInfo(
            channel=program.channel,
            title=program.title,
            subtitle=program.subtitle,
            type=program.type,
            category=program.category,
            start=program.start,
            end=program.end,
            description=program.description,
            season=program.season,
            episode=program.episode,
            year=program.year or 0,
            credits=cast(list[Credit], program.credits or []),
            aired=program.aired,
        )
        content = get_program_info(program_info.model_dump_json(indent=2))
        return ProgramInfoResponse(program=program_info, details=content)
