from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from model.dancerush import DRS_LEFT
from model.dancerush import DRS_RIGHT
from model.dancerush import DRSTrackPoint

DD_LEFT = 8
DD_RIGHT = 9

DD_LINE_LEFT = 12
DD_LINE_RIGHT = 13

DD_ROAD_BLOCK = 14

ORDER_COUNT_PER_BEAT = 24

DRS2DD_MAP_PREFIX = 44_52_53_000  # 44 = D, 52 = R, 53 = S

DRS_TO_DDS_NOTE_TYPE = {
    DRS_LEFT: DD_LEFT,
    DRS_RIGHT: DD_RIGHT,
}

DRS_TO_DDS_LINE_NOTE_TYPE = {
    DRS_LEFT: DD_LINE_LEFT,
    DRS_RIGHT: DD_LINE_RIGHT,
}


@dataclass
class X_Y:
    x: float | int
    y: float | int


@dataclass
class X_Y_Z(X_Y):
    z: float | int


@dataclass
class DDLineNode:
    lineGroupId: int
    indexInLine: int
    noteOrder: int
    time: float
    position: X_Y
    noteType: int
    position2D: X_Y = X_Y(x=0, y=0)
    size: X_Y_Z = X_Y_Z(x=1, y=1, z=1)
    isPlayAudio: bool = False
    postionOffset: X_Y_Z | None = None
    isSliding: bool = False

    def line_end(self, track_point: DRSTrackPoint, index: int):
        line = deepcopy(self)
        line.position.x = track_point.to_dance_dash_end_x
        line.indexInLine = index
        return line

    @property
    def tail(self):
        line = deepcopy(self)
        line.noteOrder += ORDER_COUNT_PER_BEAT / 4
        line.indexInLine += 1
        return line


@dataclass
class DDSphereNode:
    noteOrder: int
    time: float
    position: X_Y
    noteType: DD_LEFT | DD_RIGHT
    position2D: X_Y = X_Y(x=0, y=0)
    size: X_Y_Z = X_Y_Z(x=1, y=1, z=1)
    postionOffset: dict | None = None
    isPlayAudio: bool = False


DDJumpPos2D = X_Y(x=0.0, y=0.0)
DDDownPos2D = X_Y(x=0.0, y=0.0)

DDJumpPos = X_Y(x=5, y=-1)
DDDownPos = X_Y(x=5, y=10)


@dataclass
class DDRoadBlockNode:
    noteOrder: int
    time: float
    position: X_Y
    position2D: X_Y
    length: int = 1
    postionOffset: X_Y_Z = X_Y_Z(x=0, y=0, z=0)
    size: X_Y_Z = X_Y_Z(x=1, y=1, z=1)
    noteType: DD_ROAD_BLOCK = DD_ROAD_BLOCK
    isPlayAudio: bool = False
    startPosSelctOrder: int = -1
    endPosSelctOrder: int = -1
    duration: float = 0.000157683025


@dataclass
class DDBeatMapData:
    name: str
    sphereNodes: list[DDSphereNode]
    lineNodes: list[DDLineNode]
    roadBlockNodes: list[DDRoadBlockNode]
    intervalPerSecond: float = 0.0
    gridSize: X_Y = X_Y(x=0, y=0)
    planeSize: X_Y = X_Y(x=0, y=0)
    orderCountPerBeat: int = ORDER_COUNT_PER_BEAT
    effectNodes: list = field(default_factory=list)
    trapNodes: list = field(default_factory=list)


@dataclass
class DDBeatMap:
    data: DDBeatMapData
    BPM: int
    NPS: str
    beatSubs: int = 1
    songStartOffset: float = 0.0
    developerMode: bool = False
    noteSpeed: float = 1.0
    noteJumpOffset: float = 0.0
    interval: float = 1.0
    info: str = ''

    def save_to_file(self, target_dir: str, filename: str) -> str:
        target_difficulty_path = os.path.join(target_dir, filename)
        with open(target_difficulty_path, 'w') as f:
            json.dump(asdict(self), f, indent=4)
        return target_difficulty_path

    @property
    def block_less(self):
        beat_map = deepcopy(self)
        beat_map.data.name = f'{beat_map.data.name} (Blockless)'
        beat_map.data.roadBlockNodes = []
        return beat_map


@dataclass
class DDBeatMapInfoFile:
    BeatMapId: int
    SongName: str
    SongLength: str
    SongAuthorName: str
    Bpm: str
    SongPath: str
    CreateTicks: int
    CreateTime: str
    OstId: int
    EditorVersion: str = '1.3.2'
    LevelAuthorName: str = 'https://github.com/thomasasfk/drs2dd'
    SongPreviewSection: int = 0
    OstName: str | None = None
    CoverPath: str | None = None
    DDVR_Easy: str | None = None
    DDVR_Normal: str | None = None
    DDVR_Hard: str | None = None
    DRS_Easy: str | None = None
    DRS_Normal: str | None = None
    DRS_Hard: str | None = None
    DRS_Expert: str | None = None
    DRS_Master: str | None = None
    DRS_ACE: str | None = None
    DDVR_Env: str | None = None
    DRS_Env: str | None = None

    def save_to_file(self, target_dir: str) -> str:
        info_file_path = os.path.join(target_dir, 'info.json')
        with open(info_file_path, 'w') as f:
            json.dump(asdict(self), f, indent=4)
        return info_file_path


@dataclass
class DDAlbumInfo:
    BeatMapIdList: list[int]
    OstId: int
    OstName: str
    CoverPath: str
    CreateTime: int

    def save_to_file(self, target_dir: str) -> str:
        album_info_file_path = os.path.join(target_dir, 'info.json')
        with open(album_info_file_path, 'w') as f:
            json.dump(asdict(self), f, indent=4)
        return album_info_file_path
