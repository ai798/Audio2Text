import time

from faster_whisper import WhisperModel

model_size = "small"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

#
# if __name__ == "__main__":
#     now = time.time()
#     segments, info = model.transcribe("/Users/lennyz/data/scriptpro/download/douyin/7283485238938897700.mp3", beam_size=5)
#     print("spend time" , time.time() - now)
#     print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
#     for segment in segments:
#         print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
