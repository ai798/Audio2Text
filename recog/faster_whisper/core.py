import logging
import time
from typing import BinaryIO, Union
from io import StringIO
from threading import Lock
import torch

import whisper
from recog.utils import model_converter, ResultWriter, WriteTXT, WriteSRT, WriteVTT, WriteTSV, WriteJSON
from faster_whisper import WhisperModel

model_size = "large-v2"

# model_name = os.getenv("ASR_MODEL", "faster-whisper-small.en")
# model_path = os.path.join("/Users/lennyz/huggingface", model_name)
# model_converter(model_name, model_path)

if torch.cuda.is_available():
    logging.info("init whisper cuda float32")
    model = WhisperModel(model_size, device="cuda", compute_type="int8")
else:
    logging.info("init whisper cpu float32")
    model = WhisperModel(model_size, cpu_threads=10, num_workers=4, device="cpu", compute_type="int8")
model_lock = Lock()


def transcribe(
        audio,
        task: Union[str, None],
        language: Union[str, None],
        initial_prompt: Union[str, None],
        word_timestamps: Union[bool, None],
        output,
):
    start_time = time.time()
    options_dict = {"task": task}
    if language:
        options_dict["language"] = language
    if initial_prompt:
        options_dict["initial_prompt"] = initial_prompt
    if word_timestamps:
        options_dict["word_timestamps"] = True
    with model_lock:
        segments = []
        text = ""
        i = 0
        segment_generator, info = model.transcribe(audio, beam_size=5, **options_dict)
        for segment in segment_generator:
            segments.append(segment)
            text = text + segment.text
        result = {
            "language": options_dict.get("language", info.language),
            "segments": segments,
            "text": text
        }

    outputFile = StringIO()
    write_result(result, outputFile, output)
    outputFile.seek(0)
    logging.info("音转文耗时: %s s ， 模型 %s", str(time.time() - start_time), model_size)
    return outputFile


def language_detection(audio):
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.pad_or_trim(audio)

    # detect the spoken language
    with model_lock:
        segments, info = model.transcribe(audio, beam_size=5)
        detected_lang_code = info.language

    return detected_lang_code


def write_result(
        result: dict, file: BinaryIO, output: Union[str, None]
):
    if (output == "srt"):
        WriteSRT(ResultWriter).write_result(result, file=file)
    elif (output == "vtt"):
        WriteVTT(ResultWriter).write_result(result, file=file)
    elif (output == "tsv"):
        WriteTSV(ResultWriter).write_result(result, file=file)
    elif (output == "json"):
        WriteJSON(ResultWriter).write_result(result, file=file)
    elif (output == "txt"):
        WriteTXT(ResultWriter).write_result(result, file=file)
    else:
        return 'Please select an output method!'
