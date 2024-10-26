import os
import socket
from pathlib import Path
from typing import Any, Optional
import xml.etree.ElementTree as ET
import mariadb
from dotenv import load_dotenv
from yaml import safe_load
from mythme.model.config import DbConnectConfig, MythmeConfig
from mythme.model.setting import Setting
from mythme.utils.log import logger

load_dotenv()


def required(name: str, dict: dict[str, Any], default: Optional[str] = None) -> Any:
    if name not in dict:
        if default is not None:
            return default
        raise ValueError(f"Required key {name} not found in config")
    return dict[name]


def to_setting(row: dict) -> Setting:
    return Setting(name=row["value"], value=row["data"], host=row["hostname"])


def load_config() -> MythmeConfig:
    mythme_dir = Path(os.getenv("MYTHME_DIR", "~/.mythme")).expanduser()
    os.makedirs(mythme_dir, exist_ok=True)
    logger.info(f"Using mythme directory: {mythme_dir}")

    cfg: dict[str, Any] = {}
    yaml_file = f"{mythme_dir}/mythme.yaml"
    if not Path(yaml_file).is_file():
        yaml_file = f"{mythme_dir}/mythme.yml"

    if Path(yaml_file).is_file():
        logger.info(f"Loading mythme config from file: {yaml_file}")
        with open(yaml_file, "r") as f:
            cfg = safe_load(f.read()) or {}

    db_config: Optional[DbConnectConfig] = None
    if "database" in cfg:
        database = cfg["database"]
        db_config = DbConnectConfig(
            host=required("host", database),
            port=required("port", database),
            username=required("username", database),
            password=required("password", database),
            database=required("database", database),
        )
    else:
        # try ~/.mythtv/config.xml
        mythtv_config = Path("~/.mythtv/config.xml").expanduser()
        if Path(mythtv_config).is_file():
            logger.info(f"Loading DB config from file: {mythtv_config}")
            with open(mythtv_config, "r") as f:
                mythtv_cfg = f.read()
                root = ET.fromstring(mythtv_cfg)
                database = root.find("Database")
                if database:
                    db_config = DbConnectConfig(
                        host=database.findtext("Host"),
                        port=int(database.findtext("Port")),
                        username=database.findtext("UserName"),
                        password=database.findtext("Password"),
                        database=database.findtext("DatabaseName"),
                    )

    if db_config is None:
        raise ValueError("No MythTV database config found")
    else:
        logger.debug(f"Loaded DB config: {db_config}")

    api_base = cfg.get("mythtv_api_base") if "mythtv_api_base" in cfg else None
    if api_base is None:
        conn = mariadb.connect(
            host=db_config.host,
            port=db_config.port,
            database=db_config.database,
            user=db_config.username,
            password=db_config.password,
        )
        with conn.cursor(dictionary=True) as cursor:
            settings_select = """SELECT value, data, hostname FROM settings
WHERE value in ('BackendStatusPort', 'BackendServerAddr')"""
            cursor.execute(settings_select)
            settings = [to_setting(row) for row in cursor.fetchall()]

            def get_setting(name: str, host: Optional[str] = None) -> Optional[Setting]:
                return next(
                    (s for s in settings if s.name == name and s.host == host), None
                )

            # hostname match
            host = get_setting("BackendServerAddr", socket.gethostname())
            port = get_setting("BackendStatusPort", socket.gethostname())
            # localhost match
            if not host:
                host = get_setting("BackendServerAddr", "localhost")
            if not port:
                port = get_setting("BackendStatusPort", "localhost")
            # default match
            if not host:
                host = get_setting("BackendServerAddr")
            if not port:
                port = get_setting("BackendStatusPort")

            if host and port:
                api_base = f"http://{host.value}:{port.value}"
                logger.info(f"Using MythTV API base: {api_base} from DB settings")

    if api_base is None:
        raise ValueError("No MythTV API base URL found")

    mythme_config = MythmeConfig(
        mythme_dir=f"{mythme_dir}",
        database=db_config,
        mythtv_api_base=api_base,
    )

    logger.debug(f"Loaded mythme config: {mythme_config}")

    return mythme_config


config: MythmeConfig = load_config()
