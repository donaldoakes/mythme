from typing import Optional, Literal
from pydantic import BaseModel

IconShade = Literal["light", "dark", "white", "gray"]


class ChannelIcon(BaseModel):
    file: str
    shade: Optional[IconShade] = None
    """Based on XMLTV naming convention"""


class Channel(BaseModel):
    id: int
    number: int
    callsign: str
    name: str
    icon: Optional[ChannelIcon] = None
