from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict

import cv2
from alive_progress import alive_bar
from loguru import logger

from model.dancedash import create_note_sphere
from model.dancedash import DDBeatMap
from model.dancedash import LEFT_NOTE
from model.dancedash import RIGHT_NOTE
from util import crop_frame
from util import find_l
from util import find_r
from util import find_stage
from util import get_song_metadata_remote
from util import map_position_to_dd_x
from util import NOTE_SEARCH_AREA
from util import ORDER_COUNT_PER_BEAT
from util import SIGN_SEARCH_AREA
from util import WORKING_RESOLUTION


@logger.catch
def extract_spheres_from_drs_video(video_path: str, bpm: int):  # noqa
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f'Unable to open video file: {video_path}')

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration_seconds = total_frames / video_fps
    bps = bpm / 60

    with alive_bar(
        total=total_frames,
        title='Finding stage',
        bar='notes',
        spinner='notes',
    ) as bar:
        logger.info(f'Starting to process video: {video_path}')
        logger.info(f'Total frames: {total_frames}')

        stage_found = False
        while not stage_found:
            bar()
            ret, frame = cap.read()
            if not ret:
                raise ValueError('Unable to find stage.')

            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
            if int(frame_number % 5) != 0:
                continue

            frame = cv2.resize(frame, WORKING_RESOLUTION)
            search_area = crop_frame(frame, *SIGN_SEARCH_AREA)
            stage_found = find_stage(search_area)

        bar.title = 'Finding notes'

        frames_since_l = 0
        frames_since_r = 0

        spheres = []
        while True:
            bar()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, WORKING_RESOLUTION)
            current_position_seconds = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            # float between 0 and 1 representing the time in the song
            progress_percentage = current_position_seconds / duration_seconds

            frames_since_l -= 1
            frames_since_r -= 1

            note_order = int(
                bps * current_position_seconds *
                ORDER_COUNT_PER_BEAT,
            )
            search_area = crop_frame(frame, *NOTE_SEARCH_AREA)
            if frames_since_l < 1:
                if left := find_l(search_area):
                    frames_since_l = 5
                    note = create_note_sphere(  # noqa
                        progress_percentage,
                        map_position_to_dd_x(left[0]),
                        note_order,
                        LEFT_NOTE,
                    )
                    spheres.append(note)

            if frames_since_r < 1:
                if right := find_r(search_area):
                    frames_since_r = 5
                    note = create_note_sphere(  # noqa
                        progress_percentage,
                        map_position_to_dd_x(right[0]),
                        note_order,
                        RIGHT_NOTE,
                    )
                    spheres.append(note)

    cap.release()
    return spheres


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Image and video processing tools',
    )
    parser.add_argument('video_path', type=str, help='DRS Video path')
    parser.add_argument('--song-id', type=str, help='BeatMap ID')
    parser.add_argument('--bpm', type=int, help='BPM of the song')
    args = parser.parse_args()

    if not args.song_id and not args.bpm:
        raise ValueError('Must provide either song_id or bpm')

    raw_video_name = os.path.basename(args.video_path)
    logger.remove()  # remove default logger (stdout)
    logger.add(
        f'{raw_video_name}.log',
        backtrace=True,
        diagnose=True,
        level='DEBUG' if os.getenv('DEBUG') else 'INFO',
    )

    if song_metadata := get_song_metadata_remote(args.song_id):
        name = song_metadata.title
        bpm = song_metadata.bpm
    elif args.bpm:
        name = f'Unknown Song - {raw_video_name}'
        bpm = args.bpm
    else:
        raise ValueError('Unable to find song metadata')

    spheres = extract_spheres_from_drs_video(args.video_path, bpm)
    beatmap = DDBeatMap.create(
        name=name,
        interval_per_second=0.0,  # todo: what is this.
        order_count_per_beat=ORDER_COUNT_PER_BEAT,
        sphere_nodes=spheres,
        beat_subs=1,  # todo: what is this.
        bpm=bpm,
        info='',
    )

    beatmap_dict = asdict(beatmap)
    with open(f'{raw_video_name}.json', 'w') as f:
        json.dump(beatmap_dict, f, indent=4)

    logger.info(f'Finished processing video: {args.video_path}')
