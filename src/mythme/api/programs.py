from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from mythme.model.program import Program, ProgramsResponse
from mythme.data.programs import ProgramData
from mythme.data.recordings import RecordingsData
from mythme.query.queries import parse_params

router = APIRouter()

recordings_data = RecordingsData()


@router.get("/programs", response_model_exclude_none=True)
def get_programs(request: Request) -> ProgramsResponse:
    query = parse_params(dict(request.query_params))
    program_data = ProgramData()
    programs_response = program_data.get_programs(query)
    for program in programs_response.programs:
        if program.year == 0:
            program.year = None
        program.recording = recordings_data.find_scheduled_recording(
            program.channel.id, program.start
        )

    return programs_response


@router.get("/programs/categories")
def get_categories() -> list[str]:
    categories = ProgramData().get_categories()
    if len(categories) > 0 and categories[0] == "":
        categories.pop(0)
    return categories


@router.get("/programs/genres")
def get_genres() -> list[str]:
    return ProgramData().get_genres()


@router.get("/programs/{channel}/{start}")
def get_program(channel: str, start: str) -> Optional[Program]:
    program = ProgramData().get_program(channel, start)
    if not program:
        raise HTTPException(status_code=404)
    return program
