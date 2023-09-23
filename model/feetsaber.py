from __future__ import annotations

import json
import os
from dataclasses import dataclass


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


@dataclass
class FSBeatMapFileObstacleCustomData:
    interactable: bool
    fake: bool
    position: tuple[float, float]
    scale: tuple[float, float]
    color: tuple[float, float, float, float]
    localRotation: tuple[float, float, float] | None = None


@dataclass
class FSBeatMapFileObstacle:
    time: float
    lineIndex: int
    type: int
    duration: int
    width: int
    customData: FSBeatMapFileObstacleCustomData


@dataclass
class FSBeatMapFile:
    version: str
    customData: FSBeatMapFileCustomData
    events: list
    notes: list
    obstacles: list
    waypoints: list

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
                    color=tuple(obstacle['_customData']['_color']),
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
