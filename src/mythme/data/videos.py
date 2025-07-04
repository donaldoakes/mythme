import time
from datetime import datetime
from typing import Optional
from mythme.model.credit import Credit
from mythme.model.query import Query, Sort
from mythme.model.video import Video, VideosResponse, WebRef
from mythme.utils.mythtv import api_call, paging_params
from mythme.utils.log import logger
from mythme.utils.text import trim_article


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

        if query.sort.name and query.sort.name != "start":
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

    def sort(self, video: Video, sort: Sort) -> tuple:
        """Sort according to query."""
        title = trim_article(video.title.lower())
        if sort.name == "title":
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

    def clear_metadata(self):
        # videometadata
        # videocast
        # videometadatacast
        pass
