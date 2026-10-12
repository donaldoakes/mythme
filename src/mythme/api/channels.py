from fastapi import APIRouter
from mythme.model.program import Channel
from mythme.data.channels import ChannelData

router = APIRouter()


@router.get("/channels")
def get_channels() -> list[Channel]:
    return ChannelData().get_channels()


@router.get("/channel-groups")
def get_channel_groups() -> list[str]:
    return ChannelData().get_channel_groups()
