from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from model.dancerush import DRS_LEFT
from model.dancerush import DRS_RIGHT

DD_LEFT = 8
DD_RIGHT = 9

DD_LINE_LEFT = 12
DD_LINE_RIGHT = 13

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
    isSliding: bool
    noteOrder: int
    time: float
    position: X_Y
    position2D: X_Y
    size: X_Y_Z
    noteType: int
    postionOffset: X_Y_Z | None  # Yes, postionOffset - not positionOffset.
    isPlayAudio: bool


@dataclass
class DDSphereNode:
    noteOrder: int
    time: float
    position: X_Y
    position2D: X_Y
    size: X_Y_Z
    noteType: DD_LEFT | DD_RIGHT
    postionOffset: dict | None
    isPlayAudio: bool


@dataclass
class DDBeatMapData:
    name: str
    intervalPerSecond: float
    gridSize: X_Y
    planeSize: X_Y
    orderCountPerBeat: int
    sphereNodes: list[DDSphereNode] = field(default_factory=list)
    lineNodes: list[DDLineNode] = field(default_factory=list)
    effectNodes: list = field(default_factory=list)
    roadBlockNodes: list = field(default_factory=list)
    trapNodes: list = field(default_factory=list)


@dataclass
class DDBeatMap:
    data: DDBeatMapData
    beatSubs: int
    BPM: int
    songStartOffset: float
    NPS: str
    developerMode: bool
    noteSpeed: float
    noteJumpOffset: float
    interval: float
    info: str


@dataclass
class DDBeatMapInfoFile:
    EditorVersion: str
    BeatMapId: int
    OstId: int
    CreateTicks: int
    CreateTime: str
    SongName: str
    SongLength: str
    SongAuthorName: str
    LevelAuthorName: str
    SongPreviewSection: int
    Bpm: str
    SongPath: str
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
