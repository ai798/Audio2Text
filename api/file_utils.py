import logging
import os
import time
from enum import Enum

import requests

HOME_PATH = os.path.expanduser('~')
DOWNLOAD_PATH = HOME_PATH + "/data/files/audio2text/download"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# class VideoChannel(Enum):
#     DOUYIN = ("douyin", "01")
#     TIKTOK = ("tiktok", "02")
#
#     def __init__(self, name, code):
#         self.name = name
#         self.code = code

def download_file(video_channel, video_no: str, music_url: str):
    start_time = time.time()
    file_name = video_no + ".mp3"
    base_path = DOWNLOAD_PATH + "/" + video_channel
    full_path = base_path + "/" + file_name

    if not os.path.exists(base_path):  # 检查文件夹是否存在
        os.makedirs(base_path)  # 创建文件夹

    if os.path.exists(full_path):
        logging.error("加载音频文件存在, 不再重新下载, 返回文件路径")
        return full_path

    response = requests.get(music_url)
    with open(full_path, "wb") as file:
        file.write(response.content)
    logging.info("下载音频文件耗时 %s", str(time.time() - start_time))
    return full_path
