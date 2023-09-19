from __future__ import annotations

import contextlib
import os
import subprocess
from datetime import datetime


def get_ogg_and_duration(folder_path) -> tuple[str, str] | tuple[None, None]:
    ogg_files = [f for f in os.listdir(folder_path) if f.endswith('.ogg')]
    matching_files = [f for f in ogg_files if f.endswith('clip1.ogg')]
    if matching_files:
        ogg_file = os.path.join(folder_path, matching_files[0])
        with contextlib.suppress(subprocess.CalledProcessError):
            ffprobe_cmd = [
                'ffprobe',
                '-i', ogg_file,
                '-show_entries', 'format=duration',
                '-v', 'error',
                '-of', 'default=noprint_wrappers=1:nokey=1',
            ]
            duration_str = subprocess.check_output(
                ffprobe_cmd, text=True,
            ).strip()
            return ogg_file, duration_str

    return None, None


def get_song_cover_path(folder_path) -> str | None:
    cover_files = [
        f for f in os.listdir(folder_path) if f.startswith('jk_') and f.endswith('_b.png')
    ]
    if not cover_files:
        return None

    return os.path.join(folder_path, cover_files[0])


def create_valid_filename(input_string: str):
    valid_chars = f'-_() {os.sep}{os.sep}'
    sanitized_string = ''.join(
        c for c in input_string if c.isalnum() or c in valid_chars
    ).rstrip()
    max_filename_length = 255
    return sanitized_string[:max_filename_length]


def datetime_to_ticks(dt):
    epoch = datetime(1, 1, 1)
    dt_delta = dt - epoch
    # total_seconds() returns seconds, but we need 100-nanosecond intervals
    ticks = dt_delta.total_seconds() * 10 ** 7
    return int(ticks)


def yyyymmdd_to_ticks(date_str: str):
    dt = datetime.strptime(date_str, '%Y%m%d')
    return datetime_to_ticks(dt)
