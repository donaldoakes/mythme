import time
from mythme.model.query import Query, Sort
from mythme.model.video import Video, VideosResponse
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
        return video
