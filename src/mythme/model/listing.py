from typing import Optional, Union

from datetime import datetime
from pydantic import BaseModel
from mythme.model.channel import Channel
from mythme.model.program import Program


class Listing(BaseModel):
    channel: Channel
    programs: list["Program"]
