from dataclasses import dataclass
from typing import Literal

Role = Literal["director", "actor", "presenter", "producer", "guest", "guest_star"]


@dataclass
class Credit:
    name: str
    role: Role
