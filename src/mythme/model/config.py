from typing import Optional
from dataclasses import dataclass


@dataclass
class DbConnectConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass
class MythtvConfig:
    api_base: str
    categories: dict[str, str]
    storage_groups: dict[str, list[str]]


@dataclass
class DailyVidConfig:
    psv_file: str


@dataclass
class ChatConfig:
    anthropic_version: str
    bedrock_models: dict[str, str]
    mythme_models: dict[str, str]
    max_tokens: int


@dataclass
class MythmeConfig:
    mythme_dir: str
    database: DbConnectConfig
    mythtv: MythtvConfig
    chat: ChatConfig
    dailyvid: Optional[DailyVidConfig] = None
