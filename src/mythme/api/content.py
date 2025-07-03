from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import Response, StreamingResponse
from httpx import AsyncClient
from mythme.utils.config import config
from mythme.utils.log import logger
from mythme.utils.media import VIDEO_CHUNK_SIZE, media_file_path, video_media_type

router = APIRouter()

# TODO: file can be a path


@router.get("/files/{path:path}")
async def receive_file(path: str, group: str):
    async def stream_response():
        async with AsyncClient() as client:
            async with client.stream(
                "GET",
                f"{config.mythtv_api_base}/Content/GetFile?FileName={path}&StorageGroup={group}",
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
    st, en = range.replace("bytes=", "").split("-")
    start = int(st)
    end = int(en) if en else start + VIDEO_CHUNK_SIZE

    video_path = media_file_path(group, path)
    if not video_path:
        raise HTTPException(
            status_code=404, detail=f"Group:File not found: {group}:{path}"
        )
    media_type = video_media_type(path)
    if not media_type:
        raise HTTPException(status_code=400, detail=f"Unknown media type: {path}")
    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            "Content-Range": f"bytes {str(start)}-{str(end)}/{filesize}",
            "Accept-Ranges": "bytes",
        }
        return Response(data, status_code=206, headers=headers, media_type=media_type)
