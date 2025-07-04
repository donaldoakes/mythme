import requests
from typing import Optional, Literal
from dotenv import load_dotenv
from mythme.utils.config import config
from mythme.utils.log import logger

load_dotenv()

ApiMethod = Literal["GET", "POST"]


def api_call(
    path: str, method: ApiMethod = "GET", params: Optional[dict[str, str]] = None
) -> Optional[dict]:
    """MythTV API request.

    :param path: Resource path
    :type path: str
    :param method: HTTP method, defaults to "GET"
    :type method: str, optional
    :param params: Query parameters, defaults to None
    :type params: dict, optional
    :return: Parsed response body, or None if not found
    :rtype: dict
    """

    url = f"{config.mythtv.api_base}/{path}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    logger.debug(f"{method}: {url}")
    headers = {"Accept": "application/json"}

    if method == "POST":
        response = requests.post(url, headers=headers)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        logger.debug(f"{method} {url} not found: {response.text}")
        return None
    else:
        logger.debug(f"{method} {url} failed: {response.text}")
        raise Exception(f"{method} {url} failed: {response.status_code}")


def get_channel_icon(channel_id: int) -> Optional[bytes]:
    """Retrieve channel icon content.

    :param channel_id: channel id
    :type channel_id: int
    :return: icon content
    :rtype: bytes if found, None otherwise
    """

    url = f"{config.mythtv.api_base}/Guide/GetChannelIcon?ChanId={channel_id}"
    logger.debug(f"Retrieving icon for channel_id: {channel_id}")

    response = requests.get(url)

    if response.status_code == 200:
        return response.content
    elif response.status_code == 404:
        logger.debug(f"Channel icon not found at {url}: {response.text}")
        return None
    else:
        logger.debug(f"Channel icon retrieval at {url} failed: {response.text}")
        raise Exception(f"{url} failed: {response.status_code}")


myth_hostname: Optional[str] = None


def get_myth_hostname() -> Optional[str]:
    global myth_hostname
    if not myth_hostname:
        res = api_call("Myth/GetHostName")
        if res and "String" in res:
            myth_hostname = res["String"]
    return myth_hostname


def get_storage_group_dirs(group: str) -> Optional[list[str]]:
    if group in config.mythtv.storage_groups:
        return config.mythtv.storage_groups[group]
    hostname = get_myth_hostname()
    if hostname:
        res = api_call(f"/Myth/GetStorageGroupDirs?GroupName={group}")
        if (
            res
            and "StorageGroupDirList" in res
            and "StorageGroupDirs" in res["StorageGroupDirList"]
        ):
            sg_dirs = res["StorageGroupDirList"]["StorageGroupDirs"]
            dirs = [
                dir["DirName"]
                for dir in filter(lambda sgd: sgd["HostName"] == hostname, sg_dirs)
            ]
            config.mythtv.storage_groups[group] = dirs
            return dirs
    return None
