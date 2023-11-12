import logging
from enum import Enum
from rest_framework.decorators import api_view

from api import file_utils
from api.models import VideoContent, SucResponse, VideoContentEncoder
from fetch.fetch_douyin import fetch_douyin_info, get_douyin_video_no
from fetch.fetch_tiktok_2 import fetch_tiktok_info, get_tiktok_video_no
from recog.faster_whisper.core import transcribe

logger = logging.getLogger(__name__)


@api_view(['POST'])
def url_to_video_content(request):
    original_url = request.data.get('url')
    cookie = request.data.get("cookie")
    video_content = get_video_info(original_url, cookie)
    return SucResponse(video_content=video_content.serialize())


@api_view(['POST'])
def test(request):
    return SucResponse(msg="ok")


def get_video_info(shar_url: str, cookie: str) -> VideoContent:
    if "http" not in shar_url or shar_url == "":
        raise BizException(-1, "请输入正确的url链接")

    video_obj = None
    if "douyin" in shar_url:
        logger.debug("get video obj from http")
        douyin_info = fetch_douyin_info(shar_url, cookie)
        logger.debug("fetch_douyin_info result %s", douyin_info.video_no)

        file_path = file_utils.download_file("douyin", douyin_info.video_no, douyin_info.audio_url)
        logger.debug("file_utils.download_file id:%s path:%s", douyin_info.video_no, file_path)

        result_file = transcribe(file_path, "transcribe", language=None, initial_prompt=None, word_timestamps=None,
                                 output="vtt")
        logger.debug("transcribe finish %s", douyin_info.video_no)

        subtitle = result_file.getvalue()
        video_obj = VideoContent(video_no=douyin_info.video_no,
                                 video_title=douyin_info.video_title,
                                 video_desc=douyin_info.video_desc,
                                 video_type=VideoTypeEnums.Douyin.value,
                                 video_content=subtitle)
        return video_obj
    elif "tiktok" in shar_url:
        tiktok_info = fetch_tiktok_info(shar_url)
        file_path = file_utils.download_file("tiktok", tiktok_info.video_no, tiktok_info.audio_url)
        result_file = transcribe(file_path, "transcribe", language=None, initial_prompt=None, word_timestamps=None,
                                 output="vtt")
        subtitle = result_file.getvalue()
        video_obj = VideoContent(
            video_no=tiktok_info.video_no,
            video_title=tiktok_info.video_title,
            video_desc=tiktok_info.video_desc,
            video_type=VideoTypeEnums.TikTok.value,
            video_content=subtitle)
        return video_obj


class VideoTypeEnums(Enum):
    Douyin = "01"
    TikTok = "02"


class BizException(Exception):
    def __init__(self, errCode, errMsg):
        self.errCode = errCode
        self.errMsg = errMsg
        super().__init__()
