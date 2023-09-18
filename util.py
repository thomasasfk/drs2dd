from __future__ import annotations

import contextlib
import os
import subprocess


ORDER_COUNT_PER_BEAT = 24
DEFAULT_THRESHOLD = 0.8


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
