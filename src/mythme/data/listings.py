from datetime import datetime, UTC, timedelta
from typing import Optional
from mythme.data.channels import ChannelData
from mythme.data.programs import ProgramData
from mythme.model.channel import Channel
from mythme.model.listing import ChannelListings, Listing
from mythme.utils.db import get_connection
from mythme.utils.log import logger


class ListingsData:
    fields = """channel.chanid, channel.channum, channel.callsign, channel.name, channel.icon,
program.title, program.subtitle, program.starttime, program.endtime, program.category_type,
CONVERT(program.airdate USING utf8) as year, program.stars, program.originalairdate"""
    tables = "FROM channel, program"
    clause = "WHERE channel.chanid = program.chanid AND channel.visible > 0"

    def get_listings(
        self, channel_group: Optional[str] = None, end_dt: Optional[str] = None
    ) -> list[ChannelListings]:
        fields = ListingsData.fields
        tables = ListingsData.tables
        clause = ListingsData.clause
        clause += (
            "\nAND program.endtime >= "
            + f"'{datetime.now(UTC).isoformat(timespec='seconds')}.000Z'"
        )
        if end_dt:
            clause += "\nAND program.endtime <= " + f"'{end_dt}'"

        channel_group_channels: list[Channel] = []
        params: list[str] = []
        if channel_group:
            channel_group_channels = ChannelData().get_channels(channel_group)
            clause += "\nAND channel.chanid IN (SELECT chanid FROM channelgroup, channelgroupnames WHERE channelgroup.grpid = channelgroupnames.grpid AND channelgroupnames.name = %s)"  # noqa: E501
            params.append(channel_group)

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = f"SELECT {fields}\n{tables}\n{clause}"
                sql += "\nORDER BY channel.channum + 0, program.starttime"
                logger.debug(f"Listings SQL: {sql}")
                logger.debug(f"Listings params: {repr(params)}")
                cursor.execute(sql, params)
                channum = "0"
                listings: list[ChannelListings] = []
                channel_listings: Optional[ChannelListings] = None
                for row in cursor.fetchall():
                    if not channel_listings or row["channum"] != channum:
                        channel_listings = ChannelListings(
                            channel=ChannelData.to_channel(row),
                            listings=[],
                        )
                        listings.append(channel_listings)
                        channum = row["channum"]

                    channel_listings.listings.append(ListingsData.to_listing(row))

                # fill in any channels from the group that have no listings
                for channel in channel_group_channels:
                    if not any(
                        cl.channel.callsign == channel.callsign for cl in listings
                    ):
                        channel_listings = ChannelListings(
                            channel=channel,
                            listings=[  # a single one-hour listing starting from the most recent half-hour
                                Listing(
                                    title="Unknown",
                                    subtitle=None,
                                    type="",
                                    channel=channel.callsign,
                                    start=ProgramData.round_to_half_hour(
                                        datetime.now()
                                    ),
                                    end=ProgramData.round_to_half_hour(datetime.now())
                                    + timedelta(hours=1),
                                    year=None,
                                    rating=0,
                                    aired=None,
                                )
                            ],
                        )
                        listings.append(channel_listings)
                if len(channel_group_channels):
                    listings.sort(key=lambda cl: int(cl.channel.number))

                return listings

    @staticmethod
    def to_listing(row: dict) -> Listing:
        return Listing(
            title=row["title"],
            subtitle=row["subtitle"] or None,
            type=row["category_type"],
            channel=row["callsign"],
            start=ProgramData.from_local_timezone(row["starttime"]),
            end=ProgramData.from_local_timezone(row["endtime"]),
            year=int(row["year"]) if row["year"] else None,
            rating=row["stars"] * 5,
            aired=row["originalairdate"] or None,
        )
