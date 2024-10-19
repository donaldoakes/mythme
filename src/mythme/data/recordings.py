import time
from datetime import datetime
from typing import Optional
from mythme.model.recording import ScheduledRecording
from mythme.utils.mythtv import api_call
from mythme.utils.log import logger


class RecordingsData:
    scheduled_recordings: list[ScheduledRecording] = []

    def load(self):
        before = time.time()
        logger.info("Loading scheduled recordings...")
        result = api_call("Dvr/GetUpcomingList")
        if result:
            RecordingsData.scheduled_recordings = [
                self.to_scheduled_recording(sr)
                for sr in result["ProgramList"]["Programs"]
            ]
            logger.info(
                f"Loaded {len(RecordingsData.scheduled_recordings)} scheduled recordings in: {(time.time() - before):.2f} seconds\n"  # noqa: E501
            )
        else:
            logger.error("Failed to load scheduled recordings")

    def to_scheduled_recording(self, sr: dict) -> ScheduledRecording:
        return ScheduledRecording(
            id=sr["Recording"]["RecordId"],
            channel_id=sr["Channel"]["ChanId"],
            start=datetime.fromisoformat(sr["StartTime"]),
            type=sr["Recording"]["RecType"],
            status=sr["Recording"]["StatusName"],
        )

    def find_scheduled_recording(
        self, channel_id: int, start: datetime
    ) -> Optional[ScheduledRecording]:
        recording: Optional[ScheduledRecording] = None
        for sr in RecordingsData.scheduled_recordings:
            if (
                sr.channel_id == channel_id
                and sr.start.date() == start.date()
                and sr.start.time() == start.time()
                and (recording is None or sr.type > recording.type)
            ):
                recording = sr
        return recording

    def set_scheduled_recording(self, recording: ScheduledRecording):
        rec = self.find_scheduled_recording(recording.channel_id, recording.start)
        if rec:
            rec.id = recording.id
            rec.type = recording.type
            rec.status = recording.status
        else:
            RecordingsData.scheduled_recordings.append(recording)

    def remove_scheduled_recording(self, id: int):
        RecordingsData.scheduled_recordings = [
            sr for sr in RecordingsData.scheduled_recordings if sr.id != id
        ]
