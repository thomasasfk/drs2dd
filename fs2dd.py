from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime

from model.dancedash import DDBeatMap
from model.dancedash import DDBeatMapData
from model.dancedash import DDBeatMapInfoFile
from model.dancedash import DDLineNode
from model.dancedash import DDRoadBlockNode
from model.dancedash import DDSphereNode
from model.feetsaber import FSBeatMapFile
from model.feetsaber import FSInfoDat
from util import convert_egg_to_ogg_and_get_length
from util import get_first_image_file_in_folder
from util import random_10_digit_int
from util import yyyymmdd_to_ticks


def map_sphere_nodes(fs_beat_map: FSBeatMapFile) -> list[DDSphereNode]:
    spheres = []
    ...
    return spheres


def map_line_nodes(fs_beat_map: FSBeatMapFile) -> list[DDLineNode]:
    lines = []
    ...
    return lines


def map_down_and_jump_notes(fs_beat_map: FSBeatMapFile) -> list[DDRoadBlockNode]:
    road_blocks = []
    ...
    return road_blocks


def create_dd_tracks_from_fs(fs_map_dir: str) -> DDBeatMapInfoFile:
    info_file_path = os.path.join(fs_map_dir, 'Info.dat')
    fs_info = FSInfoDat.from_json_file(info_file_path)

    egg_song_path = [
        os.path.join(fs_map_dir, f) for f in os.listdir(
            fs_map_dir,
        ) if f.endswith('.egg')
    ][0]
    target_dir = f'{fs_info.songName} - {fs_info.levelAuthorName}'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    ogg_song_name, song_length = convert_egg_to_ogg_and_get_length(
        egg_song_path,
    )

    new_song_path = os.path.join(target_dir, ogg_song_name)
    shutil.copy(egg_song_path, new_song_path)
    song_path = new_song_path
    if song_cover_path := get_first_image_file_in_folder(fs_map_dir):
        new_song_cover_path = os.path.join(
            target_dir, os.path.basename(song_cover_path),
        )
        shutil.copy(song_cover_path, new_song_cover_path)
        song_cover_path = new_song_cover_path

    song_paths = []
    for difficulty_set in fs_info.difficultyBeatmapSets:
        for difficulty_set in difficulty_set.difficultyBeatmaps:
            beat_map: FSBeatMapFile = difficulty_set.get_beatmap(fs_map_dir)

            sphere_notes = map_sphere_nodes(beat_map)
            line_notes = map_line_nodes(beat_map)
            road_block_notes = map_down_and_jump_notes(beat_map)

            total_note_count = len(sphere_notes + line_notes + road_block_notes)  # noqa
            dd_beat_map = DDBeatMap(
                data=DDBeatMapData(
                    name=f'{fs_info.songName}',
                    sphereNodes=sphere_notes,
                    lineNodes=line_notes,
                    roadBlockNodes=road_block_notes,
                ),
                BPM=fs_info.beatsPerMinute,
                NPS=str(round(total_note_count / song_length, 2)),
            )

            song_paths.append(
                dd_beat_map.save_to_file(
                    target_dir, 'a.json',
                ),
            )

    available_difficulties = [
        'Easy', 'Normal',
        'Hard', 'Expert', 'Master', 'ACE',
    ]
    song_path_difficulties = zip(song_paths, available_difficulties)
    difficulties = {
        f'DRS_{d}': os.path.basename(
            sp,
        ) for sp, d in song_path_difficulties
    }

    create_ticks = yyyymmdd_to_ticks(datetime.now().strftime('%Y%m%d'))
    dd_beat_map_info = DDBeatMapInfoFile(
        CreateTicks=create_ticks,
        CreateTime=str(create_ticks),
        BeatMapId=random_10_digit_int(),
        SongName=fs_info.songName,
        SongLength=str(song_length),
        SongAuthorName=fs_info.songAuthorName,
        LevelAuthorName=fs_info.levelAuthorName,
        Bpm=str(fs_info.beatsPerMinute),
        SongPath=os.path.basename(song_path),
        CoverPath=os.path.basename(song_cover_path or '') or None,
        **difficulties,
    )

    dd_beat_map_info.save_to_file(target_dir)

    print(
        f'Created {dd_beat_map_info.SongName} ({dd_beat_map_info.BeatMapId})',
    )
    return dd_beat_map_info


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create Dance Dash tracks from Feet Saber maps',
    )
    parser.add_argument(
        '--fs-map-dir',
        type=str,
        help='The directory containing the Feet Saber map files',
        required=True,
    )

    args = parser.parse_args()
    if not os.path.exists(args.fs_map_dir):
        print(f'Invalid Feet Saber map directory: {args.fs_map_dir}')
        raise SystemExit(1)

    create_dd_tracks_from_fs(args.fs_map_dir)
    raise SystemExit(0)
