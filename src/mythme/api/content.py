from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from mythme.utils.config import config
from mythme.utils.log import logger
from mythme.utils.media import (
    get_video_stream,
    media_file_path,
    video_media_type,
)

router = APIRouter()


@router.get("/files/{path:path}")
async def receive_file(path: str, group: str):
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

    return StreamingResponse(
        stream_response(),
        status_code=200,
        media_type="application/octet-stream",
    )


@router.get("/videos/{path:path}")
async def stream_video(path: str, group: str, range: str = Header(None)):
    """Does not support seek. Browser cannot play video/mp2t (ts) streams."""
    video_path = media_file_path(group, path)
    if not video_path:
        raise HTTPException(
            status_code=404, detail=f"Group:File not found: {group}:{path}"
        )
    media_type = video_media_type(path)
    if not media_type:
        raise HTTPException(status_code=400, detail=f"Unknown media type: {path}")

    return StreamingResponse(get_video_stream(str(video_path)), media_type=media_type)
