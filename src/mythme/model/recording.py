from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel


@dataclass
class RecordingType:
    number: int
    name: str
    description: str


recording_types: dict[int, RecordingType] = {
    0: RecordingType(0, "Not Recording", "Do not record"),
    1: RecordingType(1, "Single Record", "Record this showing"),
    2: RecordingType(2, "Record Daily", "Record one showing every day"),
    4: RecordingType(4, "Record All", "Record all showings"),
    5: RecordingType(5, "Record Weekly", "Record one showing every week"),
    6: RecordingType(6, "Record One", "Record one showing"),
    7: RecordingType(7, "Override Record", "Record this showing with override options"),
}


@dataclass
class ScheduledRecording:
    id: int
    type: int
    channel_id: int
    start: datetime
    status: str


class RecordingRequest(BaseModel):
    channel_id: int
    start: datetime
    type: int
