import json
from datetime import datetime, timezone, UTC
from mythme.model.channel import ChannelIcon
from mythme.model.query import Criterion, DbQuery, Query
from mythme.model.program import Channel, Program, ProgramsResponse
from mythme.utils.db import get_connection
from mythme.utils.log import logger


# without CONVERT, 0000 in airdate throws an error
class ProgramData:
    fields = """channel.chanid, channel.channum, channel.callsign, channel.name, channel.icon,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type,
CONVERT(program.airdate USING utf8) as year, program.stars, program.season, program.episode, program.originalairdate,
(SELECT COUNT(*) FROM credits WHERE credits.chanid = program.chanid AND credits.starttime = program.starttime) AS credits"""  # noqa: E501
    tables = "FROM channel, program"
    clause = "WHERE channel.chanid = program.chanid AND channel.visible > 0"

    # TODO pagination and sorting
    def get_programs(self, query: Query, with_genres: bool = False) -> ProgramsResponse:
        fields = ProgramData.fields
        tables = ProgramData.tables
        clause = ProgramData.clause
        if with_genres:
            fields += ", programgenres.genre"
            tables += ", programgenres"
            clause += " AND programgenres.chanid = program.chanid AND programgenres.starttime = program.starttime AND programgenres.relevance != 0"  # noqa: E501
        clause += (
            "\nAND program.endtime >= "
            + f"'{datetime.now(UTC).isoformat(timespec="seconds")}.000Z'"
        )

        params: list[str] = []
        for criterion in query.criteria:
            clause += f" AND {self.colname(criterion.name)} {criterion.operator} "
            val = self.colval(criterion)
            if isinstance(val, list):
                if criterion.operator == "IN":
                    clause += "(" + ", ".join(["%s"] * len(val)) + ")"
                elif criterion.operator == "BETWEEN":
                    clause += "%s AND %s"
                params.extend(val)
            else:
                clause += "%s"
                params.append(val)

        total = 0

        with get_connection() as conn:
            with conn.cursor() as cursor:
                count_sql = f"SELECT COUNT(*) {tables} {clause}"
                logger.debug(f"Program count SQL: {count_sql}")
                logger.debug(f"Program count params: {repr(params)}")
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
            with conn.cursor(dictionary=True) as cursor:
                sql = f"SELECT {fields}\n{tables}\n{clause}"
                sort_col = self.colsort(query.sort.name)
                sql += f"\nORDER BY {sort_col} {query.sort.order}"
                if sort_col == "airdate":
                    sql += f", originalairdate {query.sort.order}"
                if sort_col != "starttime":
                    sql += ", starttime"
                sql += f"\nLIMIT {query.paging.limit} OFFSET {query.paging.offset}"
                logger.debug(f"Programs SQL: {sql}")
                logger.debug(f"Programs params: {repr(params)}")
                cursor.execute(sql, params)
                response = ProgramsResponse(
                    programs=[self.to_program(row) for row in cursor.fetchall()],
                    total=total,
                )
                if query.debug:
                    response.query = DbQuery(sql=sql, params=params)

                return response

    def get_categories(self) -> list[str]:
        sql = "SELECT DISTINCT category FROM program ORDER BY category"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]

    def get_genres(self) -> list[str]:
        sql = """SELECT DISTINCT(programgenres.genre) FROM programgenres WHERE programgenres.relevance != 0 ORDER BY programgenres.genre"""  # noqa: E501
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                return [row["genre"] for row in cursor.fetchall()]

    def colname(self, name: str) -> str:
        if name == "channel":
            return "callsign"
        elif name == "channum":
            return "channum"
        elif name == "start":
            return "starttime"
        elif name == "end":
            return "endtime"
        elif name == "type":
            return "category_type"
        elif name == "year":
            return "airdate"
        elif name == "rating":
            return "stars"

        if name not in Program.model_fields.keys():
            raise ValueError(f"Invalid criterion: {name}")
        return name

    def colsort(self, name: str) -> str:
        sort = self.colname(name)
        if sort == "channum":
            sort = "CAST(channum as unsigned)"
        return sort

    def colval(self, criterion: Criterion) -> str | list[str]:
        if criterion.name in [
            "channel",
            "title",
            "description",
            "type",
            "category",
        ] and (
            criterion.operator != "="
            and criterion.operator != "IN"
            and criterion.operator != "LIKE"
        ):
            raise ValueError(
                f"Invalid operator for {criterion.name}: {criterion.operator}"
            )
        # TODO BETWEEN for rating
        if criterion.name == "rating":
            if not criterion.value.replace(".", "").isnumeric():
                raise ValueError(f"Invalid value for rating: {criterion.value}")
            return str(float(criterion.value) / 5)
        if criterion.operator == "IN" or criterion.operator == "BETWEEN":
            try:
                lst = json.loads(criterion.value)
                if not isinstance(lst, list):
                    raise ValueError(
                        f"Invalid value for {criterion.name} {criterion.operator}: {criterion.value}"
                    )
                return lst
            except json.JSONDecodeError:
                raise ValueError(
                    f"Invalid value for {criterion.name} {criterion.operator}: {criterion.value}"
                )
        return criterion.value

    def to_program(self, row: dict) -> Program:
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
                pass

        return Program(
            channel=channel,
            title=row["title"],
            subtitle=row["subtitle"] or None,
            start=self.from_local_timezone(row["starttime"]),
            end=self.from_local_timezone(row["endtime"]),
            description=row["description"] or None,
            category=row["category"],
            type=row["category_type"],
            year=int(row["year"]) if row["year"] else None,
            rating=row["stars"] * 5,
            season=row["season"] or None,
            episode=row["episode"] or None,
            aired=row["originalairdate"] or None,
            genre=row["genre"] if "genre" in row else None,
            credits=row["credits"] or None,
        )

    def from_local_timezone(self, dt: datetime) -> datetime:
        return dt.replace(tzinfo=timezone.utc)
