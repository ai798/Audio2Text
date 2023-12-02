import json
import logging
import os
import re
import subprocess
from urllib.parse import parse_qs, urlparse

import requests

from fetch.fetch_douyin import VideoInfo
from web.middleware import BizException

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

HOME_PATH = os.path.expanduser('~')
DOWNLOAD_PATH = HOME_PATH + "/data/files/scriptpro/download/youtube/"

SUBTILT_HOST = "https://savesubs.com"
SUBTITLE_DOWNLOADER_API = 'https://savesubs.com/action/extract'
headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'X-Requested-Domain': 'savesubs.com',
    'X-Requested-With': 'xmlhttprequest',
    'X-Auth-Token': "q5qmytiplqllk5/OnJLKm2aabWpoaZHIx5lqaJ1nY5mPjsyErJqwgbKOqrHVfoyJhoKCusKvpop3",
    'Cookie': "cf_clearance=tGaUPagoXvIYT2AspCoWdLA2wGC_8AwItRV_K9nawss-1700059778-0-1-aefea140.d83d6674.f9fffea0-0.2.1700059778"
}

# youtube-dl
YOUTUBE_DL_CMD = "/Users/lennyz/github/repo/ytdl-org/youtube-dl/youtube-dl "
YOUTUBE_DOWNLOAD_AUDIO_CMD = "youtube-dl "
YOUTUBE_CHECK_SUBTITLES = YOUTUBE_DL_CMD + "--list-subs {}"
# 上传的字幕
YOUTUBE_DOWNLOAD_SUBTITLE = (YOUTUBE_DL_CMD +
                             "-o '" + DOWNLOAD_PATH + "subtitles/%(id)s.%(ext)s' "
                                                      "--skip-download  --write-sub {}")
# 机翻字幕
YOUTUBE_DOWNLOAD_SUBTITLE_AUTO = (YOUTUBE_DL_CMD +
                                  "-o '" + DOWNLOAD_PATH + "subtitles/%(id)s.%(ext)s' "
                                                           "--skip-download  --write-auto-sub {}")

# 下载音频
YOUTUBE_DOWNLOAD_AUDIO = (YOUTUBE_DL_CMD +
                          "-o '" + DOWNLOAD_PATH + "%(id)s.%(ext)s' "
                                                   " -x --audio-format m4a {}")
# 获取音频信息
YOUTUBE_DOWNLOAD_INFO = (YOUTUBE_DL_CMD +
                         "-o '" + DOWNLOAD_PATH + "json/%(id)s.%(ext)s' "
                                                  " --skip-download --write-info-json {}")


def fetch_youtube_info(original_url) -> VideoInfo:
    if original_url is None or not str(original_url).find("youtube.com") or not str(original_url).find("youtu.be"):
        print("youtube url is error")
        return None
    try:
        video_no = get_youtube_video_id(original_url)
        data = {
            "data": {"url": original_url},
        }
        response = requests.post(SUBTITLE_DOWNLOADER_API, headers=headers, data=json.dumps(data))
        json_response = response.json()
        if json_response.get("response", None) is not None:
            respBody = json_response.get("response")
            downloadUrl = SUBTILT_HOST + respBody.get("formats")[0]['url']
            subtitle = requests.get(downloadUrl).text
            title = respBody.get("title")
            duration = respBody.get("duration_raw")
            return VideoInfo(video_no=video_no,
                             video_title=title,
                             video_desc=title,
                             video_url=original_url,
                             video_duration=duration,
                             video_subtitles=subtitle)
    except Exception:
        logging.error("获取youtube字幕失败")
        raise BizException("-1", "Fetch youtube url error!")


def fetch_youtube_info_by_youtube_dl(original_url) -> VideoInfo:
    if original_url is None or not str(original_url).find("youtube.com") or not str(original_url).find("youtu.be"):
        print("youtube url is error")
        return None
    # 获取视频内容

    # 下载字幕
    subtitle = youtube_dl_get_subtitles(original_url)
    if subtitle is None:
        # 下载音频
        if youtube_dl_get_audio(original_url):
            return None

    # except Exception:
    #     logging.error("获取youtube字幕失败")
    #     raise BizException("-1", "Fetch youtube url error!")
    return None


def youtube_dl_get_subtitles(original_url) -> str:
    try:
        # 检查字幕
        process = subprocess.Popen(YOUTUBE_CHECK_SUBTITLES.format(original_url), shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        if stderr is not None:
            logging.error(str(stderr))
            return None
        if "Available subtitles" in stdout.decode("utf-8"):
            # 字幕
            fetch_cmd = YOUTUBE_DOWNLOAD_SUBTITLE.format(original_url)
            print(fetch_cmd)
            process = subprocess.Popen(fetch_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = process.communicate()
            if stderr is not None:
                logging.error(str(stderr))
                return None
            read_subtitles_file(stdout.decode("utf-8"))
            return
        elif "Available automatic captions" in stdout.decode("utf-8"):
            # 机翻字幕
            fetch_cmd = YOUTUBE_DOWNLOAD_SUBTITLE_AUTO.format(original_url)
            print(fetch_cmd)
            process = subprocess.Popen(fetch_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = process.communicate()
            if stderr is not None:
                logging.error(str(stderr))
                return None
            return
        else:
            logging.warning("Youtube video has no subtitles %s", original_url)
            return None
    except Exception as e:
        logging.error("下载youtube字幕异常, 返回null")
        return None


def youtube_dl_get_audio(original_url) -> bool:
    try:
        # 检查字幕
        cmd = YOUTUBE_DOWNLOAD_AUDIO.format(original_url)
        print(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        if stderr is not None:
            logging.error(str(stderr))
            return False
        if "Destination" in stdout.decode("utf-8"):
            return True
    except Exception as e:
        logging.error("下载youtube字幕异常, 返回null")
        return False


def fetch_youtube_info_by_dl(original_url) -> VideoInfo:
    try:
        # 检查字幕
        cmd = YOUTUBE_DOWNLOAD_INFO.format(original_url)
        print(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        if stderr is not None:
            logging.warning("解析youtube链接异常")
            raise BizException(-1, "解析youtube链接异常")

        if stdout is None or stdout.decode("utf-8") == "":
            logging.warning("解析youtube链接获取视频信息json为空")
            raise BizException(-1, "解析youtube链接异常")

        res = stdout.decode('utf-8')
        file_path = res.split(':')[-1].strip()
        logging.info("download json file: %s", file_path)
        json_str = ""
        with open(file_path, 'r') as file:
            json_str = file.read()
        json_obj = json.loads(json_str)
        video_no = json_obj.get('id')
        video_title = json_obj.get('title')
        video_subtitles = ""
        audio_url = ""
        # 遍历字幕, 人工
        if json_obj.get('subtitles') is not None and len(json_obj.get('subtitles')) > 0:
            for key, value in json_obj.get('subtitles').items():
                if video_subtitles != "":
                    break

                for item in list(value):
                    if item.get("ext") == "vtt":
                        subtitle_url = item.get("url")
                        try:
                            logging.info("Youtube get subtitles url %s", subtitle_url)
                            resp = requests.get(subtitle_url)
                            if resp is not None and resp.status_code == 200:
                                video_subtitles = resp.text
                                break
                        except Exception as e:
                            logging.error("Youtube youtube subtitles error url %s error %s", subtitle_url, e)
        elif json_obj.get('automatic_captions') is not None and len(json_obj.get('automatic_captions')) > 0:
            for key, value in json_obj.get('automatic_captions').items():
                if video_subtitles != "":
                    break

                if key in {"ja", "zh", "en", "zh-Hant", "zh-Hans"}:
                    for item in list(value):
                        if item.get("ext") == "vtt":
                            subtitle_url = item.get("url")
                            try:
                                logging.info("Youtube get auto subtitles url %s", subtitle_url)
                                resp = requests.get(subtitle_url)
                                if resp is not None and resp.status_code == 200:
                                    video_subtitles = resp.text
                                    break
                            except Exception as e:
                                logging.error("Youtube get auto subtitles error url %s error %s", subtitle_url, e)
        else:
            # 遍历音频
            for audio in list(json_obj.get('formats')):
                ext = audio.get('ext')
                if ext == "webm" or ext == "m4a":
                    audio_url = audio.get('url')
                    logging.info("Http get audio url %s", audio_url)
                    break
        return VideoInfo(video_no=video_no,
                         video_title=video_title,
                         video_subtitles=video_subtitles,
                         video_url=original_url,
                         audio_url=audio_url)
    except Exception as e:
        logging.error("下载youtube字幕异常, 返回null %s", e)
        raise BizException(-1,"Youtube url analyze error ")


def read_subtitles_file(stdout: str):
    if stdout is None or stdout == "":
        return ""
    substring = "Writing video subtitles to:"
    start_index = stdout.find(substring)
    if start_index != -1:
        file_path = stdout[start_index + len(substring):].strip()
        content = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(content)
        return content
    else:
        print("Substring not found")


def get_youtube_video_id(origi_url):
    video_id = ""
    if "youtube.com" in origi_url:
        if "/shorts/" in origi_url:
            # https://youtube.com/shorts/QPd7nT7ecQI?si=knyiF8ZxGWawp_lS
            arr = origi_url.split("/shorts/")[1]
            video_id = arr.split("?")[0]
            return video_id
        else:
            # https://www.youtube.com/watch?v=YP-fFpj2Xyw
            video_id = parse_qs(urlparse(origi_url).query)["v"][0]
    elif "youtu.be" in origi_url:
        # https://youtu.be/YP-fFpj2Xyw?si=mrOFutPs7TenJVs-
        video_id = re.search(r"youtu\.be/([^?]+)", origi_url).group(1)
    return video_id


if __name__ == "__main__":
    # url = "https://youtu.be/7gCtkT1A1tA?si=6O8Pf5fN2LtnK58M"
    # 多字幕
    url = "https://www.youtube.com/watch?v=0zLSbqGUNJQ"
    # 无字幕
    url = "https://www.youtube.com/watch?v=blfaIVvjpCg"
    # 机翻字幕
    url = "https://www.youtube.com/watch\?v\=3NIbs1N39AY"
    # 短视频
    url = "https://youtube.com/shorts/QPd7nT7ecQI?si=DAyU9RLJaURbAU3d"
    # video = fetch_youtube_info(url)
    # print(video)
    # youtube_dl_get_subtitles(url)
    # youtube_dl_get_audio(url)
    # video_info = fetch_youtube_info_by_dl(url)
    # print(video_info)

    video_no = get_youtube_video_id(url)
    print(video_no)
