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
from model.dancedash import X_Y
from model.dancerush import DRSSongData
from util import get_m4a_and_duration
from util import get_song_cover_path
from util import ORDER_COUNT_PER_BEAT


def create_dd_tracks_from_DRSSongData(
        drs_song_data: DRSSongData, target_dir: str,
) -> bool:
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f'Created directory: {target_dir}')

    dd_bmp = int(drs_song_data.info.bpm_max / 100)

    song_paths = []
    for attr, difficulty in drs_song_data.difficulties.with_attrs_as_str.items():
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
                sphereNodes=[],  # TODO: DO THE MAPPING LOL.
                lineNodes=[],    # TODO: DO THE MAPPING LOL.
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

    folder_path = TRACK_ID_TO_PATH.get(drs_song_data.song_id)
    song_path, song_length = get_m4a_and_duration(folder_path)
    if song_path and song_length:
        shutil.copy(song_path, target_dir)

    if song_cover_path := get_song_cover_path(folder_path):
        shutil.copy(song_cover_path, target_dir)

    drs_song_info_json = DDBeatMapInfoFile(
        EditorVersion='1.3.2',
        BeatMapId=drs_song_data.song_id,
        OstId=0,
        CreateTicks=0,
        CreateTime='',
        SongName=drs_song_data.info.title_name,
        SongLength=song_length or '-1',
        SongAuthorName=drs_song_data.info.artist_name,
        LevelAuthorName='https://github.com/thomasasfk/drs2dd',
        SongPreviewSection=0,
        Bpm=str(dd_bmp),
        SongPath=os.path.basename(song_path) if song_path else None,
        OstName=None,
        CoverPath=os.path.basename(
            song_cover_path,
        ) if song_cover_path else None,
        DRS_Easy=os.path.basename(song_paths[0]) if len(
            song_paths,
        ) > 0 else None,
        DRS_Normal=os.path.basename(song_paths[1]) if len(
            song_paths,
        ) > 1 else None,
        DRS_Hard=os.path.basename(song_paths[2]) if len(
            song_paths,
        ) > 2 else None,
        DRS_Expert=os.path.basename(song_paths[3]) if len(
            song_paths,
        ) > 3 else None,
    )

    info_file_path = os.path.join(
        target_dir, f'{drs_song_data.song_id}_info.json',
    )
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
    created = create_dd_tracks_from_DRSSongData(
        song_data, song_data.info.title_name,
    )

    print(f'Song {args.song_id} created?: {created}')
