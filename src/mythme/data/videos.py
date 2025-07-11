import os
import time
import textwrap
from datetime import datetime
from typing import Optional, Tuple, Union
from mythme.model.credit import Credit
from mythme.model.query import Query, Sort
from mythme.model.video import Video, VideosResponse, WebRef
from mythme.utils.db import get_connection
from mythme.utils.media import media_file_path
from mythme.utils.mythtv import (
    api_call,
    api_update,
    get_myth_hostname,
    get_storage_group_dirs,
    paging_params,
)
from mythme.utils.text import gen_hash, trim_article
from mythme.utils.config import config
from mythme.utils.log import logger


class VideoData:
    fields = [
        "host",
        "filename",
        "title",
        "hash",
        "contenttype",
        "year",
        "releasedate",
        "userrating",
        "inetref",
        "coverfile",
        "director",
        "subtitle",
        "collectionref",
        "homepage",
        "rating",
        "length",
        "playcount",
        "season",
        "episode",
        "showlevel",
        "childid",
        "browse",
        "watched",
        "processed",
        "category",
    ]

    values = [f"%({field})s" for field in fields]

    def get_videos(self, query: Query) -> VideosResponse:
        """Uses the MythTV API"""
        before = time.time()
        result = api_call("Video/GetVideoList" + paging_params(query))
        total = 0
        if (
            result
            and "VideoMetadataInfoList" in result
            and "VideoMetadataInfos" in result["VideoMetadataInfoList"]
        ):
            videos = [
                self.to_video(vid)
                for vid in result["VideoMetadataInfoList"]["VideoMetadataInfos"]
            ]
            total = result["VideoMetadataInfoList"]["TotalAvailable"]
            logger.info(
                f"Retrieved {len(videos)} videos in: {(time.time() - before):.2f} seconds\n"
            )
        else:
            raise Exception("Failed to retrieve videos")

        if query.sort.name and query.sort.name != "id":
            videos.sort(
                key=lambda vid: self.sort(vid, query.sort),
                reverse=True if query.sort.order == "desc" else False,
            )

        return VideosResponse(videos=videos, total=total)

    def get_video(self, id: int) -> Optional[Video]:
        """Uses the MythTV API"""
        res = api_call(f"Video/GetVideo?Id={id}")
        if (
            res
            and "VideoMetadataInfo" in res
            and "Id" in res["VideoMetadataInfo"]
            and res["VideoMetadataInfo"]["Id"]
        ):
            return self.to_video(res["VideoMetadataInfo"])
        return None

    def get_video_file(self, title: str, category: str, medium: str) -> Optional[str]:
        """Checks the file system, returns the full file path"""
        filepath = self.get_filepath(title, category, medium)
        if filepath:
            path = media_file_path("Videos", filepath)
            if path:
                return str(path)
        return None

    def get_filepath(
        self, title: str, category: Optional[str] = None, medium: Optional[str] = None
    ) -> Optional[str]:
        catdir = self.get_category_dir(category)
        if not catdir:
            logger.error(f"No category dir: {category} for '{title}'")
            return None
        if not medium:
            logger.warning(f"Missing medium for '{title}'")
            return None
        elif medium == "DVD":
            logger.debug(f"Skipping DVD title '{title}'")
            return None
        ext = medium.lower()
        return f"{catdir}/{title}.{ext}"

    def update_video(self, video: Video) -> bool:
        """Uses the MythTV API"""
        return api_update("Video/UpdateVideoMetadata", params=self.from_video(video))

    def delete_video_metadata(self) -> int:
        """Deletes all video metadata directly from the database"""
        rows = 0
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM videometadatacast")
                cursor.execute("DELETE FROM videometadata")
                rows = cursor.rowcount
                cursor.execute("DELETE FROM videocast")
        return rows

    def get_category_dir(self, category: Optional[str] = None) -> Optional[str]:
        if category and category in config.mythtv.categories:
            return f"{config.mythtv.categories[category]}"
        else:
            return None

    def get_db_filepaths(self) -> dict[str, int]:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                filepaths: dict[str, int] = {}
                cursor.execute("SELECT filename, intid FROM videometadata")
                for filename, intid in cursor.fetchall():
                    filepaths[filename] = intid
                return filepaths

    def get_fs_filepaths(self) -> Optional[list[str]]:
        sg_dirs = get_storage_group_dirs("Videos")
        if sg_dirs is None:
            return None
        logger.info(f"Scanning video storage group directories: {sg_dirs}")
        filepaths: list[str] = []
        for sg_dir in sg_dirs:
            for root, _dirs, files in os.walk(sg_dir):
                for file in files:
                    filepaths.append(os.path.join(root[len(sg_dir) + 1 :], file))
        return filepaths

    def get_insert_sql(self) -> str:
        return f"INSERT INTO videometadata ({", ".join(self.fields)}) VALUES ({", ".join(self.values)})"  # noqa: E501

    def get_update_sql(self) -> str:
        return (
            "UPDATE videometadata SET "
            + ", ".join(
                [f"{field} = {self.values[i]}" for i, field in enumerate(self.fields)]
            )
            + " WHERE filename = %(filename)s"
        )

    def scan_videos(self) -> Optional[Tuple[list[str], list[str]]]:
        """Crawls file system and updates the database. Returns a tuple with added/deleted filepaths."""
        fs_filepaths = self.get_fs_filepaths()
        if fs_filepaths is None:
            return None
        db_filepaths = self.get_db_filepaths()
        deleted: list[str] = []
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for db_filepath in db_filepaths:
                    file_exists = db_filepath in fs_filepaths
                    if not file_exists:
                        logger.info(
                            f"Deleting metadata for unfound file: {db_filepath}"
                        )
                        cursor.execute(
                            "DELETE FROM videometadata WHERE filename = %s",
                            (db_filepath,),
                        )
                        deleted.append(db_filepath)

        added: list[str] = []
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for fs_filepath in fs_filepaths:
                    if fs_filepath not in db_filepaths:
                        logger.info(f"Found new video file: {fs_filepath}")
                        data = (
                            self.base_sql_data(fs_filepath)
                            | self.info_sql_data()
                            | self.unused_sql_data()
                        )
                        sql = self.get_insert_sql()
                        cursor.execute(sql, data)
                        added.append(fs_filepath)
        return (added, deleted)

    def sync_video_metadata(
        self, videos: list[Video]
    ) -> Optional[Tuple[list[str], list[str]]]:
        """Updates matching videos in the database"""
        sg_dirs = get_storage_group_dirs("Videos")
        if sg_dirs is None:
            return None
        updated: list[str] = []
        missing: list[str] = []
        db_filepaths = self.get_db_filepaths()
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for vid in videos:
                    filepath = self.get_filepath(vid.title, vid.category, vid.medium)
                    if not filepath:
                        if vid.medium != "DVD":
                            missing.append(vid.title)
                        continue
                    row_exists = filepath in db_filepaths
                    if row_exists:
                        logger.info(f"Update existing video title: {vid.title}")
                        sql = self.get_update_sql()
                        data = (
                            self.base_sql_data(filepath)
                            | self.info_sql_data(vid)
                            | self.unused_sql_data()
                            | {"contenttype": "MOVIE"}
                        )
                        cursor.execute(sql, data)
                        videoid = db_filepaths[filepath]
                        if vid.credits:
                            actors = [c.name for c in vid.credits if c.role == "actor"]
                            for actor in actors:
                                cursor.execute(
                                    "SELECT intid FROM videocast where cast = %(cast)s",
                                    {"cast": actor},
                                )
                                row = cursor.fetchone()
                                castid = row["intid"] if row else None
                                if not castid:
                                    cursor.execute(
                                        "INSERT INTO videocast (cast) VALUES (%(cast)s)",
                                        {"cast": actor},
                                    )
                                    castid = cursor.lastrowid
                                cursor.execute(
                                    "SELECT 1 FROM videometadatacast WHERE idvideo = %(idvideo)s AND idcast = %(idcast)s",  # noqa: E501
                                    {"idvideo": videoid, "idcast": castid},
                                )
                                if cursor.fetchone() is None:
                                    cursor.execute(
                                        "INSERT INTO videometadatacast (idvideo, idcast) VALUES (%(idvideo)s, %(idcast)s)",  # noqa: E501
                                        {"idvideo": videoid, "idcast": castid},
                                    )

                        updated.append(vid.title)
                    else:
                        logger.info(f"Video missing from database: {filepath}")
                        missing.append(filepath)

        return (updated, missing)

    def sort(self, video: Video, sort: Sort) -> tuple:
        """Sort according to query."""
        if sort.name == "file":
            return (video.file.lower(), video.id)
        elif sort.name == "title":
            title = trim_article(video.title.lower())
            return (title, video.id)
        else:
            raise ValueError(f"Unsupported sort: {sort.name}")

    def get_title(self, file: str) -> str:
        filename = file[file.rindex("/") + 1 :]
        title = filename[: filename.rindex(".")]
        if len(title) > 128:
            title = textwrap.shorten(title, width=128, placeholder="...")
        return title

    def base_sql_data(self, file: str) -> dict[str, Union[str, int, float]]:
        host = get_myth_hostname()
        if not host:
            raise ValueError("MythTV hostname not found")
        return {
            "host": host,
            "filename": file,
            "title": self.get_title(file),
            "hash": gen_hash(file),
            "contenttype": "MUSICVIDEO",
        }

    def info_sql_data(
        self, video: Optional[Video] = None
    ) -> dict[str, Union[str, int, float]]:
        if video:
            coverfile = ""
            if video.poster:
                catdir = self.get_category_dir(video.category)
                if catdir:
                    cov_sg_dirs = get_storage_group_dirs("Coverart")
                    if cov_sg_dirs and len(cov_sg_dirs) > 0:
                        coverfile = f"{cov_sg_dirs[0]}/{catdir}/{video.poster}"
                    else:
                        logger.error("Coverart storage group not found")
                else:
                    logger.error(
                        f"No category dir for '{video.title}': {video.category}"
                    )
            director = ""
            if video.credits:
                directors = [
                    d.name
                    for d in filter(lambda c: c.role == "director", video.credits)
                ]
                if len(directors):
                    director = ", ".join(directors)
            return {
                "year": video.year or 0,
                "releasedate": f"{video.year}-01-01" if video.year else "0000-00-00",
                "userrating": (video.rating or 0) * 2,
                "inetref": video.webref.ref if video.webref else "00000000",
                "coverfile": coverfile,
                "director": director,
            }
        else:
            return {
                "year": 0,
                "releasedate": "0000-00-00",
                "userrating": 0,
                "inetref": "00000000",
                "coverfile": "",
                "director": "",
            }

    def unused_sql_data(self) -> dict[str, Union[str, int, float]]:
        return {
            "subtitle": "",
            "collectionref": -1,
            "homepage": "",
            "rating": "NR",
            "length": 0,
            "playcount": 0,
            "season": 0,
            "episode": 0,
            "showlevel": 1,
            "childid": -1,
            "browse": 1,
            "watched": 0,
            "processed": 0,
            "category": 0,
        }

    # def add_video_from_recording(
    #     self, rec: Recording, category: str
    # ) -> Optional[Video]:
    #     recext = rec.file[rec.file.rindex(".") + 1 :]
    #     video = Video(id="", category=category, title=rec.title, medium=recext.upper())
    #     filepath = self.get_filepath(video.title, video.category, video.medium)
    #     if not filepath:
    #         return None
    #     video.file = filepath
    #     video.year = rec.year
    #     video.credits = rec.credits

    def to_video(self, vid: dict) -> Video:
        video = Video(id=vid["Id"], title=vid["Title"], file=vid["FileName"])
        if "SubTitle" in vid and vid["SubTitle"]:
            video.subtitle = vid["SubTitle"]
        if "ReleaseDate" in vid and vid["ReleaseDate"]:
            video.year = datetime.fromisoformat(vid["ReleaseDate"]).year
        if "Description" in vid and vid["Description"] and vid["Description"] != "None":
            video.description = vid["Description"]
        if "UserRating" in vid and vid["UserRating"]:
            video.rating = vid["UserRating"] / 2
        credits: list[Credit] = []
        if "Director" in vid and vid["Director"] and vid["Director"] != "Unknown":
            credits.append(Credit(name=vid["Director"], role="director"))
        if "Cast" in vid and "CastMembers" in vid["Cast"]:
            for cm in vid["Cast"]["CastMembers"]:
                if "Role" in cm and cm["Role"] == "ACTOR":
                    credits.append(Credit(name=cm["Name"], role="actor"))
        if len(credits):
            video.credits = credits
        if "Coverart" in vid and vid["Coverart"]:
            video.poster = vid["Coverart"][vid["Coverart"].rindex("/") + 1 :]
        if "Inetref" in vid and vid["Inetref"] and vid["Inetref"] != "00000000":
            video.webref = WebRef(site="imdb.com", ref=vid["Inetref"])
        return video

    def from_video(self, video: Video) -> dict:
        vid = {"Id": video.id, "Title": video.title}
        if video.subtitle:
            vid["SubTitle"] = video.subtitle
        if video.year:
            vid["ReleaseDate"] = f"{video.year}-01-01T00:00:00Z"
            vid["Year"] = video.year
        if video.description:
            vid["Plot"] = video.description
        if video.rating:
            vid["UserRating"] = int(video.rating * 2)
        if video.credits:
            actors = [
                a.name for a in filter(lambda c: c.role == "actor", video.credits)
            ]
            if len(actors):
                vid["Cast"] = ",".join(actors)
            directors = [
                d.name for d in filter(lambda c: c.role == "director", video.credits)
            ]
            if len(directors):
                vid["Director"] = ", ".join(directors)
        if (
            video.poster
            and video.category
            and video.category in config.mythtv.categories
        ):
            ca_sgs = get_storage_group_dirs("Coverart")
            if ca_sgs and len(ca_sgs):
                ca_sg = ca_sgs[0]
                cat_path = (
                    config.mythtv.categories[video.category]
                    if video.category in config.mythtv.categories
                    else None
                )
                if cat_path:
                    vid["Coverart"] = vid["CoverFile"] = (
                        f"{ca_sg}/{cat_path}/{video.poster}"
                    )
        if video.webref:
            vid["Inetref"] = video.webref.ref

        return vid
