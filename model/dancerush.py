from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

import xmltodict


@dataclass
class DRSSheetDataZetaraku:
    type: str
    difficulty: str
    level: str
    levelValue: int


@dataclass
class DRSSongDataZetaraku:
    songId: str
    category: str
    title: str
    artist: str
    bpm: int
    imageName: str
    version: str | None = None
    releaseDate: str | None = None
    isNew: bool | None = None
    isLocked: bool = False
    sheets: list[DRSSheetDataZetaraku] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data_dict):
        sheets_data = data_dict.get('sheets') or []
        sheets = [DRSSheetDataZetaraku(**sheet) for sheet in sheets_data]
        return cls(**{**data_dict, 'sheets': sheets})


@dataclass
class DRSSongInfo:
    artist_name: str
    artist_yomigana: str
    genre: int
    title_name: str
    title_yomigana: str
    bpm_max: int
    bpm_min: int
    distribution_date: int
    license: str
    region: str
    volume: int


@dataclass
class DRSSongDifficulty:
    track: DRSTrack
    difnum: int | None = None


@dataclass
class DRSSongDifficulties:
    difficulty_1a: DRSSongDifficulty | None = None
    difficulty_1b: DRSSongDifficulty | None = None
    difficulty_2a: DRSSongDifficulty | None = None
    difficulty_2b: DRSSongDifficulty | None = None


@dataclass
class DRSSongData:
    song_id: int
    difficulties: DRSSongDifficulties | None = None
    info: DRSSongInfo | None = None

    @classmethod
    def from_dict(cls, data: dict, difficulties: DRSSongDifficulties) -> DRSSongData:
        return cls(
            song_id=int(data['@id']),
            difficulties=difficulties,
            info=DRSSongInfo(
                artist_name=data['info']['artist_name'].get('#text'),
                artist_yomigana=data['info']['artist_yomigana'].get('#text'),
                genre=int(data['info']['genre']['#text']),
                title_name=data['info']['title_name']['#text'],
                title_yomigana=data['info']['title_yomigana']['#text'],
                bpm_max=int(data['info']['bpm_max']['#text']),
                bpm_min=int(data['info']['bpm_min']['#text']),
                distribution_date=int(
                    data['info']['distribution_date']['#text'],
                ),
                license=data['info']['license'].get('#text'),
                region=data['info']['region']['#text'],
                volume=int(data['info']['volume']['#text']),
            ),
        )


@dataclass
class DRSTrackBPMInfo:
    bpm: int
    tick: int


@dataclass
class DRSTrackMeasureInfo:
    denomi: int
    num: int
    tick: int


@dataclass
class DRSTrackTimeInfo:
    time_unit: int


@dataclass
class DRSTrackInfo:
    end_tick: int
    time_unit: DRSTrackTimeInfo
    bpm_info: list[DRSTrackBPMInfo] = field(default_factory=list)
    measure_info: list[DRSTrackMeasureInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        if type(data['measure_info']['measure']) is list:
            drs_track_measure_info = [
                DRSTrackMeasureInfo(
                    int(measure['denomi']['#text']),
                    int(measure['num']['#text']),
                    int(measure['tick']['#text']),
                ) for measure in data['measure_info']['measure']
            ]
        else:
            drs_track_measure_info = [
                DRSTrackMeasureInfo(
                    int(data['measure_info']['measure']['denomi']['#text']),
                    int(data['measure_info']['measure']['num']['#text']),
                    int(data['measure_info']['measure']['tick']['#text']),
                ),
            ]

        if type(data['bpm_info']['bpm']) is list:
            drs_track_bpm_info = [
                DRSTrackBPMInfo(
                    int(bpm['bpm']['#text']),
                    int(bpm['tick']['#text']),
                ) for bpm in data['bpm_info']['bpm']
            ]
        else:
            drs_track_bpm_info = [
                DRSTrackBPMInfo(
                    int(data['bpm_info']['bpm']['bpm']['#text']),
                    int(data['bpm_info']['bpm']['tick']['#text']),
                ),
            ]

        return cls(
            end_tick=int(data['end_tick']['#text']),
            time_unit=DRSTrackTimeInfo(int(data['time_unit']['#text'])),
            bpm_info=drs_track_bpm_info,
            measure_info=drs_track_measure_info,
        )


@dataclass
class DRSTrackStepTickInfo:
    start_tick: int
    end_tick: int


@dataclass
class DRSTrackStepPositionInfo:
    left_pos: int
    right_pos: int


@dataclass
class DRSTrackStepPlayerInfo:
    player_id: int


@dataclass
class DRSTrackStep:
    tick_info: DRSTrackStepTickInfo
    kind: int
    position_info: DRSTrackStepPositionInfo
    long_point: bool | None
    player_info: DRSTrackStepPlayerInfo

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            DRSTrackStepTickInfo(
                int(data['start_tick']['#text']), int(
                    data['end_tick']['#text'],
                ),
            ),
            int(data['kind']['#text']),
            DRSTrackStepPositionInfo(
                int(data['left_pos']['#text']), int(
                    data['right_pos']['#text'],
                ),
            ),
            bool(data.get('long_point')),  # Optional field
            DRSTrackStepPlayerInfo(int(data['player_id']['#text'])),
        )


@dataclass
class DRSTrack:
    seq_version: int
    info: DRSTrackInfo
    sequence_data: list[DRSTrackStep] = field(default_factory=list)
    extend_data = None  # TODO: Implement this ???
    rec_data = None  # TODO: Implement this ???

    @classmethod
    def from_dict(cls, data: dict):
        data = data['data']
        return cls(
            int(data['seq_version']['#text']),
            DRSTrackInfo.from_dict(data['info']),
            [
                DRSTrackStep.from_dict(step)
                for step in data['sequence_data']['step']
            ],
        )

    @classmethod
    def from_xml(cls, path: str):
        data = open(path, encoding='utf-8').read()
        return cls.from_dict(xmltodict.parse(data))
