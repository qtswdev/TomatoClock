import os

_SOUND_DIR = os.path.join(
    os.path.split(os.path.dirname(__file__))[0],
    "sounds"
)
REST_START = os.path.join(_SOUND_DIR, "rest_start.wav")
BREAK = os.path.join(_SOUND_DIR, "break.mp3")
ABORT = os.path.join(_SOUND_DIR, "abort.mp3")
PAGE = os.path.join(_SOUND_DIR, "page.mp3")
TIMEOUT = os.path.join(_SOUND_DIR, "TIMEOUT.mp3")
HALF_TIME = os.path.join(_SOUND_DIR, "half_time.wav")
