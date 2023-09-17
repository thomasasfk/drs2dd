from __future__ import annotations

import contextlib
import os
import subprocess


ORDER_COUNT_PER_BEAT = 24
DEFAULT_THRESHOLD = 0.8


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
