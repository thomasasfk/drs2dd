from __future__ import annotations

import contextlib
import json
import os
import subprocess
from functools import partial

import cv2
import numpy as np
import requests
from PIL import Image

from model.dancerush import DRSSongDataZetaraku

ORDER_COUNT_PER_BEAT = 24
DEFAULT_THRESHOLD = 0.8


def match_template(image, template, threshold=DEFAULT_THRESHOLD) -> tuple[int, int, int, int]:
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray_template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    if loc[0].size:
        x, y = loc[1][0], loc[0][0]
        width, height = gray_template.shape[::-1]
        return int(x), int(y), int(width), int(height)


def map_position_to_dd_x(number):
    minimum, maximum = 31, 522  # 31 is the leftmost, 522 is the rightmost
    if number < minimum:
        return 1
    elif number > maximum:
        return 9
    percentage = (number - minimum) / (maximum - minimum)
    return int(percentage * 8) + 1


def _get_song_metadata_json():
    if os.getenv('REMOTE_DATA'):
        return requests.get(DRS_DATA_LINK).json()
    return json.load(open('resources/data.json', encoding='utf-8'))


def get_song_metadata_remote(song_id: str) -> DRSSongDataZetaraku | None:
    if not song_id:
        return None
    drs_data = _get_song_metadata_json()
    song_id_to_song = {s['songId']: s for s in drs_data['songs']}
    if metadata := song_id_to_song.get(song_id):
        return DRSSongDataZetaraku.from_dict(metadata)


def crop_frame(frame, x, y, width, height):
    cropped_frame = frame[y:y + height, x:x + width]
    return cropped_frame


DRS_DATA_LINK = 'https://dp4p6x0xfi5o9.cloudfront.net/drs/data.json'
WORKING_RESOLUTION = 1920, 1080

L_TEMPLATE = Image.open(
    'resources/l_template.png',
)
R_TEMPLATE = Image.open(
    'resources/r_template.png',
)

NOTE_SEARCH_AREA = 650, 475, 618, 105

find_l = partial(match_template, template=L_TEMPLATE)
find_r = partial(match_template, template=R_TEMPLATE)

SIGN_TEMPLATE = Image.open(
    'resources/drs_sign_template.png',
)

SIGN_SEARCH_AREA = 850, 143, 223, 49

find_stage = partial(match_template, template=SIGN_TEMPLATE)


def get_mp3_and_duration(folder_path) -> tuple[str, str] | tuple[None, None]:
    mp3_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    if not mp3_files:
        return None, None

    mp3_file = os.path.join(folder_path, mp3_files[0])
    with contextlib.suppress(subprocess.CalledProcessError):
        ffprobe_cmd = [
            'ffprobe',
            '-i', mp3_file,
            '-show_entries', 'format=duration',
            '-v', 'error',
            '-of', 'default=noprint_wrappers=1:nokey=1',
        ]
        duration_str = subprocess.check_output(ffprobe_cmd, text=True).strip()
        return mp3_file, duration_str

    return None, None


def get_song_cover_path(folder_path) -> str | None:
    cover_files = [
        f for f in os.listdir(folder_path) if f.startswith('jk_') and f.endswith('_b.png')
    ]
    if not cover_files:
        return None

    return os.path.join(folder_path, cover_files[0])
