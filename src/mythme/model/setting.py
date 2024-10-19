from dataclasses import dataclass


@dataclass
class Setting:
    name: str
    value: str
    host: str
