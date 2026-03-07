import aiofiles
from typing import Optional
from pathlib import Path
from fastapi import HTTPException, status
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


def get_range(range_header: str, file_size: int) -> tuple[int, int]:
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range: {range_header})",
        )

    try:
        asked = range_header.replace("bytes=", "").split("-")
        start = int(asked[0]) if asked[0] != "" else 0
        end = int(asked[1]) if asked[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()

    return start, end


async def send_bytes_range_requests(
    file_path: str, start: int, end: int, chunk_size: int
):
    async with aiofiles.open(file_path, mode="rb") as f:
        await f.seek(start)
        pos = await f.tell()
        while pos <= end:
            read_size = min(chunk_size, end + 1 - pos)
            chunk = await f.read(read_size)
            if not chunk:
                break
            pos += len(chunk)
            yield chunk
