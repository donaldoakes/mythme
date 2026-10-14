from typing import Optional
from fastapi import APIRouter, HTTPException
from mythme.model.api import MessageResponse
from mythme.model.channel import Channel, ChannelGroup
from mythme.data.channels import ChannelData

router = APIRouter()


@router.get("/channels")
def get_channels(channel_group: Optional[str] = None) -> list[Channel]:
    return ChannelData().get_channels(channel_group)


@router.get("/channel-groups")
def get_channel_groups() -> list[str]:
    return ChannelData().get_channel_groups()


@router.get("/channel-groups/{channel_group_name}")
def get_channel_group(channel_group_name: str) -> ChannelGroup:
    channel_group = ChannelData().get_channel_group(channel_group_name)
    if not channel_group:
        raise HTTPException(status_code=404)
    return channel_group


@router.post("/channel-groups")
def add_channel_group(channel_group: ChannelGroup) -> MessageResponse:
    channel_data = ChannelData()
    if channel_data.get_group_id(channel_group.name):
        raise HTTPException(
            status_code=409,
            detail=f"Channel group already exists: {channel_group.name}",
        )
    ChannelData().insert_channel_group(channel_group)
    return MessageResponse(message=f"Channel group added: {channel_group.name}")


@router.put("/channel-groups/{channel_group_name}")
def update_channel_group(
    channel_group_name: str, channel_group: ChannelGroup
) -> MessageResponse:
    if channel_group_name != channel_group.name:
        raise HTTPException(status_code=400, detail="Channel group name mismatch")
    if ChannelData().update_channel_group(channel_group):
        return MessageResponse(message=f"Channel group updated: {channel_group_name}")
    raise HTTPException(status_code=404)


@router.delete("/channel-groups/{channel_group_name}")
def delete_channel_group(channel_group_name: str):
    if ChannelData().delete_channel_group(channel_group_name):
        return MessageResponse(message=f"Channel group deleted: {channel_group_name}")
    raise HTTPException(status_code=404)
