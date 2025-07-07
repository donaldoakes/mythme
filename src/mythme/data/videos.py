import os
import time
import textwrap
from datetime import datetime
from typing import Optional, Union
from mythme.model.credit import Credit
from mythme.model.query import Query, Sort
from mythme.model.video import Video, VideosResponse, WebRef
from mythme.utils.db import get_connection
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
    exists_sql = "SELECT 1 FROM videometadata WHERE filename = %s LIMIT 1"
    delete_sql = "DELETE FROM videometadata WHERE intid = %s"
    insert_sql = """INSERT INTO videometadata
(host, filename, title, hash, contenttype,
year, releasedate, userrating, inetref, coverfile, director,
subtitle, collectionref, homepage, rating, length, playcount, season, episode, showlevel, childid, browse, watched, processed, category)
VALUES
(%(host)s, %(filename)s, %(title)s, %(hash)s, %(contenttype)s,
%(year)s, %(releasedate)s, %(userrating)s, %(inetref)s, %(coverfile)s, %(director)s,
%(subtitle)s, %(collectionref)s, %(homepage)s, %(rating)s, %(length)s, %(playcount)s, %(season)s, %(episode)s, %(showlevel)s, %(childid)s, %(browse)s, %(watched)s, %(processed)s, %(category)s)
"""  # noqa: E501

    def get_videos(self, query: Query) -> VideosResponse:
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
        res = api_call(f"Video/GetVideo?Id={id}")
        if (
            res
            and "VideoMetadataInfo" in res
            and "Id" in res["VideoMetadataInfo"]
            and res["VideoMetadataInfo"]["Id"]
        ):
            return self.to_video(res["VideoMetadataInfo"])
        return None

    def get_video_by_file(self, file: str) -> Optional[Video]:
        try:
            res = api_call(f"Video/GetVideoByFileName?FileName={file}")
            if (
                res
                and "VideoMetadataInfo" in res
                and "Id" in res["VideoMetadataInfo"]
                and res["VideoMetadataInfo"]["Id"]
            ):
                return self.to_video(res["VideoMetadataInfo"])
        except Exception as e:
            logger.debug(f"Error retrieving video by file name: {e}")
        return None

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

    def delete_unfound(self) -> int:
        sg_dirs = get_storage_group_dirs("Videos")
        if not sg_dirs or len(sg_dirs) == 0:
            return 0
        count = 0
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT intid, filename FROM videometadata")
                for intid, filename in cursor.fetchall():
                    file_exists = False
                    for sg_dir in sg_dirs:
                        logger.info(f"OS PATH: {sg_dir}/{filename}")
                        if os.path.exists(f"{sg_dir}/{filename}"):
                            file_exists = True
                            break
                    if not file_exists:
                        logger.info(f"Deleting metadata for unfound file: {filename}")
                        cursor.execute(self.delete_sql, (intid,))
                        count += 1
        return count

    def scan_videos(self) -> int:
        self.delete_unfound()

        sg_dirs = get_storage_group_dirs("Videos")
        if not sg_dirs or len(sg_dirs) == 0:
            return 0
        count = 0
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for sg_dir in sg_dirs:
                    logger.info(f"Scanning for videos in directory: {sg_dir}")

                    for root, _dirs, files in os.walk(sg_dir):
                        for file in files:
                            filepath = os.path.join(root[len(sg_dir) + 1 :], file)
                            cursor.execute(self.exists_sql, (filepath,))
                            row_exists = cursor.fetchone() is not None
                            if not row_exists:
                                logger.info(f"Found new video file: {filepath}")
                                data = (
                                    self.base_sql_data(filepath)
                                    | self.info_sql_data()
                                    | self.unused_sql_data()
                                )
                                cursor.execute(self.insert_sql, data)
                                count += 1
        return count

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
            catdir = ""
            if video.poster:
                if video.category:
                    catdir = (
                        f"/{config.mythtv.categories[video.category]}"
                        if video.category in config.mythtv.categories
                        else ""
                    )
                cov_sg_dirs = get_storage_group_dirs("Coverart")
                if cov_sg_dirs and len(cov_sg_dirs) > 0:
                    coverfile = f"{cov_sg_dirs[0]}{catdir}/{video.poster}"
                    raise ValueError("Coverart storage group not found")
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
                "releasedate": f"{video.year}-00-00" if video.year else "0000-00-00",
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
            "showlevel": 0,
            "childid": -1,
            "browse": 1,
            "watched": 0,
            "processed": 0,
            "category": 0,
        }

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

    def clear_metadata(self):
        # videometadata
        # videocast
        # videometadatacast
        pass
