import json
import logging
import re
from http import HTTPStatus

import requests

from fetch.fetch_douyin import VideoInfo

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
USER_AGENT_DESKTOP = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1";
USER_AGENT_MOBILE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36";

VIDEO_PATTERN = r"/video/(\d+)"

DOUYIN_DOMAIN = "https://www.douyin.com/aweme/v1/web/aweme/related/?"
DOUYIN_DETAIL_URL = 'https://www.douyin.com/aweme/v1/web/aweme/detail/?'
DOUYIN_URL = "https://www.douyin.com/"

TIKTOK_AGENT = "com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36"


def fetch_tiktok_info(origi_url):
    if origi_url is None or not str(origi_url).find("v.douyin.com") or not str(origi_url).find("www.douyin.com"):
        print("tiktok url is error")
        return ""

    video_no = get_tiktok_video_no(origi_url)

    tiktok_api_headers = {
        'User-Agent': TIKTOK_AGENT,
    }
    api_url = f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_no}'
    resp = requests.get(api_url, headers=tiktok_api_headers)
    title = ""
    desc = ""
    music_url = ""
    if resp.status_code == HTTPStatus.OK:
        aweme_detail_json = json.loads(resp.content)
        aweme_detail = aweme_detail_json["aweme_list"][0]
        music_url = aweme_detail["music"]["play_url"]["uri"]
        title = aweme_detail['desc']
        desc = aweme_detail['desc']
        logging.info("Get music videoId: %s, music url: %s", video_no, music_url)

    info = VideoInfo(video_no=video_no, video_title=title, video_desc=desc, video_url=origi_url, audio_url=music_url)
    return info


def get_tiktok_video_no(url):
    headers = {
        'User-Agent': TIKTOK_AGENT,
    }
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        logging.error("get_douyin_video_id url: %s ,reason:%s", url, resp
                      .reason)
        return resp.reason

    matches = re.search(VIDEO_PATTERN, resp.url)
    video_no = matches.group(1)
    logging.info("get douyin video_id: [%s] ", video_no)
    return video_no


def get_tiktok_audio_url(video_no, cookies: str = ""):
    '''
    允许不传参数
    '''
    tiktok_api_headers = {
        'User-Agent': TIKTOK_AGENT,
    }
    api_url = f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_no}'
    resp = requests.get(api_url, headers=tiktok_api_headers)
    if resp.status_code == HTTPStatus.OK:
        aweme_detail_json = json.loads(resp.content)
        aweme_detail = aweme_detail_json["aweme_list"][0]
        music_url = aweme_detail["music"]["play_url"]["uri"]
        logging.info("Get music videoId: %s, music url: %s", video_no, music_url)
        return music_url

#
# def download_music(video_no, cookie):
#     music_url = get_tiktok_audio_url(video_no, cookie)
#     file_utils.download_file("", video_no, music_url)


if __name__ == '__main__':
    get_tiktok_audio_url("6876811402821061890")
