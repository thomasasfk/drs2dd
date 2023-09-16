from __future__ import annotations

from drs2dd import create_dd_tracks_from_DRSSongData
from drsxml2json import ALL_TRACK_PATHS
from drsxml2json import get_songdata_from_track_id

if __name__ == '__main__':

    for song_id in ALL_TRACK_PATHS:
        if song_data := get_songdata_from_track_id(int(song_id)):
            created = create_dd_tracks_from_DRSSongData(
                song_data, f'tracks/{song_data.info.title_name}',
            )
            print(f'Song {song_id} created?: {created}')
