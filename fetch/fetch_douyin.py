import json
import logging
import re
from http import HTTPStatus

import requests

from fetch.douyin_XB import XBogus

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
USER_AGENT_DESKTOP = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1";
USER_AGENT_MOBILE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36";

VIDEO_PATTERN = r"/video/(\d+)"

DOUYIN_DOMAIN = "https://www.douyin.com/aweme/v1/web/aweme/related/?"
DOUYIN_DETAIL_URL = 'https://www.douyin.com/aweme/v1/web/aweme/detail/?'
DOUYIN_URL = "https://www.douyin.com/"


class VideoInfo:
    def __init__(self, video_no, video_title, video_url, audio_url, video_subtitles, video_desc=""):
        self.video_no = video_no
        self.video_title = video_title
        self.video_desc = video_desc
        self.video_url = video_url
        self.audio_url = audio_url
        self.video_subtitles = video_subtitles


def fetch_douyin_info(original_url: str, cookie: str) -> VideoInfo:
    if (original_url is None
            or not str(original_url).find("v.douyin.com")
            or not str(original_url).find("www.douyin.com")):
        return ""
    video_no = get_douyin_video_no(original_url)

    XB = XBogus()
    params_url = "aweme_id=" + video_no + "&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333"

    xbogus = XB.getXBogus(params_url)
    url = DOUYIN_DETAIL_URL + xbogus[0]
    logging.info("get video info url param: %s", params_url)

    headers = {
        "cookie": cookie,
        "referer": DOUYIN_URL,
        "user-agent": USER_AGENT_MOBILE
    }

    logging.debug("fetch_douyin_info url %s", url)
    resp = requests.get(url, headers=headers)
    logging.debug("fetch_douyin_info url result %s", resp.status_code)
    if resp.status_code == HTTPStatus.OK:
        aweme_detail_json = json.loads(resp.content)
        aweme_detail = aweme_detail_json["aweme_detail"]
        music_url = aweme_detail["music"]["play_url"]["uri"]
        title = aweme_detail['preview_title']
        desc = aweme_detail['desc']
        logging.info("Get music videoId: %s, music url: %s", video_no, music_url)
        return VideoInfo(video_no, title, desc, original_url, music_url)
    else:
        return VideoInfo()


def get_douyin_video_no(url):
    headers = {
        'User-Agent': USER_AGENT_DESKTOP,
    }
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        logging.error("get_douyin_video_id url: %s ,reason:%s", url, resp
                      .reason)
        return resp.reason

    matches = re.search(VIDEO_PATTERN, resp.url)
    video_no = matches.group(1)
    logging.info("get douyin video_id: [%s] ", video_no)
    return video_no


def get_douyin_audio_url(video_no, cookie):
    XB = XBogus()
    params_url = "aweme_id=" + video_no + "&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333"

    xbogus = XB.getXBogus(params_url)
    url = DOUYIN_DETAIL_URL + xbogus[0]
    logging.info("get video info url param: %s", params_url)

    headers = {
        "cookie": cookie,
        "referer": DOUYIN_URL,
        "user-agent": USER_AGENT_MOBILE
    }

    resp = requests.get(url, headers=headers)
    if resp.status_code == HTTPStatus.OK:
        aweme_detail_json = json.loads(resp.content)
        aweme_detail = aweme_detail_json["aweme_detail"]
        music_url = aweme_detail["music"]["play_url"]["uri"]
        logging.info("Get music videoId: %s, music url: %s", video_no, music_url)
        return music_url
#
#
# def download_music(video_no, cookie):
#     music_url = get_douyin_audio_url(video_no, cookie)
#     file_utils.download_file("douyin", video_no, music_url)
