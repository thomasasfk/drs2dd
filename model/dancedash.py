from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

LEFT_NOTE = 8
RIGHT_NOTE = 9


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
    Ticks: int


@dataclass
class DDLSphereNode:
    noteOrder: int
    time: float
    position: X_Y
    position2D: X_Y
    size: X_Y_Z
    noteType: int
    postionOffset: dict | None
    isPlayAudio: bool


def create_note_sphere(
        time: float,
        position: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9,
        note_order: int,
        note_type: LEFT_NOTE | RIGHT_NOTE,
):
    return DDLSphereNode(
        noteOrder=note_order,
        time=time,
        position=X_Y(x=position, y=0),
        position2D=X_Y(x=0, y=0),
        size=X_Y_Z(x=1, y=1, z=1),
        noteType=note_type,
        postionOffset=None,
        isPlayAudio=False,
    )


@dataclass
class DDBeatMapData:
    name: str
    intervalPerSecond: float
    gridSize: X_Y
    planeSize: X_Y
    orderCountPerBeat: int
    sphereNodes: list[DDLSphereNode] = field(default_factory=list)
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

    @classmethod
    def create(
            cls,
            name: str,
            interval_per_second: float,
            order_count_per_beat: int,
            sphere_nodes: list[DDLSphereNode],
            beat_subs: int,
            bpm: int,
            info: str,
    ):
        return cls(
            data=DDBeatMapData(
                name=name,
                intervalPerSecond=interval_per_second,
                gridSize=X_Y(x=0, y=0),
                planeSize=X_Y(x=0, y=0),
                orderCountPerBeat=order_count_per_beat,
                sphereNodes=sphere_nodes,
                lineNodes=[],
                effectNodes=[],
                roadBlockNodes=[],
                trapNodes=[],
            ),
            beatSubs=beat_subs,
            BPM=bpm,
            songStartOffset=-0.4,  # -0.4 is arbitrary, figure out a better value. (because we detect notes early)
            NPS='0.0',
            developerMode=False,
            noteSpeed=1.0,
            noteJumpOffset=0.0,
            interval=1.0,
            info=info,
        )
