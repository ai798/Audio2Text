import time


#
#
# if __name__ == '__main__':
#     # instantiate pipeline
#     pipeline = FlaxWhisperPipline("openai/whisper-small")
#
#     # JIT compile the forward call - slow, but we only do once
#     now = time.time()
#     text = pipeline("/Users/lennyz/data/scriptpro/download/douyin/7283485238938897700.mp3")
#     print("first spend time", time.time() - now)
#     now = time.time()
#     print(text)
#
#     # used cached function thereafter - super fast!!
#     text = pipeline("/Users/lennyz/data/scriptpro/download/douyin/7283485238938897700.mp3")
#     print("second spend time", time.time() - now)
#     print(text)
