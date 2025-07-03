from typing import Optional
from pathlib import Path

# TODO: more comprehensive
AUDIO_MEDIA_TYPES = {"mp3": "audio/mpeg"}

# TODO: more comprehensive
VIDEO_MEDIA_TYPES = {"mp4": "video/mp4", "mpg": "video/mpeg", "ts": "video/mp2t"}
VIDEO_CHUNK_SIZE = 1024 * 1024


def video_media_type(file: str) -> Optional[str]:
    last_dot = file.rfind(".")
    if last_dot > 0:
        return file[last_dot]
    return None


# TODO: obtain by retrieving GetHostName, GetStorageGroupDirs
STORAGE_GROUP_DIRS = {
    "RECORDINGS": "/mnt/mythnas/media/myth_store",
    "VIDEOS": "/mnt/mythnas/media/mpg",
    "MUSIC": "/mng/mythnas/media/mp3",
}


def media_file_path(group: str, path: str) -> Optional[Path]:
    if group in STORAGE_GROUP_DIRS:
        file_path = Path(f"{STORAGE_GROUP_DIRS[group]}/{path}")
        if file_path.exists():
            return file_path
    return None
