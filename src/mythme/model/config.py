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
class MythmeConfig:
    mythme_dir: str
    database: DbConnectConfig
    mythtv: MythtvConfig
