from datetime import datetime
from fastapi import APIRouter, HTTPException
from mythme.data.recordings import RecordingsData
from mythme.model.recording import RecordingRequest, ScheduledRecording, recording_types
from mythme.utils.mythtv import api_call
from mythme.utils.log import logger

router = APIRouter()


@router.put("/recordings")
def schedule_recording(recording: RecordingRequest) -> ScheduledRecording:
    rec_type = recording_types[recording.type]
    if not rec_type:
        logger.error(f"Invalid recording type: {recording.type}")
        raise HTTPException(status_code=400, detail="Invalid recording type")

    logger.info(f"Getting recording schedule: {recording}")
    result = api_call(
        "Dvr/GetRecordSchedule",
        params={
            "ChanId": f"{recording.channel_id}",
            "StartTime": recording.start.isoformat(),
        },
    )
    if not result or "RecRule" not in result:
        logger.error("Failed to get recording schedule: {recording}")
        raise HTTPException(status_code=404, detail="Failed to get recording schedule")

    rule = result["RecRule"]

    logger.info(f"Scheduling recording: {recording}")
    result = api_call(
        "Dvr/AddRecordSchedule",
        method="POST",
        params={
            "ChanId": f"{rule["ChanId"]}",
            "StartTime": rule["StartTime"],
            "EndTime": rule["EndTime"],
            "Station": rule["CallSign"],
            "Type": rec_type.name,
            "Title": rule["Title"],
            "FindDay": f"{rule["FindDay"]}",
            "FindTime": f"{rule["FindTime"]}",
        },
    )
    if not result:
        logger.error(f"Failed to schedule: {recording}")
        raise HTTPException(status_code=404, detail=f"Failed to schedule: {recording}")

    rec = ScheduledRecording(
        id=result["uint"],
        channel_id=recording.channel_id,
        start=datetime.fromisoformat(rule["StartTime"]),
        type=recording.type,
        status="WillRecord",
    )

    RecordingsData().set_scheduled_recording(rec)

    return rec


@router.delete("/recordings/{id}")
def unschedule_recording(id: int):
    logger.info(f"Unscheduling recording: {id}")
    result = api_call(
        "Dvr/RemoveRecordSchedule", method="POST", params={"RecordId": f"{id}"}
    )
    if not result:
        logger.error(f"Failed to unschedule recording: {id}")
        raise HTTPException(status_code=404, detail=f"Recording not found: {id}")

    RecordingsData().remove_scheduled_recording(id)

    return {"detail": "OK"}
