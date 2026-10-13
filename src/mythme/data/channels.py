import os
import time
from typing import Optional
from mythme.model.channel import Channel, ChannelGroup, ChannelIcon
from mythme.utils.db import get_connection
from mythme.utils.mythtv import get_channel_icon
from mythme.utils.config import config
from mythme.utils.log import logger


class ChannelData:
    select = "SELECT channel.chanid, channel.channum, channel.callsign, channel.name, channel.icon"
    tables = "FROM channel"
    clause = "WHERE visible > 0 AND deleted is NULL"
    sort = "ORDER BY CONVERT(channum, UNSIGNED) asc"

    @staticmethod
    def to_channel(row: dict) -> Channel:
        channel = Channel(
            id=row["chanid"],
            number=row["channum"],
            callsign=row["callsign"],
            name=row["name"],
        )

        if row["icon"]:
            channel.icon = ChannelIcon(file=row["icon"])
            try:
                channel.icon.shade = row["icon"].split("_")[1]
            except IndexError:
                logger.debug(f"Cannot determine icon shade: {row[4]}")

        return channel

    def __init__(self):
        self.icons_dir = f"{config.mythme_dir}/icons"
        os.makedirs(self.icons_dir, exist_ok=True)

    def get_channels(self, channel_group: Optional[str] = None) -> list[Channel]:
        clause = ChannelData.clause
        params: list[str] = []
        if channel_group:
            clause += "\nAND chanid IN (SELECT chanid FROM channelgroup, channelgroupnames WHERE channelgroup.grpid = channelgroupnames.grpid AND channelgroupnames.name = %s)"  # noqa: E501
            params.append(channel_group)
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = f"{ChannelData.select}\n{ChannelData.tables}\n{clause}\n{ChannelData.sort}"
                cursor.execute(sql, params)
                return [self.to_channel(row) for row in cursor.fetchall()]

    def get_channel_groups(self) -> list[str]:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name from channelgroupnames")
                return [row[0] for row in cursor.fetchall()]

    def get_channel_group(self, channel_group_name: str) -> Optional[ChannelGroup]:
        with get_connection() as conn:
            group_id = 0
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT grpid from channelgroupnames WHERE name = %s",
                    [channel_group_name],
                )
                rows = cursor.fetchone()
                if not rows:
                    return None
                group_id = rows[0]
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT channel.callsign FROM channel, channelgroup WHERE channel.chanid = channelgroup.chanid AND channelgroup.grpid = %s",  # noqa: E501
                    [group_id],
                )
                rows = cursor.fetchall()
                return ChannelGroup(
                    name=channel_group_name,
                    channels=[row[0] for row in rows],
                )

    def load_icons(self):
        before = time.time()
        logger.info("Loading channel icons...")

        channels = self.get_channels()
        for channel in channels:
            if channel.icon:
                icon_file = f"{self.icons_dir}/{channel.icon.file}"
                if not os.path.isfile(icon_file):
                    icon = get_channel_icon(channel.id)
                    if icon:
                        with open(icon_file, "wb") as f:
                            f.write(icon)

        logger.info(
            f"Loaded {len(channels)} channel icons in: {(time.time() - before):.2f} seconds"
        )
