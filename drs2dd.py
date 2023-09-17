from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import asdict

from drsxml2json import get_songdata_from_track_id
from drsxml2json import TRACK_ID_TO_PATH
from model.dancedash import DDBeatMap
from model.dancedash import DDBeatMapData
from model.dancedash import DDBeatMapInfoFile
from model.dancedash import DDLineNode
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
        ticks_per_second = difficulty.track.info.end_tick / total_time_seconds
        time = track_step.tick_info.end_tick / ticks_per_second
        sphere = DDSphereNode(
            noteOrder=round(bps * time * ORDER_COUNT_PER_BEAT),
            time=time / total_time_seconds,
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
        ticks_per_second = difficulty.track.info.end_tick / total_time_seconds

        # DANCERUSH defines the first line step as a point, with the first point being the start of the line.
        # So we need to add a point at the start of the line for Dance Dash.
        initial_track_point = DRSTrackPoint(
            tick=track_step.tick_info.start_tick,
            left_pos=track_step.position_info.left_pos,
            right_pos=track_step.position_info.right_pos,
        )
        track_step.long_point.insert(0, initial_track_point)

        for index_in_line, drs_track_point in enumerate(track_step.long_point):
            drs_track_point: DRSTrackPoint = drs_track_point

            if drs_track_point.left_end_pos or drs_track_point.right_end_pos:
                continue  # handle shuffles later

            time = drs_track_point.tick / ticks_per_second
            line = DDLineNode(
                lineGroupId=line_group_id,
                indexInLine=index_in_line,
                isSliding=False,
                noteOrder=round(bps * time * ORDER_COUNT_PER_BEAT),
                time=time / total_time_seconds,
                position=X_Y(x=drs_track_point.to_dance_dash_x, y=0),
                position2D=X_Y(x=0, y=0),
                size=X_Y_Z(x=1, y=1, z=1),
                noteType=DRS_TO_DDS_LINE_NOTE_TYPE[track_step.kind],
                postionOffset=None,
                isPlayAudio=False,
            )
            lines.append(line)

    return lines


def create_dd_tracks_from_DRSSongData(
        drs_song_data: DRSSongData, target_dir: str,
) -> bool:
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f'Created directory: {target_dir}')

    dd_bmp = int(drs_song_data.info.bpm_max / 100)

    folder_path = TRACK_ID_TO_PATH.get(drs_song_data.song_id)
    song_path, song_length = get_mp3_and_duration(folder_path)
    if song_path and song_length:
        shutil.copy(song_path, target_dir)

    if song_cover_path := get_song_cover_path(folder_path):
        shutil.copy(song_cover_path, target_dir)

    if not song_path or not song_length:
        print(
            f'Could not find song path or song length for {drs_song_data.info.title_name}',
        )
        return False

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
                    # 10 seconds because the songs are 10 seconds longer... ?
                    float(song_length) - 10,
                    dd_bmp,
                ),
                lineNodes=map_line_nodes(
                    difficulty,
                    # 10 seconds because the songs are 10 seconds longer... ?
                    float(song_length) - 10,
                    dd_bmp,
                ),
                effectNodes=[],
                roadBlockNodes=[],
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

    easy, normal = song_paths
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
        help='ID of the song to process (number of folder)', required=True,
    )

    args = parser.parse_args()

    song_data = get_songdata_from_track_id(args.song_id)
    if not song_data:
        print(f'No song data found for song id {args.song_id}')
        raise SystemExit(1)

    created = create_dd_tracks_from_DRSSongData(
        song_data, song_data.info.title_name,
    )

    print(f'Song {args.song_id} created?: {created}')
