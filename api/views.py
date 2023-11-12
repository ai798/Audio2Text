import json
import logging
import os
import time
from enum import Enum

import requests
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
    video_content = get_video_info(original_url, None)
    return SucResponse(video_content=video_content.serialize())


@api_view(['POST'])
def test(request):
    return SucResponse(msg="ok")


def get_video_info(shar_url: str, lang: str) -> VideoContent:
    if "http" not in shar_url or shar_url == "":
        raise BizException(-1, "请输入正确的url链接")

    video_obj = None
    if "douyin" in shar_url:
        logger.debug("get video obj from http")
        cookieCache = "ttwid=1%7CxPjGPema3niiD3j16yy6uEaOrqt-ndlL5fZBf0Mr9iI%7C1688808453%7Cbd7badbab79b2b4e4fbe56124b1b643f828d6b60580a2d3829cb28ee5b4c0dca; s_v_web_id=verify_lmbtvz7s_Gc8iNIqR_gTy4_4raA_8IRg_v75wG52svqek; passport_csrf_token=07e7337d9e0457998baaee7fad4a5500; passport_csrf_token_default=07e7337d9e0457998baaee7fad4a5500; xgplayer_user_id=934309758701; d_ticket=62b1b182c8a46b3eb944e902f937864aaf5c3; passport_assist_user=Cjxb0loT3woyI6BEqJ8Ky6t1TIrhXxrzCylHf9CP7yKcqC-2sgG_RZUg2sLfu701Ce0GXxVzdYwnazv4CI0aSgo8fjRMBCNswvPgpV3SQ3_6K_sET7KZt70ncI7du8PjgmmPyeIgsoUVeSvFxuE1aeNhkQE_8R_5F8oe-xqfEMzEuw0Yia_WVCABIgED4jDbkg%3D%3D; n_mh=HfLXgDL8rksuzXUhP9IOwC4ewsDkoXROYkTGYlY7YNs; sso_uid_tt=eee3d0165f7e5512198d0ed73ad41091; sso_uid_tt_ss=eee3d0165f7e5512198d0ed73ad41091; toutiao_sso_user=59eee91b157c39bab244b37f7eac7ec6; toutiao_sso_user_ss=59eee91b157c39bab244b37f7eac7ec6; sid_ucp_sso_v1=1.0.0-KDg5YWU3NzBjYzUyMWI3Y2IyMGE0YTQ1ZDhkNjAxMTk5OTk2Y2Q0YTAKHQjmsrKk8gEQ1Kf1pwYY7zEgDDCk3IzMBTgCQPEHGgJsZiIgNTllZWU5MWIxNTdjMzliYWIyNDRiMzdmN2VhYzdlYzY; ssid_ucp_sso_v1=1.0.0-KDg5YWU3NzBjYzUyMWI3Y2IyMGE0YTQ1ZDhkNjAxMTk5OTk2Y2Q0YTAKHQjmsrKk8gEQ1Kf1pwYY7zEgDDCk3IzMBTgCQPEHGgJsZiIgNTllZWU5MWIxNTdjMzliYWIyNDRiMzdmN2VhYzdlYzY; odin_tt=df958841cb608e7dd719413d6020d7bade64423bdeb43ed26493a05703f2456a3aa759f4ebe212096a809f267f8b3ae9; uid_tt=60c301738c0b5276c4b95811609f798e; uid_tt_ss=60c301738c0b5276c4b95811609f798e; sid_tt=996110e9d6356c81844e53f015b184cf; sessionid=996110e9d6356c81844e53f015b184cf; sessionid_ss=996110e9d6356c81844e53f015b184cf; LOGIN_STATUS=1; store-region=cn-gd; store-region-src=uid; _bd_ticket_crypt_doamin=3; _bd_ticket_crypt_cookie=3a84d0c73216b3e71e23819fef8eb3fd; __security_server_data_status=1; sid_guard=996110e9d6356c81844e53f015b184cf%7C1694323674%7C5183997%7CThu%2C+09-Nov-2023+05%3A27%3A51+GMT; sid_ucp_v1=1.0.0-KDQ1M2UyYThjMDQzYTY3NTQ1ZDFlMWZkNTVjMTg4ZTQ2YzkwMzAxZGEKGQjmsrKk8gEQ2qf1pwYY7zEgDDgCQPEHSAQaAmxxIiA5OTYxMTBlOWQ2MzU2YzgxODQ0ZTUzZjAxNWIxODRjZg; ssid_ucp_v1=1.0.0-KDQ1M2UyYThjMDQzYTY3NTQ1ZDFlMWZkNTVjMTg4ZTQ2YzkwMzAxZGEKGQjmsrKk8gEQ2qf1pwYY7zEgDDgCQPEHSAQaAmxxIiA5OTYxMTBlOWQ2MzU2YzgxODQ0ZTUzZjAxNWIxODRjZg; douyin.com; device_web_cpu_core=10; device_web_memory_size=8; webcast_local_quality=null; csrf_session_id=9be981bc4749baffbb99f85bd1bd43fa; webcast_local_quality=null; passport_fe_beating_status=true; publish_badge_show_info=%220%2C0%2C0%2C1697257414259%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.803%7D; SEARCH_RESULT_LIST_TYPE=%22single%22; download_guide=%223%2F20231014%2F0%22; pwa2=%220%7C0%7C3%7C0%22; strategyABtestKey=%221697346430.761%22; tt_scid=gGeFK3iWL74ZKVfW2nrc9f.yOa0pduMSZKu1b3aXdHoyNsy0xhp2GOjplYqCVbRAd01e; __ac_nonce=0652b810a00f524e7d8b4; __ac_signature=_02B4Z6wo00f01QlYuigAAIDBkTMtWGwCpBkJeL6AACeAdXfcK5bN38P785IPUAkMwgUu-wBhMvkF6HmF5367L4T2wsLxdoMfyoARJbGq6YE-64w71k5DszDg1LHUJUe0VEdhxp0gwtA0E92J41; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2056%2C%5C%22screen_height%5C%22%3A1329%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A10%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A6.8%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A100%7D%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTnNaaHRab0Q4d0FKeHhhbXMxZXE5T3J1WERLTitPclZITHJOOXQ4Q1VLSkZLOUJRa3V2OFVhUVc4OW5NaTJiOHJLYmpaSU9kWi9uWFo2WkJKTTcyM2M9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; msToken=mevoMEtfRjgzMmr_1ysPA0lZuGkaoaiaXzB29UAbncxF5KL3C_gOAfXLsvcNZB_I8DzyAyTf9ONtgnDAzWjlUuz-vXL7wwX5l9rjqIpoCx_K1TSzfXKwUe6dv3jl42k=; msToken=8SoA9WQPVVBIOz6pymGP8Cc6aL9TrCE--dB3IXOcxFOGDVOKMVJRmysqq6NjhmhMXpunMK-J1ORnX_j-5s_bnOE99zSbPR8YTcPn5jW6vUyAXFpZfdHYn6HDlo54jlgZ"
        douyin_info = fetch_douyin_info(shar_url, cookieCache)
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
