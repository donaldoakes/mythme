from datetime import datetime
from mythme.model.video import Video
from mythme.utils.config import config
from mythme.utils.log import logger

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_watched_vids(videos: list[Video]) -> dict[str, datetime]:
    video_files = [vid.file for vid in videos]
    watched_vids: dict[str, datetime] = {}
    if not config.dailyvid:
        raise ValueError("Missing config: 'dailyvid'")
    with open(config.dailyvid.psv_file, "r") as file:
        for i, line in enumerate(file):
            parts = line.strip().split("|")
            if parts[0] in watched_vids:
                logger.error(f"Duplicate dailyvid on line {i + 1}: '{parts[0]}'")
            elif parts[0] in video_files:
                watched_vids[parts[0]] = datetime.strptime(parts[1], DATETIME_FORMAT)
            else:
                logger.error(f"Unfound dailyvid on line {i + 1}: '{parts[0]}'")
    return watched_vids


def to_psv(videos: list[Video]) -> str:
    lines = [f"{v.file}|{v.watched}" for v in videos if v.watched]
    return "\n".join(lines)
