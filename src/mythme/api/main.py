import os
import platform
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mythme.data.recordings import RecordingsData
from mythme.data.channels import ChannelData
from mythme.utils.log import logger
from mythme.api import channels
from mythme.api import programs
from mythme.api import queries
from mythme.api import recordings
from mythme.api import credits

logger.info(f"Python: {platform.python_version()}")

recording_data = RecordingsData()
channels_data = ChannelData()


async def periodic_reload(after: int = 600):
    """Periodically reload recordings data
    :param after: seconds before next reloads
    """
    while True:
        await asyncio.sleep(after)
        recording_data.load()


@asynccontextmanager
async def lifespan(app: FastAPI):
    recording_data.load()
    channels_data.load_icons()
    asyncio.create_task(periodic_reload())
    yield


router = APIRouter(prefix="/api")

router.include_router(channels.router)
router.include_router(programs.router)
router.include_router(queries.router)
router.include_router(recordings.router)
router.include_router(credits.router)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.mount(
    "/mythme",
    StaticFiles(packages=[("mythme", "ui")], html=True),
    name="ui",
)
app.mount(
    "/icons",
    StaticFiles(directory=f"{channels_data.icons_dir}", html=False),
    name="icons",
)
