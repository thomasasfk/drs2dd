from __future__ import annotations

import json
import os
from dataclasses import dataclass
from dataclasses import field

from model.dancedash import DD_LINE_LEFT
from model.dancedash import DD_LINE_RIGHT


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
        ]

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
                        difficultyLabel=beatmap['_customData']['_difficultyLabel'],
                        editorOffset=beatmap['_customData']['_editorOffset'],
                        editorOldOffset=beatmap['_customData']['_editorOldOffset'],
                        suggestions=beatmap['_customData']['_suggestions'],
                        requirements=beatmap['_customData']['_requirements'],
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


@dataclass
class FSBeatMapFileNote:
    time: float
    lineIndex: int
    lineLayer: int
    type: int
    cutDirection: int
    customData: FSBeatMapFileNoteCustomData


FS_RIGHT_COLOUR = (0.0, 1.0, 3.0, 1.0)
FS_LEFT_COLOUR = (2.0, 1.5, 0.0, 1.0)

FS_LONG_NOTE_TO_DD_NOTE_TYPE = {
    FS_RIGHT_COLOUR: DD_LINE_RIGHT,
    FS_LEFT_COLOUR: DD_LINE_LEFT,
}


@dataclass
class FSBeatMapFileObstacleCustomData:
    interactable: bool
    fake: bool
    position: tuple[float, float]
    scale: tuple
    color: tuple[float, float, float, float]
    localRotation: tuple[float, float, float] | None = None

    @property
    def height(self):
        return self.scale[1]

    @property
    def y(self):
        _, y = self.position
        return y

    @property
    def x(self):
        x, _ = self.position
        return x

    @property
    def is_fs(self):
        return all(
            [
                self.height == 0.1,
                self.y == -0.25,
                self.fake,
            ],
        )

    @property
    def is_fs_slider(self) -> bool:
        return self.scale[0] == 1.0 and self.is_fs

    @property
    def is_tail(self) -> bool:
        return self.scale[0] == 1.5 and self.is_fs

    @property
    def dd_x(self):
        if not self.is_fs:
            raise ValueError('This is not a FS note')

        if self.x < -2.5 or self.x > 1.5:
            raise ValueError('Input should be between -1.5 and 1.5')

        normalized = (self.x + 2.5) / 4.0
        mapped_value = round(normalized * 8 + 1)
        return int(mapped_value)

    @property
    def dd_note_type(self):
        return FS_LONG_NOTE_TO_DD_NOTE_TYPE[self.color]


@dataclass
class FSBeatMapFileObstacle:
    time: float
    lineIndex: int
    type: int
    duration: int
    width: int
    customData: FSBeatMapFileObstacleCustomData

    def is_part_of_last_obstacle(self, last_obstacle: FSBeatMapFileObstacle) -> bool:
        if self.time < last_obstacle.time:
            return False

        if self.time > last_obstacle.time + last_obstacle.duration:
            return False

        return True


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
            time=json_dict['_customData']['_time'],
            bookmarks=[
                FSBeatMapFileBookmark(
                    time=bm['_time'],
                    name=bm['_name'],
                    color=bm['_color'],
                ) for bm in json_dict['_customData']['_bookmarks']
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
                ),
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
                    interactable=obstacle['_customData']['_interactable'],
                    fake=obstacle['_customData']['_fake'],
                    position=tuple(obstacle['_customData']['_position']),
                    localRotation=tuple(obstacle['_customData']['_localRotation']) if '_localRotation' in obstacle[
                        '_customData'
                    ] else None,
                    scale=tuple(obstacle['_customData']['_scale']),
                    # type: ignore
                    color=tuple(
                        float(c)
                        for c in obstacle['_customData']['_color']
                    ),
                ),
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
