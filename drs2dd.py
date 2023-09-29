from __future__ import annotations

import argparse
import os
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from drsxml2json import ALL_TRACK_PATHS
from drsxml2json import get_songdata_from_track_id
from drsxml2json import TRACK_ID_TO_PATH
from model.dancedash import DDAlbumInfo
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
from model.dancedash import ORDER_COUNT_PER_BEAT
from model.dancedash import X_Y
from model.dancerush import ALBUM_NAME
from model.dancerush import DEFAULT_TRACK_DIR
from model.dancerush import DRS_ALBUM_ID
from model.dancerush import DRS_DOWN
from model.dancerush import DRS_JUMP
from model.dancerush import DRSSongData
from model.dancerush import DRSSongDifficulty
from model.dancerush import DRSTrackPoint
from model.dancerush import OUTPUT_ZIP_NAME
from util import create_valid_filename
from util import get_drs_ogg_and_duration
from util import get_song_cover_path
from util import yyyymmdd_to_ticks
from util import zipdir


def map_sphere_nodes(
        difficulty: DRSSongDifficulty,
        total_time_seconds: float,
        bps: float,
        ticks_per_second: float,
) -> list[DDSphereNode]:
    spheres = []
    for track_step in difficulty.track.sequence_data:
        if track_step.long_point or track_step.is_down_or_up:
            continue

        if track_step.tick_info.start_tick:
            seconds = track_step.tick_info.end_tick / ticks_per_second
        else:
            seconds = track_step.tick_info.stime_ms / 1000

        spheres.append(
            DDSphereNode(
                noteOrder=round(bps * seconds * ORDER_COUNT_PER_BEAT),
                time=seconds / total_time_seconds,
                position=X_Y(x=track_step.position_info.to_dance_dash_x, y=0),
                noteType=DRS_TO_DDS_NOTE_TYPE[track_step.kind],
            ),
        )
    return spheres


def map_line_nodes(
        difficulty: DRSSongDifficulty,
        total_time_seconds: float,
        bps: float,
        ticks_per_second: float,
) -> list[DDLineNode]:
    lines = []
    for line_group_id, track_step in enumerate(difficulty.track.sequence_data, start=1):
        if not track_step.long_point or track_step.is_down_or_up:
            continue

        track_step.long_point.insert(
            0, DRSTrackPoint(
                tick=track_step.tick_info.start_tick,
                left_pos=track_step.position_info.left_pos,
                right_pos=track_step.position_info.right_pos,
                point_time=track_step.tick_info.stime_ms,
            ),
        )

        last_was_shuffle_end = False
        index_in_line = 0
        for drs_track_point in track_step.long_point:
            last_was_shuffle_end = False
            index_in_line += 1

            if drs_track_point.tick:
                seconds = drs_track_point.tick / ticks_per_second
            else:
                seconds = drs_track_point.point_time / 1000

            lines.append(
                DDLineNode(
                    lineGroupId=line_group_id,
                    indexInLine=index_in_line,
                    noteOrder=round(bps * seconds * ORDER_COUNT_PER_BEAT),
                    time=seconds / total_time_seconds,
                    position=X_Y(x=drs_track_point.to_dance_dash_x, y=0),
                    noteType=DRS_TO_DDS_LINE_NOTE_TYPE[track_step.kind],
                ),
            )

            if drs_track_point.left_end_pos and drs_track_point.right_end_pos:
                index_in_line += 1
                lines.append(
                    lines[-1].line_end(drs_track_point, index_in_line),
                )
                last_was_shuffle_end = True

        if last_was_shuffle_end:
            lines.append(lines[-1].tail)
    return lines


def map_down_and_jump_notes(
        difficulty: DRSSongDifficulty,
        total_time_seconds: float,
        bps: float,
        ticks_per_second: float,
) -> list[DDRoadBlockNode]:
    road_blocks = []
    for track_step in difficulty.track.sequence_data:
        if not track_step.is_down_or_up:
            continue

        if track_step.tick_info.start_tick:
            seconds = track_step.tick_info.end_tick / ticks_per_second
        else:
            seconds = track_step.tick_info.stime_ms / 1000

        note_order = round(bps * seconds * ORDER_COUNT_PER_BEAT)
        if track_step.kind == DRS_JUMP:
            # user jumps OVER in DD, not ON like in DRS
            note_order += ORDER_COUNT_PER_BEAT / 2
        elif track_step.kind == DRS_DOWN:
            # user needs to duck UNDER in DD, not go down ON like in DRS
            note_order += ORDER_COUNT_PER_BEAT / 16

        road_blocks.append(
            DDRoadBlockNode(
                noteOrder=note_order,
                time=seconds / total_time_seconds,
                position=DDJumpPos if track_step.kind == DRS_JUMP else DDDownPos,
                position2D=DDJumpPos2D if track_step.kind == DRS_JUMP else DDDownPos2D,
            ),
        )
    return road_blocks


def create_dd_tracks_from_DRSSongData(drs_song_data: DRSSongData, target_dir: str = None) -> DDBeatMapInfoFile:
    if not target_dir:
        target_dir = f'{DEFAULT_TRACK_DIR}/{create_valid_filename(drs_song_data.info.title_name)}/'

    highest_bpm = max(
        drs_song_data.difficulties.difficulty_1a.track.info.bpm_info, key=lambda x: x.bpm,
    ).bpm
    # note we don't use drs_song_data.info.bpm_max as it is not always correct... sometimes higher bpms exist.
    # not sure why.
    dd_bpm = int(highest_bpm / 100)
    dd_bps = dd_bpm / 60

    folder_path = TRACK_ID_TO_PATH.get(drs_song_data.song_id)
    song_path, song_length = get_drs_ogg_and_duration(folder_path)
    if not song_path or not song_length:
        print(
            f'No song found for {drs_song_data.info.title_name} ({drs_song_data.song_id})',
        )
        return None

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    new_song_path = os.path.join(target_dir, drs_song_data.ogg)
    shutil.copy(song_path, new_song_path)
    song_path = new_song_path
    if song_cover_path := get_song_cover_path(folder_path):
        new_song_cover_path = os.path.join(target_dir, drs_song_data.png)
        shutil.copy(song_cover_path, new_song_cover_path)
        song_cover_path = new_song_cover_path

    song_paths = []
    for attr, difficulty in drs_song_data.difficulties.with_attrs_as_str.items():
        if attr in ('difficulty_2a', 'difficulty_2b'):  # 2 player difficulties
            continue

        ticks_per_second = None
        if difficulty.track.clip and difficulty.track.clip.end_time:
            end_time_seconds = difficulty.track.clip.end_time / 1000
            ticks_per_second = difficulty.track.info.end_tick / end_time_seconds

        song_length_f = float(song_length)
        sphere_notes = map_sphere_nodes(
            difficulty, song_length_f, dd_bps, ticks_per_second,
        )
        line_notes = map_line_nodes(
            difficulty, song_length_f, dd_bps, ticks_per_second,
        )
        road_block_notes = map_down_and_jump_notes(
            difficulty, song_length_f, dd_bps, ticks_per_second,
        )

        total_note_count = len(sphere_notes + line_notes + road_block_notes)  # noqa
        dd_beat_map = DDBeatMap(
            data=DDBeatMapData(
                name=f'{drs_song_data.info.title_name} {attr}',
                sphereNodes=sphere_notes,
                lineNodes=line_notes,
                roadBlockNodes=road_block_notes,
            ),
            BPM=dd_bpm,
            NPS=str(round(total_note_count / song_length_f, 2)),
        )

        song_paths.append(
            dd_beat_map.save_to_file(
                target_dir, f'{attr}.json',
            ),
        )
        song_paths.append(
            dd_beat_map.block_less.save_to_file(
                target_dir, f'{attr}_blockless.json',
            ),
        )

    normal, normal_no_blocks, easy, easy_no_blocks = song_paths
    create_ticks = yyyymmdd_to_ticks(str(drs_song_data.info.distribution_date))
    drs_beat_map_info = DDBeatMapInfoFile(
        CreateTicks=create_ticks,
        CreateTime=str(create_ticks),
        BeatMapId=drs_song_data.song_id,
        SongName=drs_song_data.info.title_name,
        SongLength=song_length,
        SongAuthorName=drs_song_data.info.artist_name,
        Bpm=str(dd_bpm),
        SongPath=os.path.basename(song_path),
        CoverPath=os.path.basename(song_cover_path or '') or None,
        DRS_Easy=os.path.basename(easy_no_blocks),
        DRS_Normal=os.path.basename(normal_no_blocks),
        DRS_Hard=os.path.basename(easy),
        DRS_Expert=os.path.basename(normal),
    )
    drs_beat_map_info.save_to_file(target_dir)

    print(f'Created {drs_song_data.info.title_name} ({drs_song_data.song_id})')
    return drs_beat_map_info


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create Dance Dash tracks from DANCERUSH STARDOM Song Data',
    )
    parser.add_argument(
        '--song-id',
        type=int,
        help='ID of the song to process (number of folder)',
    )

    args = parser.parse_args()
    if args.song_id:
        song_data = get_songdata_from_track_id(args.song_id)
        if not song_data:
            print(f'No song data found for song id {args.song_id}')
            raise SystemExit(1)

        target_directory = create_valid_filename(song_data.info.title_name)
        info_file = create_dd_tracks_from_DRSSongData(
            song_data, target_directory,
        )
        print(f'Song {args.song_id} created?: {bool(info_file)}')
        raise SystemExit(0)

    if not os.path.exists(DEFAULT_TRACK_DIR):
        os.makedirs(DEFAULT_TRACK_DIR)

    tracks = []

    def _process_track(song_id):
        if _song_data := get_songdata_from_track_id(int(song_id)):
            try:
                if _info_file := create_dd_tracks_from_DRSSongData(_song_data):
                    tracks.append(_info_file)
            except Exception as e:
                print(f'Error creating song {song_id}: {e}')

    with ThreadPoolExecutor() as executor:
        executor.map(_process_track, ALL_TRACK_PATHS)
    print(f'Created {len(tracks)} tracks')

    album_info = DDAlbumInfo(
        OstName='DANCERUSH STARDOM',
        BeatMapIdList=[track.BeatMapId for track in tracks],
        OstId=DRS_ALBUM_ID,
        CoverPath='DANCERUSH_STARDOM.jpg',
        CreateTime=yyyymmdd_to_ticks(datetime.now().strftime('%Y%m%d')),
    ).save_to_file(DEFAULT_TRACK_DIR)
    print(f'Created album info file: {album_info}')

    shutil.copy('resources/drs/DANCERUSH_STARDOM.jpg', DEFAULT_TRACK_DIR)
    if not os.path.exists('bin'):
        os.makedirs('bin')

    print('Zipping tracks...')
    with zipfile.ZipFile(f'bin/{OUTPUT_ZIP_NAME}', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(
            DEFAULT_TRACK_DIR, zipf,
            f'Dance Dash_Data/StreamingAssets/NewDLC/{ALBUM_NAME}',
        )

    print(f'Created bin/{OUTPUT_ZIP_NAME}')
    raise SystemExit(0)
