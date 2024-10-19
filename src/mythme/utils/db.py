import mariadb
from mythme.utils.config import config


def get_connection() -> mariadb.Connection:
    return mariadb.connect(
        host=config.database.host,
        port=config.database.port,
        database=config.database.database,
        user=config.database.username,
        password=config.database.password,
    )
