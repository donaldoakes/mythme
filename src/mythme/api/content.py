import os
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from typing_extensions import Optional
from mythme.utils.config import config
from mythme.utils.log import logger
from mythme.utils.media import (
    get_range,
    media_file_path,
    send_bytes_range_requests,
    video_media_type,
)

router = APIRouter()


@router.get("/files/{path:path}")
async def receive_file(path: str, group: str, download: Optional[str] = None):
    async def stream_response():
        async with AsyncClient() as client:
            async with client.stream(
                "GET",
                f"{config.mythtv.api_base}/Content/GetFile?FileName={path}&StorageGroup={group}",
            ) as response:
                if response.status_code != 200:
                    response_text = await response.aread()
                    logger.error(
                        f"MythTV file request failed ({response.status_code}): {response_text.decode()}"
                    )
                    raise HTTPException(
                        status_code=response.status_code, detail=response_text.decode()
                    )
                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk

    headers = {}
    if download:
        headers = {"content-disposition": f"attachment; filename={download}"}
    return StreamingResponse(
        stream_response(),
        status_code=200,
        media_type="application/octet-stream",
        headers=headers,
    )


@router.get("/media/videos/{path:path}")
async def stream_video(path: str, range: str = Header(None)):
    """Browser cannot play video/mp2t (ts) streams."""
    video_path = media_file_path("Videos", path)
    if not video_path:
        raise HTTPException(status_code=404, detail=f"Video not found: {path}")
    media_type = video_media_type(path)
    if not media_type:
        raise HTTPException(status_code=400, detail=f"Unknown media type: {path}")

    file_size = os.path.getsize(video_path)

    headers = {
        "content-type": media_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, "
            "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK

    if range is not None:
        start, end = get_range(range, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        send_bytes_range_requests(str(video_path), start, end, 1024 * 1024),
        headers=headers,
        status_code=status_code,
    )
