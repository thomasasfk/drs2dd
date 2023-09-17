from __future__ import annotations

import json
import os
import re
from dataclasses import asdict

import xmltodict

from model.dancerush import DRSSongData
from model.dancerush import DRSSongDifficulties
from model.dancerush import DRSSongDifficulty
from model.dancerush import DRSTrack

TRACK_LIST = r'resources/drs/datax/music/music-info-base.xml'
TRACKS_BASE_DIR = r'resources/drs/datax/music'
ALL_TRACK_PATHS = [x for x in os.listdir(TRACKS_BASE_DIR) if x.isdigit()]
TRACK_ID_TO_PATH = {
    int(x): os.path.join(TRACKS_BASE_DIR, x)
    for x in ALL_TRACK_PATHS
}


def get_songdata_from_track_id(track_id: int) -> DRSSongData | None:
    if os.getenv('HAS_XML'):
        return TRACK_ID_TO_SONGDATA.get(track_id)
    track_path = TRACK_ID_TO_PATH.get(track_id)
    if not track_path:
        return None
    songs_json_path = os.path.join(track_path, 'songs.json')
    if not os.path.exists(songs_json_path):
        return None
    songs_dict = json.load(open(songs_json_path, encoding='utf-8'))
    song_data = DRSSongData.from_json_dict(songs_dict)
    return song_data


if os.getenv('HAS_XML'):
    ALL_SONG_METADATA = open(TRACK_LIST, encoding='utf-8').read()
    ALL_SONG_METADATA_DICT = xmltodict.parse(ALL_SONG_METADATA)

    TRACK_ID_TO_SONGDATA = {}
    TRACK_ID_TO_SONGDATA_DICT = {}

    for song in ALL_SONG_METADATA_DICT['mdb']['music']:
        if os.getenv('TRACK') and song['@id'] != os.getenv('TRACK'):
            continue

        song_id = int(song['@id'])
        path = TRACK_ID_TO_PATH.get(song_id)

        files = os.listdir(path)
        track_id_to_path_dict = {
            re.search(r'_(\d[a-zA-Z])\.xml$', f).group(1): os.path.join(path, f)
            for f in files
            if re.search(r'_(\d[a-zA-Z])\.xml$', f)
        }
        if not track_id_to_path_dict:
            continue
        track_id_to_track = {
            key: DRSTrack.from_xml(
                value,
            ) for key, value in track_id_to_path_dict.items()
        }

        difficulties = DRSSongDifficulties(
            **{
                f'difficulty_{key}': DRSSongDifficulty(
                    difnum=int(
                        song['difficulty']
                        [f'fumen_{key}']['difnum']['#text'],
                    ),
                    track=track_id_to_track[key],
                ) for key, value in track_id_to_path_dict.items()
            },
        )

        song_data = DRSSongData.from_xml_dict(song, difficulties)
        song_data_dict = asdict(song_data)
        TRACK_ID_TO_SONGDATA[song_id] = song_data
        TRACK_ID_TO_SONGDATA_DICT[song_id] = song_data_dict


    def map_and_save_song(song_id, song_data_dict):
        song_json_path = os.path.join(
            TRACK_ID_TO_PATH[song_id], 'songs.json',
        )
        with open(song_json_path, 'w', encoding='utf-8') as f:
            json.dump(song_data_dict, f, ensure_ascii=False, indent=4)

        for key, data in song_data_dict['difficulties'].items():
            path = os.path.join(TRACK_ID_TO_PATH[song_id], f'{key}.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


    if __name__ == '__main__':
        if track_id := os.getenv('TRACK'):
            track_id = int(track_id)
            song_data_dict = TRACK_ID_TO_SONGDATA_DICT[track_id]
            map_and_save_song(track_id, song_data_dict)
            raise SystemExit(0)

        for song_id, song_data_dict in TRACK_ID_TO_SONGDATA_DICT.items():
            map_and_save_song(song_id, song_data_dict)
