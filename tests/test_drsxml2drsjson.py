from __future__ import annotations

from drsxml2drsjson import get_songdata_from_track_id
from model.dancerush import DRSSongData


def test_get_songdata_from_track_id():
    song_data = get_songdata_from_track_id(187)
    assert isinstance(song_data, DRSSongData)
