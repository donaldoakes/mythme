from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from mythme.utils.config import config

router = APIRouter()


@router.get("/files/{file}")
async def receiveFile(file: str, group: str):
    async def stream_response():
        async with AsyncClient() as client:
            async with client.stream(
                "GET",
                f"{config.mythtv_api_base}/Content/GetFile?FileName={file}&StorageGroup={group}",
            ) as response:
                # if response.status_code != 200:
                #     response_text = await response.aread()
                #     logger.error(f"Relay request failed with status code {response.status_code}: {response_text.decode()}")
                #     raise HTTPException(status_code=response.status_code, detail=response_text.decode())

                # logger.debug(f"Received response with status code {response.status_code}.")
                async for chunk in response.aiter_bytes():
                    if chunk:
                        # logger.debug(f"Received chunk: {chunk.decode()}")
                        yield chunk

    return StreamingResponse(
        stream_response(),
        status_code=200,
        media_type="application/octet-stream",
    )

    # response = await client.get(
    #     f"{config.mythtv_api_base}/Content/GetFile?FileName={file}&StorageGroup={group}"
    # )

    # async for dataBytes in response.aiter_bytes():
    #     yield dataBytes
