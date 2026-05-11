from datetime import datetime
from mythme.model.video import Video
from mythme.utils.config import config
from mythme.utils.log import logger

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_watched_vids(videos: list[Video], log_unfound=True) -> dict[str, datetime]:
    if not config.dailyvid:
        raise ValueError("Missing config: 'dailyvid'")
    video_files = [vid.file for vid in videos]
    watched_vids: dict[str, datetime] = {}
    with open(config.dailyvid.psv_file, "r") as file:
        for i, line in enumerate(file):
            parts = line.strip().split("|")
            if parts[0] in watched_vids:
                logger.error(f"Duplicate dailyvid on line {i + 1}: '{parts[0]}'")
            elif parts[0] in video_files:
                watched_vids[parts[0]] = datetime.strptime(parts[1], DATETIME_FORMAT)
            elif log_unfound:
                logger.error(f"Unfound dailyvid on line {i + 1}: '{parts[0]}'")
    return watched_vids


def to_psv(videos: list[Video]) -> str:
    lines = [f"{v.file}|{v.watched}" for v in videos if v.watched]
    return "\n".join(lines)


def update_watched(video: Video) -> bool:
    if not config.dailyvid:
        raise ValueError("Missing config: 'dailyvid'")
    if not video.watched:
        return False
    lines: list[str] = []
    idx = -1
    with open(config.dailyvid.psv_file, "r") as file:
        lines = [line.strip() for line in file]
        idx = next(
            (i for i, ln in enumerate(lines) if ln.strip().split("|")[0] == video.file),
            -1,
        )

    if idx >= 0:
        lines[idx] = f"{video.file}|{video.watched}"
    else:
        lines.append(f"{video.file}|{video.watched}")
    lines.sort(key=lambda line: line.strip().split("|")[0].lower())
    with open(config.dailyvid.psv_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return idx >= 0
