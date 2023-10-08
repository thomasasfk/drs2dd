from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime

from model.dancedash import DD_LINE_LEFT
from model.dancedash import DD_LINE_RIGHT
from model.dancedash import DDBeatMap
from model.dancedash import DDBeatMapData
from model.dancedash import DDBeatMapInfoFile
from model.dancedash import DDDownPos
from model.dancedash import DDDownPos2D
from model.dancedash import DDJumpPos
from model.dancedash import DDJumpPos2D
from model.dancedash import DDLineNode
from model.dancedash import DDRoadBlockNode
from model.dancedash import DDSphereNode
from model.dancedash import ORDER_COUNT_PER_BEAT
from model.dancedash import X_Y
from model.feetsaber import FS_LEFT_NOTE
from model.feetsaber import FS_RIGHT_NOTE
from model.feetsaber import FS_TO_DD_NOTE_TYPE
from model.feetsaber import FSBeatMapFile
from model.feetsaber import FSInfoDat
from util import convert_egg_to_ogg_and_get_length
from util import get_first_image_file_in_folder
from util import random_9_digit_int
from util import yyyymmdd_to_ticks


def map_sphere_nodes(
        fs_beat_map: FSBeatMapFile,
        fs_info_dat: FSInfoDat,
        total_time_seconds: float,
) -> list[DDSphereNode]:

    def process_notes(note_type: FS_LEFT_NOTE | FS_RIGHT_NOTE, line_type: DD_LINE_LEFT | DD_LINE_RIGHT):
        all_lines_of_type = [
            o for o in fs_beat_map.obstacles if o.customData.dd_note_type == line_type
        ]
        all_notes = [
            n for n in fs_beat_map.notes if n.type == note_type
        ]
        non_overlapping_notes = [
            note for note in all_notes
            if not any(obstacle.time <= note.time < obstacle.end_time for obstacle in all_lines_of_type)
        ]
        return [
            DDSphereNode(
                noteOrder=round(note.time * ORDER_COUNT_PER_BEAT),
                time=(fs_info_dat.bps * note.time) / total_time_seconds,
                position=X_Y(x=note.to_dd_x, y=0),
                noteType=FS_TO_DD_NOTE_TYPE[note.type],
            )
            for note in non_overlapping_notes
        ]

    spheres = process_notes(FS_LEFT_NOTE, DD_LINE_LEFT) + \
        process_notes(FS_RIGHT_NOTE, DD_LINE_RIGHT)
    return sorted(spheres, key=lambda s: s.noteOrder)


def map_line_nodes(
        fs_beat_map: FSBeatMapFile,
        fs_info_dat: FSInfoDat,
        total_time_seconds: float,
) -> list[DDLineNode]:
    lines = []

    line_obstacles = [
        o for o in fs_beat_map.obstacles if o.customData.is_fs
    ]

    obstacles_by_type = {
        DD_LINE_LEFT: [
            o for o in line_obstacles if o.customData.dd_note_type == DD_LINE_LEFT
        ],
        DD_LINE_RIGHT: [
            o for o in line_obstacles if o.customData.dd_note_type == DD_LINE_RIGHT
        ],
    }

    index_in_line = 0
    line_group_id = 1
    last_obstacle = None
    for note_type, obstacles in obstacles_by_type.items():
        for obstacle in obstacles:
            if obstacle.is_part_of_last_obstacle(last_obstacle) and not obstacle.customData.is_fs_slider:
                index_in_line += 1
                is_left = obstacle.customData.position[0] < last_obstacle.customData.position[0]
                last_obstacle_x = lines[-1].position.x
                lines.append(
                    DDLineNode(
                        lineGroupId=line_group_id,
                        indexInLine=index_in_line,
                        noteOrder=round(obstacle.time * ORDER_COUNT_PER_BEAT),
                        time=(fs_info_dat.bps * obstacle.time) /
                        total_time_seconds,
                        position=X_Y(
                            last_obstacle_x +
                            (-1 if is_left else 1), y=0,
                        ),
                        noteType=note_type,
                    ),
                )
                index_in_line += 1
                lines.append(
                    DDLineNode(
                        lineGroupId=line_group_id,
                        indexInLine=index_in_line,
                        noteOrder=round(
                            obstacle.time * ORDER_COUNT_PER_BEAT,
                        ) + ORDER_COUNT_PER_BEAT / 4,
                        time=(fs_info_dat.bps * obstacle.time) /
                        total_time_seconds,
                        position=X_Y(
                            last_obstacle_x +
                            (-1 if is_left else 1), y=0,
                        ),
                        noteType=note_type,
                    ),
                )
                last_obstacle = obstacle
                continue

            if not obstacle.is_part_of_last_obstacle(last_obstacle):
                index_in_line = 0
                line_group_id += 1

            lines.append(
                DDLineNode(
                    lineGroupId=line_group_id,
                    indexInLine=index_in_line,
                    noteOrder=round(obstacle.time * ORDER_COUNT_PER_BEAT),
                    time=(fs_info_dat.bps * obstacle.time) /
                    total_time_seconds,
                    position=X_Y(x=obstacle.to_dd_x(), y=0),
                    noteType=note_type,
                ),
            )
            index_in_line += 1
            lines.append(
                DDLineNode(
                    lineGroupId=line_group_id,
                    indexInLine=index_in_line,
                    noteOrder=round(obstacle.end_time * ORDER_COUNT_PER_BEAT),
                    time=(fs_info_dat.bps * obstacle.time) /
                    total_time_seconds,
                    position=X_Y(x=obstacle.end_to_dd_x, y=0),
                    noteType=note_type,
                ),
            )
            last_obstacle = obstacle

    return lines


def map_down_and_jump_notes(
        fs_beat_map: FSBeatMapFile,
        fs_info_dat: FSInfoDat,
        total_time_seconds: float,
) -> list[DDRoadBlockNode]:
    def create_block(obstacle, position, position2D):
        return DDRoadBlockNode(
            noteOrder=round(obstacle.time * ORDER_COUNT_PER_BEAT) +
            (ORDER_COUNT_PER_BEAT / 16),
            time=(fs_info_dat.bps * obstacle.time) / total_time_seconds,
            position=position,
            position2D=position2D,
        )

    downs = [
        create_block(o, DDDownPos, DDDownPos2D)
        for o in fs_beat_map.obstacles if o.is_down
    ]
    ups = [
        create_block(o, DDJumpPos, DDJumpPos2D)
        for o in fs_beat_map.obstacles if o.is_up
    ]
    return sorted(downs + ups, key=lambda r: r.noteOrder)


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
        for difficulty in difficulty_set.difficultyBeatmaps:
            beat_map: FSBeatMapFile = difficulty.get_beatmap(fs_map_dir)

            sphere_notes = map_sphere_nodes(beat_map, fs_info, song_length)
            line_notes = map_line_nodes(beat_map, fs_info, song_length)
            road_block_notes = map_down_and_jump_notes(
                beat_map, fs_info, song_length,
            )

            total_note_count = len(sphere_notes + line_notes + road_block_notes)  # noqa
            dd_beat_map = DDBeatMap(
                data=DDBeatMapData(
                    name=fs_info.songName,
                    sphereNodes=sphere_notes,
                    lineNodes=line_notes,
                    roadBlockNodes=road_block_notes,
                ),
                BPM=fs_info.beatsPerMinute,
                NPS=str(round(total_note_count / song_length, 2)),
            )

            difficulty_name = f'{difficulty_set.beatmapCharacteristicName}_{difficulty.difficulty}'
            song_paths.append(
                dd_beat_map.save_to_file(
                    target_dir, f'{difficulty_name}.json',
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
        OstId=0,  # default
        CreateTicks=create_ticks,
        CreateTime=str(create_ticks),
        BeatMapId=random_9_digit_int(),
        SongName=fs_info.songName,
        SongLength=str(song_length),
        SongAuthorName=fs_info.songAuthorName,
        LevelAuthorName=fs_info.levelAuthorName,
        Bpm=str(fs_info.beatsPerMinute),
        SongPath=os.path.basename(song_path),
        CoverPath=os.path.basename(song_cover_path or '') or None,
        SongPreviewSection=fs_info.previewStartTime,
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
