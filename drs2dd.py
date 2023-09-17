from __future__ import annotations

import argparse
import json
import os
import shutil
from copy import deepcopy
from dataclasses import asdict

from drsxml2json import ALL_TRACK_PATHS
from drsxml2json import get_songdata_from_track_id
from drsxml2json import TRACK_ID_TO_PATH
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
from model.dancedash import DRS_TO_DDS_LINE_NOTE_TYPE
from model.dancedash import DRS_TO_DDS_NOTE_TYPE
from model.dancedash import X_Y
from model.dancedash import X_Y_Z
from model.dancerush import DRS_DOWN
from model.dancerush import DRS_JUMP
from model.dancerush import DRSSongData
from model.dancerush import DRSSongDifficulty
from model.dancerush import DRSTrackPoint
from model.dancerush import DRSTrackStep
from util import get_mp3_and_duration
from util import get_song_cover_path
from util import ORDER_COUNT_PER_BEAT


def map_sphere_nodes(
        difficulty: DRSSongDifficulty,
        total_time_seconds: float,
        bpm: int,
) -> list[DDSphereNode]:
    spheres = []
    for track_step in difficulty.track.sequence_data:
        track_step: DRSTrackStep = track_step
        # Long note get mapped elsewhere
        if track_step.long_point or track_step.kind in (DRS_DOWN, DRS_JUMP):
            continue
        bps = bpm / 60
        if track_step.tick_info.start_tick:
            end_time_seconds = difficulty.track.clip.end_time / 1000
            ticks_per_second = difficulty.track.info.end_tick / end_time_seconds
            seconds = track_step.tick_info.end_tick / ticks_per_second
        else:
            seconds = track_step.tick_info.stime_ms / 1000

        time = seconds / total_time_seconds
        sphere = DDSphereNode(
            noteOrder=round(bps * seconds * ORDER_COUNT_PER_BEAT),
            time=time,
            position=X_Y(x=track_step.position_info.to_dance_dash_x, y=0),
            position2D=X_Y(x=0, y=0),
            size=X_Y_Z(x=1, y=1, z=1),
            noteType=DRS_TO_DDS_NOTE_TYPE[track_step.kind],
            postionOffset=None,
            isPlayAudio=False,
        )
        spheres.append(sphere)

    return spheres


def map_line_nodes(
        difficulty: DRSSongDifficulty,
        total_time_seconds: float,
        bpm: int,
) -> list[DDLineNode]:
    lines = []
    for line_group_id, track_step in enumerate(difficulty.track.sequence_data, start=1):
        track_step: DRSTrackStep = track_step
        if not track_step.long_point or track_step.kind in (DRS_DOWN, DRS_JUMP):
            continue

        bps = bpm / 60

        # DANCERUSH defines the first line step as a point, with the first point being the start of the line.
        # So we need to add a point at the start of the line for Dance Dash.
        initial_track_point = DRSTrackPoint(
            tick=track_step.tick_info.start_tick,
            left_pos=track_step.position_info.left_pos,
            right_pos=track_step.position_info.right_pos,
            point_time=track_step.tick_info.stime_ms,
        )
        track_step.long_point.insert(0, initial_track_point)

        index_in_line = 0
        for drs_track_point in track_step.long_point:
            index_in_line += 1
            drs_track_point: DRSTrackPoint = drs_track_point

            if drs_track_point.tick is not None:
                end_time_seconds = difficulty.track.clip.end_time / 1000
                ticks_per_second = difficulty.track.info.end_tick / end_time_seconds
                seconds = drs_track_point.tick / ticks_per_second
            else:
                seconds = drs_track_point.point_time / 1000

            line = DDLineNode(
                lineGroupId=line_group_id,
                indexInLine=index_in_line,
                isSliding=False,
                noteOrder=round(bps * seconds * ORDER_COUNT_PER_BEAT),
                time=seconds / total_time_seconds,
                position=X_Y(x=drs_track_point.to_dance_dash_x, y=0),
                position2D=X_Y(x=0, y=0),
                size=X_Y_Z(x=1, y=1, z=1),
                noteType=DRS_TO_DDS_LINE_NOTE_TYPE[track_step.kind],
                postionOffset=None,
                isPlayAudio=False,
            )
            lines.append(line)

            if drs_track_point.left_end_pos and drs_track_point.right_end_pos:
                index_in_line += 1
                end_line = deepcopy(line)
                end_line.position.x = drs_track_point.to_dance_dash_end_x
                end_line.indexInLine = index_in_line
                lines.append(end_line)

    return lines


def map_down_and_jump_notes(
        difficulty: DRSSongDifficulty,
        total_time_seconds: float,
        bpm: int,
) -> list[DDRoadBlockNode]:

    road_blocks = []
    for track_step in difficulty.track.sequence_data:
        if track_step.kind not in (DRS_DOWN, DRS_JUMP):
            continue

        bps = bpm / 60
        if track_step.tick_info.start_tick:
            end_time_seconds = difficulty.track.clip.end_time / 1000
            ticks_per_second = difficulty.track.info.end_tick / end_time_seconds
            seconds = track_step.tick_info.end_tick / ticks_per_second
        else:
            seconds = track_step.tick_info.stime_ms / 1000

        note_order = round(bps * seconds * ORDER_COUNT_PER_BEAT)
        if track_step.kind == DRS_JUMP:
            # user jumps OVER in DD, not ON like in DRS
            note_order += ORDER_COUNT_PER_BEAT / 2

        road_block = DDRoadBlockNode(
            noteOrder=note_order,
            time=seconds / total_time_seconds,
            position=DDJumpPos if track_step.kind == DRS_JUMP else DDDownPos,
            position2D=DDJumpPos2D if track_step.kind == DRS_JUMP else DDDownPos2D,
        )
        road_blocks.append(road_block)

    return road_blocks


def create_dd_tracks_from_DRSSongData(
        drs_song_data: DRSSongData, target_dir: str,
) -> bool:
    dd_bmp = int(drs_song_data.info.bpm_max / 100)
    folder_path = TRACK_ID_TO_PATH.get(drs_song_data.song_id)
    song_path, song_length = get_mp3_and_duration(folder_path)

    if not song_path or not song_length:
        print(
            f'Could not find song path or song length for {drs_song_data.info.title_name}',
        )
        return False

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f'Created directory: {target_dir}')

    if song_path and song_length:
        shutil.copy(song_path, target_dir)

    if song_cover_path := get_song_cover_path(folder_path):
        shutil.copy(song_cover_path, target_dir)

    song_paths = []
    for attr, difficulty in drs_song_data.difficulties.with_attrs_as_str.items():

        if attr in ('difficulty_2a', 'difficulty_2b'):  # 2 player difficulties
            continue

        target_difficulty_path = os.path.join(
            target_dir, f'{drs_song_data.song_id}_{attr}.json',
        )

        song_paths.append(target_difficulty_path)
        drs_beat_map = DDBeatMap(
            data=DDBeatMapData(
                name=f'{drs_song_data.info.title_name} {attr}',
                intervalPerSecond=0.0,
                gridSize=X_Y(x=0, y=0),
                planeSize=X_Y(x=0, y=0),
                orderCountPerBeat=ORDER_COUNT_PER_BEAT,
                sphereNodes=map_sphere_nodes(
                    difficulty,
                    float(song_length),
                    dd_bmp,
                ),
                lineNodes=map_line_nodes(
                    difficulty,
                    float(song_length),
                    dd_bmp,
                ),
                effectNodes=[],
                roadBlockNodes=map_down_and_jump_notes(
                    difficulty,
                    float(song_length),
                    dd_bmp,
                ),
                trapNodes=[],
            ),
            beatSubs=1,
            BPM=dd_bmp,
            songStartOffset=0.0,
            NPS='0.0',
            developerMode=False,
            noteSpeed=1.0,
            noteJumpOffset=0.0,
            interval=1.0,
            info='',
        )
        with open(target_difficulty_path, 'w') as f:
            json.dump(asdict(drs_beat_map), f, indent=4)
            print(f'Created file: {target_difficulty_path}')

    normal, easy = song_paths
    drs_song_info_json = DDBeatMapInfoFile(
        EditorVersion='1.3.2',
        BeatMapId=drs_song_data.song_id,
        OstId=0,
        CreateTicks=0,
        CreateTime='',
        SongName=drs_song_data.info.title_name,
        SongLength=song_length,
        SongAuthorName=drs_song_data.info.artist_name,
        LevelAuthorName='https://github.com/thomasasfk/drs2dd',
        SongPreviewSection=0,
        Bpm=str(dd_bmp),
        SongPath=os.path.basename(song_path or '') or None,
        OstName=None,
        CoverPath=os.path.basename(song_cover_path or '') or None,
        DRS_Easy=os.path.basename(easy),
        DRS_Normal=os.path.basename(normal),
    )

    info_file_path = os.path.join(target_dir, 'info.json')
    with open(info_file_path, 'w') as f:
        json.dump(asdict(drs_song_info_json), f, indent=4)
        print(f'Created file: {info_file_path}')

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create DD tracks from DRS Song Data',
    )
    parser.add_argument(
        '--song-id', type=int,
        help='ID of the song to process (number of folder)',
    )

    args = parser.parse_args()

    if args.song_id:
        song_data = get_songdata_from_track_id(args.song_id)
        if not song_data:
            print(f'No song data found for song id {args.song_id}')
            raise SystemExit(1)

        created = create_dd_tracks_from_DRSSongData(
            song_data, song_data.info.title_name,
        )

        print(f'Song {args.song_id} created?: {created}')
        raise SystemExit(0)

    for song_id in ALL_TRACK_PATHS:
        if song_data := get_songdata_from_track_id(int(song_id)):
            try:
                created = create_dd_tracks_from_DRSSongData(
                    song_data, f'tracks/{song_data.info.title_name}',
                )
            except Exception as e:
                print(f'Error creating song {song_id}: {e}')
                created = False
            print(f'Song {song_id} created?: {created}')
