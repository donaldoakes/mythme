import time
from datetime import datetime
from typing import Optional
from mythme.model.credit import Credit
from mythme.model.query import Query, Sort
from mythme.model.video import Video, VideosResponse, WebRef
from mythme.utils.mythtv import (
    api_call,
    api_update,
    get_storage_group_dirs,
    paging_params,
)
from mythme.utils.text import trim_article
from mythme.utils.config import config
from mythme.utils.log import logger


class VideoData:
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
        return api_update("Video/UpdateVideoMetadata", params=self.from_video(video))

    def sort(self, video: Video, sort: Sort) -> tuple:
        """Sort according to query."""
        if sort.name == "file":
            return (video.file.lower(), video.id)
        elif sort.name == "title":
            title = trim_article(video.title.lower())
            return (title, video.id)
        else:
            raise ValueError(f"Unsupported sort: {sort.name}")

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
                    vid["Coverart"] = f"{ca_sg}/{cat_path}/{video.poster}"
        if video.webref:
            vid["Inetref"] = video.webref.ref

        return vid

    def clear_metadata(self):
        # videometadata
        # videocast
        # videometadatacast
        pass
