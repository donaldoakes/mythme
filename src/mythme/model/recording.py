from pydantic import BaseModel
from mythme.model.program import Program


class Recording(Program):
    recid: int
    status: str
    file: str
    size: int
    group: str


class RecordingsResponse(BaseModel):
    recordings: list[Recording]
    total: int
