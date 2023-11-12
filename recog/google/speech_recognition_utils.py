import logging
import os

import speech_recognition as sr
import sys

# sys.path.append('/opt/homebrew/bin/ffmpeg')
#
# logger = logging.getLogger(__name__)
#
# def recognition_google(audio_file_path, language):
#     if os.path.exists(audio_file_path):
#         r = sr.Recognizer()
#         with sr.AudioFile(audio_file_path) as source:
#             audio = r.record(source)  # read the entire audio file
#
#         text = r.recognize_google(audio_data=audio, language=language)
#         logger.info("音频转文字完成 file path:", audio_file_path, " text:", text)
#         return text
#     else:
#         return ""
