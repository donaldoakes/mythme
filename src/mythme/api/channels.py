from fastapi import APIRouter
from mythme.data.channels import ChannelData
from mythme.model.program import Channel

router = APIRouter()


@router.get("/channels")
def get_channels() -> list[Channel]:
    return ChannelData().get_channels()
