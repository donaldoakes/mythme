import os
import time
from datetime import datetime
from typing import Optional
from mythme.model.channel import Channel, ChannelIcon
from mythme.model.credit import Credit
from mythme.model.query import Query, Sort
from mythme.model.recording import Recording, RecordingsResponse
from mythme.model.scheduled import ScheduledRecording
from mythme.utils.mythtv import (
    api_call,
    api_update,
    paging_params,
    get_storage_group_dirs,
)
from mythme.utils.log import logger
from mythme.utils.text import trim_article


class RecordingsData:
    scheduled_recordings: list[ScheduledRecording] = []

    def get_recordings(self, query: Query) -> RecordingsResponse:
        before = time.time()
        result = api_call("Dvr/GetRecordedList" + paging_params(query))
        total = 0
        if result and "ProgramList" in result and "Programs" in result["ProgramList"]:
            recordings = [
                self.to_recording(prog)
                for prog in result["ProgramList"]["Programs"]
                if "RecGroup" not in prog["Recording"]
                or prog["Recording"]["RecGroup"] != "Deleted"
            ]
            total = result["ProgramList"]["TotalAvailable"]
            logger.info(
                f"Retrieved {len(recordings)} recordings in: {(time.time() - before):.2f} seconds\n"  # noqa: E501
            )
        else:
            raise Exception("Failed to retrieve recordings")

        if query.sort.name and query.sort.name != "start":
            recordings.sort(
                key=lambda rec: self.sort(rec, query.sort),
                reverse=True if query.sort.order == "desc" else False,
            )

        return RecordingsResponse(recordings=recordings, total=total)

    def get_recording(self, recid: int) -> Optional[Recording]:
        result = api_call(f"Dvr/GetRecorded?RecordedId={recid}")
        prog = result["Program"] if result and "Program" in result else None
        if prog:
            rec = prog["Recording"] if "Recording" in prog else None
            if rec and ("RecGroup" not in rec or rec["RecGroup"] != "Deleted"):
                return self.to_recording(prog)
        return None

    def delete_recording(self, recid: int) -> bool:
        return api_update(path=f"Dvr/DeleteRecording?RecordedId={recid}")

    def sort(self, recording: Recording, sort: Sort) -> tuple:
        """Sort according to query."""
        title = trim_article(recording.title.lower())
        if sort.name == "title":
            return (title, recording.start)
        elif sort.name == "year":
            return (recording.year or 0, title)
        elif sort.name == "rating":
            return (recording.rating or 0, title)
        elif sort.name == "channel":
            return (recording.channel.number, title)
        elif sort.name == "category":
            return (recording.category, title)
        elif sort.name == "size":
            return (recording.size, title)
        else:
            raise ValueError(f"Unsupported sort: {sort.name}")

    def load_scheduled(self):
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

    def to_recording(self, prog: dict) -> Recording:
        chan = prog["Channel"]
        channel = Channel(
            id=chan["ChanId"],
            number=chan["ChanNum"],
            callsign=chan["CallSign"],
            name=chan["ChannelName"],
        )
        if "Icon" in chan:
            channel.icon = ChannelIcon(file=chan["Icon"])
            try:
                channel.icon.shade = chan["Icon"].split("_")[1]
            except IndexError:
                pass

        rec = prog["Recording"]

        recording = Recording(
            channel=channel,
            title=prog["Title"],
            subtitle=prog["SubTitle"] or None,
            start=datetime.fromisoformat(prog["StartTime"]),
            end=datetime.fromisoformat(prog["EndTime"]),
            description=prog["Description"] or None,
            type=prog["CatType"],
            category=prog["Category"],
            rating=prog["Stars"] * 5 if "Stars" in prog else 0,
            recid=rec["RecordedId"],
            status=rec["StatusName"],
            file=rec["FileName"],
            size=rec["FileSize"],
            group=rec["StorageGroup"],
        )
        if "Airdate" in prog and prog["Airdate"]:
            hyphen = prog["Airdate"].find("-")
            if hyphen == 4:
                recording.year = int(prog["Airdate"][:4])
        if "Season" in prog and prog["Season"]:
            recording.season = prog["Season"]
            if "Episode" in prog and prog["Episode"]:
                recording.episode = prog["Episode"]
        recording.credits = []
        if "Cast" in prog and "CastMembers" in prog["Cast"]:
            recording.credits = [
                Credit(name=cm["Name"], role=cm["Role"])
                for cm in prog["Cast"]["CastMembers"]
            ]

        return recording

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

    def get_recording_file(self, recording: Recording) -> Optional[str]:
        sg_dirs = get_storage_group_dirs(recording.group)
        if sg_dirs is not None:
            for sg_dir in sg_dirs:
                filepath = f"{sg_dir}/{recording.file}"
                if os.path.isfile(filepath):
                    return filepath
        return None
