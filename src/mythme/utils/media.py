from typing import Optional
from pathlib import Path
from mythme.utils.mythtv import get_storage_group_dirs

# TODO: more comprehensive
AUDIO_MEDIA_TYPES = {"mp3": "audio/mpeg"}

# TODO: more comprehensive
VIDEO_MEDIA_TYPES = {"mp4": "video/mp4", "mpg": "video/mpeg", "ts": "video/mp2t"}
VIDEO_CHUNK_SIZE = 1024 * 1024


def video_media_type(file: str) -> Optional[str]:
    last_dot = file.rfind(".")
    if last_dot > 0:
        ext = file[last_dot + 1 :]
        if ext in VIDEO_MEDIA_TYPES:
            return VIDEO_MEDIA_TYPES[ext]
    return None


def media_file_path(group: str, path: str) -> Optional[Path]:
    dirs = get_storage_group_dirs(group)
    if dirs:
        for dir in dirs:
            file_path = Path(f"{dir}/{path}")
        if file_path.exists():
            return file_path
    return None
