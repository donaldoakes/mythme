from typing import Optional
from fastapi import APIRouter
from mythme.model.channel import Channel
from mythme.model.channel import ChannelGroup
from mythme.data.channels import ChannelData

router = APIRouter()


@router.get("/channels")
def get_channels(channel_group: Optional[str] = None) -> list[Channel]:
    return ChannelData().get_channels(channel_group)


@router.get("/channel-groups")
def get_channel_groups() -> list[str]:
    return ChannelData().get_channel_groups()


@router.get("/channel-groups/{channel_group_name}")
def get_channel_group(channel_group_name: str) -> Optional[ChannelGroup]:
    return ChannelData().get_channel_group(channel_group_name)
