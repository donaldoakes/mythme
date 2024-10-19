import os
import time
from mythme.model.channel import Channel, ChannelIcon
from mythme.utils.db import get_connection
from mythme.utils.mythtv import get_channel_icon
from mythme.utils.config import config
from mythme.utils.log import logger


class ChannelData:
    select = """SELECT chanid, channum, callsign, name, icon
FROM channel
WHERE visible > 0
AND DELETED is NULL
ORDER BY CONVERT(channum, UNSIGNED) asc"""

    def __init__(self):
        self.icons_dir = f"{config.mythme_dir}/icons"
        os.makedirs(self.icons_dir, exist_ok=True)

    def get_channels(self) -> list[Channel]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(ChannelData.select)
                return [self.to_channel(row) for row in cursor.fetchall()]

    def to_channel(self, row: dict) -> Channel:
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
