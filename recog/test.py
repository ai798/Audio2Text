import time

from recog.faster_whisper.core import transcribe
from transfer.ffmpeg_utils import load_audio_file_path

if __name__ ==  "__main__":
    file_path = "/Users/lennyz/data/files/scriptpro/download/douyin/7296777201654009138.mp3"

    star_time = time.time()
    result_file = transcribe(file_path, "transcribe", language=None, initial_prompt=None, word_timestamps=None,
                             output="vtt")
    print("音转文耗时", time.time() - star_time)
    print(result_file.getvalue())