from typing import Literal
from pydantic import BaseModel
from mythme.model.program import Program

RecordingStatus = Literal["Recorded", "Failed", "Deleted", "Locked"]


class Recording(Program):
    status: RecordingStatus
    file: str
    size: int


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
    total: int
