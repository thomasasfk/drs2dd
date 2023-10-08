from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from dataclasses import field

from model.dancedash import DD_LEFT
from model.dancedash import DD_LINE_LEFT
from model.dancedash import DD_LINE_RIGHT
from model.dancedash import DD_RIGHT


@dataclass
class FSEditor:
    version: str


@dataclass
class FSEditorMetadata:
    lastEditedBy: str
    editors: dict[str, FSEditor]


@dataclass
class FSContributor:
    role: str
    name: str
    iconPath: str


@dataclass
class FSDatCustomData:
    contributors: list[FSContributor]
    editors: FSEditorMetadata


@dataclass
class FSBeatMapCustomData:
    difficultyLabel: str
    editorOffset: int
    editorOldOffset: int
    suggestions: list[str]
    requirements: list[str]


@dataclass
class FSBeatmap:
    difficulty: str
    difficultyRank: int
    beatmapFilename: str
    noteJumpMovementSpeed: int
    noteJumpStartBeatOffset: float
    customData: FSBeatMapCustomData

    def get_beatmap(self, map_dir: str) -> FSBeatMapFile:
        file_name = os.path.join(map_dir, self.beatmapFilename)
        beat_map_dict = json.load(open(file_name, encoding='utf-8'))
        return FSBeatMapFile.from_json_dict(beat_map_dict)


@dataclass
class FSDifficultyBeatMapSets:
    beatmapCharacteristicName: str
    difficultyBeatmaps: list[FSBeatmap]


@dataclass
class FSInfoDat:
    version: str
    songName: str
    songSubName: str
    songAuthorName: str
    levelAuthorName: str
    beatsPerMinute: int
    shuffle: int
    shufflePeriod: float
    previewStartTime: int
    previewDuration: int
    songFilename: str
    coverImageFilename: str
    environmentName: str
    allDirectionsEnvironmentName: str
    songTimeOffset: int
    customData: FSDatCustomData
    difficultyBeatmapSets: list[FSDifficultyBeatMapSets]

    @property
    def bps(self):
        return self.beatsPerMinute / 60

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> FSInfoDat:
        custom_data_raw = json_dict['_customData']

        def remove_underscore_from_keys(data):
            return {key.lstrip('_'): value for key, value in data.items()}

        contributors = [
            FSContributor(**remove_underscore_from_keys(contributor)) for contributor in
            custom_data_raw['_contributors']
        ] if '_contributors' in custom_data_raw else []

        editors = {
            editor: FSEditor(version=data['version']) for editor, data in custom_data_raw['_editors'].items() if
            editor != '_lastEditedBy'
        }

        custom_data = FSDatCustomData(
            contributors=contributors,
            editors=FSEditorMetadata(
                lastEditedBy=custom_data_raw['_editors']['_lastEditedBy'],
                editors=editors,
            ),
        )

        difficulty_beatmap_sets_raw = json_dict['_difficultyBeatmapSets']

        difficulty_beatmaps_list = []
        for dbset in difficulty_beatmap_sets_raw:
            beatmaps = [
                FSBeatmap(
                    difficulty=beatmap['_difficulty'],
                    difficultyRank=beatmap['_difficultyRank'],
                    beatmapFilename=beatmap['_beatmapFilename'],
                    noteJumpMovementSpeed=beatmap['_noteJumpMovementSpeed'],
                    noteJumpStartBeatOffset=beatmap['_noteJumpStartBeatOffset'],
                    customData=FSBeatMapCustomData(
                        difficultyLabel=beatmap['_customData'].get(
                            '_difficultyLabel',
                        ),
                        editorOffset=beatmap['_customData'].get(
                            '_editorOffset',
                        ),
                        editorOldOffset=beatmap['_customData'].get(
                            '_editorOldOffset',
                        ),
                        suggestions=beatmap['_customData'].get('_suggestions'),
                        requirements=beatmap['_customData'].get(
                            '_requirements',
                        ),
                    ),
                ) for beatmap in dbset['_difficultyBeatmaps']
            ]

            difficulty_beatmaps_list.append(
                FSDifficultyBeatMapSets(
                    beatmapCharacteristicName=dbset['_beatmapCharacteristicName'],
                    difficultyBeatmaps=beatmaps,
                ),
            )

        return cls(
            version=json_dict['_version'],
            songName=json_dict['_songName'],
            songSubName=json_dict['_songSubName'],
            songAuthorName=json_dict['_songAuthorName'],
            levelAuthorName=json_dict['_levelAuthorName'],
            beatsPerMinute=json_dict['_beatsPerMinute'],
            shuffle=json_dict['_shuffle'],
            shufflePeriod=json_dict['_shufflePeriod'],
            previewStartTime=json_dict['_previewStartTime'],
            previewDuration=json_dict['_previewDuration'],
            songFilename=json_dict['_songFilename'],
            coverImageFilename=json_dict['_coverImageFilename'],
            environmentName=json_dict['_environmentName'],
            allDirectionsEnvironmentName=json_dict['_allDirectionsEnvironmentName'],
            songTimeOffset=json_dict['_songTimeOffset'],
            customData=custom_data,
            difficultyBeatmapSets=difficulty_beatmaps_list,
        )

    @classmethod
    def from_json_file(cls, json_file: str) -> FSInfoDat:
        import json
        with open(json_file) as f:
            json_dict = json.load(f)
        return cls.from_json_dict(json_dict)


@dataclass
class FSBeatMapFileBookmark:
    time: int
    name: str
    color: list[float]


@dataclass
class FSBeatMapFileCustomData:
    time: float
    bookmarks: list[FSBeatMapFileBookmark]


@dataclass
class FSBeatMapFileEvent:
    time: int
    type: int
    value: int


@dataclass
class FSBeatMapFileNoteCustomData:
    position: tuple[float, float]


FS_LEFT_NOTE = 0
FS_RIGHT_NOTE = 1


@dataclass
class FSBeatMapFileNote:
    time: float
    lineIndex: int
    lineLayer: int
    type: int
    cutDirection: int
    customData: FSBeatMapFileNoteCustomData

    @property
    def to_dd_x(self) -> 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
        if not self.customData:
            if self.lineIndex == 0:
                return 2
            elif self.lineIndex == 1:
                return 4
            elif self.lineIndex == 2:
                return 6
            elif self.lineIndex == 3:
                return 8
        x = self.customData.position[0]
        x_min, x_max = -2, 1
        y_min, y_max = 2, 8
        y = (x - x_min) * (y_max - y_min) / (x_max - x_min) + y_min
        return round(y)


FS_RIGHT_COLOUR = (0.0, 1.0, 3.0, 1.0)
FS_LEFT_COLOUR = (2.0, 1.5, 0.0, 1.0)

FS_LONG_NOTE_TO_DD_NOTE_TYPE = {
    FS_RIGHT_COLOUR: DD_LINE_RIGHT,
    FS_LEFT_COLOUR: DD_LINE_LEFT,
}

FS_TO_DD_NOTE_TYPE = {
    FS_LEFT_NOTE: DD_LEFT,
    FS_RIGHT_NOTE: DD_RIGHT,
}


@dataclass
class FSBeatMapFileObstacleCustomData:
    track: str
    interactable: bool
    fake: bool
    scale: tuple
    position: tuple[float, float] | None
    color: tuple[float, float, float, float] | None
    localRotation: tuple[float, float, float] | None = None

    @property
    def height(self) -> float:
        return self.scale[1]

    @property
    def is_fs(self) -> bool:
        if not self.position:
            return False
        return self.height == 0.1 and self.position[1] == -0.25 and self.fake

    @property
    def is_fs_slider(self) -> bool:
        return self.scale[0] == 1.0 and self.is_fs

    @property
    def dd_note_type(self) -> DD_LINE_RIGHT | DD_LINE_LEFT | None:
        return FS_LONG_NOTE_TO_DD_NOTE_TYPE.get(self.color)


@dataclass
class FSBeatMapFileObstacle:
    time: float
    lineIndex: int
    type: int
    duration: int
    width: int
    customData: FSBeatMapFileObstacleCustomData

    def to_dd_x(self, x: float = None) -> 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
        x_min, x_max = -2, 1
        y_min, y_max = 2, 8
        if not x:
            x = self.customData.position[0]
        if x < x_min:
            x = -2
        elif x > x_max:
            x = 1
        y = (x - x_min) * (y_max - y_min) / (x_max - x_min) + y_min
        return round(y)

    @property
    def end_to_dd_x(self) -> 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
        opposite_angle = self.customData.localRotation[1]
        if opposite_angle == 0.0:
            return self.to_dd_x()
        # this angle calculation came out of nowhere, fix this with proper math or something idk
        opposite_length = self.duration * \
            math.sin(math.radians(opposite_angle))
        return self.to_dd_x(x=self.customData.position[0] + (opposite_length * 6.4))

    @property
    def has_rotation(self) -> bool:
        return self.customData.localRotation[1] != 0.0

    @property
    def end_time(self):
        return self.time + self.duration

    @property
    def is_down(self) -> bool:
        if not self.customData:
            return False
        if not self.customData.track:
            return False
        return self.customData.track.casefold() == 'DownArch'.casefold()

    @property
    def is_up(self) -> bool:
        if not self.customData:
            return False
        if not self.customData.track:
            return False
        return self.customData.track.casefold() == 'JumpBar'.casefold()

    def is_part_of_last_obstacle(self, last_obstacle: FSBeatMapFileObstacle | None) -> bool:
        if not last_obstacle:
            return False
        return last_obstacle.time <= self.time <= last_obstacle.end_time


@dataclass
class FSBeatMapFile:
    version: str
    customData: FSBeatMapFileCustomData
    notes: list[FSBeatMapFileNote]
    obstacles: list[FSBeatMapFileObstacle]
    events: list[FSBeatMapFileEvent] = field(default_factory=list)
    waypoints: list = field(default_factory=list)

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> FSBeatMapFile:
        custom_data = FSBeatMapFileCustomData(
            time=json_dict['_customData'].get('_time'),
            bookmarks=[
                FSBeatMapFileBookmark(
                    time=bm['_time'],
                    name=bm['_name'],
                    color=bm['_color'],
                ) for bm in json_dict['_customData'].get('_bookmarks') or []
            ],
        )

        events = [
            FSBeatMapFileEvent(
                time=event['_time'],
                type=event['_type'],
                value=event['_value'],
            ) for event in json_dict['_events']
        ]

        notes = [
            FSBeatMapFileNote(
                time=note['_time'],
                lineIndex=note['_lineIndex'],
                lineLayer=note['_lineLayer'],
                type=note['_type'],
                cutDirection=note['_cutDirection'],
                customData=FSBeatMapFileNoteCustomData(
                    position=tuple(note['_customData']['_position']),
                ) if '_customData' in note and '_position' in note['_customData'] else None,
            ) for note in json_dict['_notes']
        ]

        obstacles = [
            FSBeatMapFileObstacle(
                time=obstacle['_time'],
                lineIndex=obstacle['_lineIndex'],
                type=obstacle['_type'],
                duration=obstacle['_duration'],
                width=obstacle['_width'],
                customData=FSBeatMapFileObstacleCustomData(
                    track=obstacle['_customData'].get('_track'),
                    interactable=obstacle['_customData'].get('_interactable'),
                    fake=obstacle['_customData'].get('_fake'),
                    position=tuple(
                        obstacle['_customData']['_position'],
                    ) if '_position' in obstacle['_customData'] else None,
                    localRotation=tuple(obstacle['_customData']['_localRotation']) if '_localRotation' in obstacle[
                        '_customData'
                    ] else None,
                    scale=tuple(obstacle['_customData']['_scale']),
                    # type: ignore
                    color=tuple(
                        float(c)
                        for c in obstacle['_customData']['_color']
                    ) if '_color' in obstacle['_customData'] else None,
                ) if '_customData' in obstacle else None,
            ) for obstacle in json_dict['_obstacles']
        ]

        return cls(
            version=json_dict['_version'],
            customData=custom_data,
            events=events,
            notes=notes,
            obstacles=obstacles,
            waypoints=json_dict['_waypoints'],
        )

    @classmethod
    def from_json_file(cls, json_file: str) -> FSBeatMapFile:
        import json
        with open(json_file) as f:
            json_dict = json.load(f)
        return cls.from_json_dict(json_dict)
