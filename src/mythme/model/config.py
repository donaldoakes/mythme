from dataclasses import dataclass


@dataclass
class DbConnectConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass
class MythmeConfig:
    mythme_dir: str
    database: DbConnectConfig
    mythtv_api_base: str
