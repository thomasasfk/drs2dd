from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

import xmltodict


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


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

    @property
    def with_attrs_as_str(self) -> dict[str, DRSSongDifficulty]:
        return {
            'difficulty_1a': self.difficulty_1a,
            'difficulty_1b': self.difficulty_1b,
            'difficulty_2a': self.difficulty_2a,
            'difficulty_2b': self.difficulty_2b,
        }


@dataclass
class DRSSongData:
    song_id: int
    difficulties: DRSSongDifficulties | None = None
    info: DRSSongInfo | None = None

    @classmethod
    def from_xml_dict(cls, data: dict, difficulties: DRSSongDifficulties) -> DRSSongData:
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

    @classmethod
    def from_json_dict(cls, data: dict):
        difficulties = data['difficulties']
        info = data['info']
        return cls(
            song_id=int(data['song_id']),
            difficulties=DRSSongDifficulties(
                difficulty_1a=DRSSongDifficulty(
                    track=DRSTrack.from_json_dict(
                        difficulties['difficulty_1a']['track'],
                    ),
                    difnum=difficulties['difficulty_1a']['difnum'],
                ) if difficulties['difficulty_1a'] else None,
                difficulty_1b=DRSSongDifficulty(
                    track=DRSTrack.from_json_dict(
                        difficulties['difficulty_1b']['track'],
                    ),
                    difnum=difficulties['difficulty_1b']['difnum'],
                ) if difficulties['difficulty_1b'] else None,
                difficulty_2a=DRSSongDifficulty(
                    track=DRSTrack.from_json_dict(
                        difficulties['difficulty_2a']['track'],
                    ),
                    difnum=difficulties['difficulty_2a']['difnum'],
                ) if difficulties['difficulty_2a'] else None,
                difficulty_2b=DRSSongDifficulty(
                    track=DRSTrack.from_json_dict(
                        difficulties['difficulty_2b']['track'],
                    ),
                    difnum=difficulties['difficulty_2b']['difnum'],
                ) if difficulties['difficulty_2b'] else None,
            ),
            info=DRSSongInfo(
                artist_name=info['artist_name'],
                artist_yomigana=info['artist_yomigana'],
                genre=info['genre'],
                title_name=info['title_name'],
                title_yomigana=info['title_yomigana'],
                bpm_max=info['bpm_max'],
                bpm_min=info['bpm_min'],
                distribution_date=info['distribution_date'],
                license=info['license'],
                region=info['region'],
                volume=info['volume'],
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
    def from_xml_dict(cls, data: dict):
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

    @classmethod
    def from_json_dict(cls, data: dict):
        return cls(
            end_tick=int(data['end_tick']),
            time_unit=DRSTrackTimeInfo(int(data['time_unit']['time_unit'])),
            bpm_info=[
                DRSTrackBPMInfo(
                    bpm=int(bpm['bpm']),
                    tick=int(bpm['tick']),
                ) for bpm in data['bpm_info']
            ],
            measure_info=[
                DRSTrackMeasureInfo(
                    denomi=int(measure['denomi']),
                    num=int(measure['num']),
                    tick=int(measure['tick']),
                ) for measure in data['measure_info']
            ],
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
class DRSTrackPoint:
    tick: int
    left_pos: int
    right_pos: int
    left_end_pos: int
    right_end_pos: int


@dataclass
class DRSTrackStepPlayerInfo:
    player_id: int


DRS_LEFT = 1
DRS_RIGHT = 2
DRS_DOWN = 3


@dataclass
class DRSTrackStep:
    tick_info: DRSTrackStepTickInfo
    kind: DRS_LEFT | DRS_RIGHT | DRS_DOWN
    position_info: DRSTrackStepPositionInfo
    player_info: DRSTrackStepPlayerInfo
    long_point: list[DRSTrackPoint] = field(default_factory=list)

    @classmethod
    def from_xml_dict(cls, data: dict):

        points = []
        if long_point := data.get('long_point'):
            if points := long_point.get('point'):
                if not isinstance(points, list):
                    points = [points]

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
            DRSTrackStepPlayerInfo(int(data['player_id']['#text'])),
            [
                DRSTrackPoint(
                    tick=safe_int(point.get('tick', {}).get('#text')),
                    left_pos=safe_int(point.get('left_pos', {}).get('#text')),
                    right_pos=safe_int(
                        point.get('right_pos', {}).get('#text'),
                    ),
                    left_end_pos=safe_int(
                        point.get('left_end_pos', {}).get('#text'),
                    ),
                    right_end_pos=safe_int(
                        point.get('right_end_pos', {}).get('#text'),
                    ),
                ) for point in points
            ],
        )

    @classmethod
    def from_json_dict(cls, data: dict):
        return cls(
            DRSTrackStepTickInfo(
                int(data['tick_info']['start_tick']),
                int(data['tick_info']['end_tick']),
            ),
            int(data['kind']),
            DRSTrackStepPositionInfo(
                int(data['position_info']['left_pos']),
                int(data['position_info']['right_pos']),
            ),
            DRSTrackStepPlayerInfo(int(data['player_info']['player_id'])),
            [
                DRSTrackPoint(
                    tick=int(point['tick']) if point.get('tick') else None,
                    left_pos=int(point['left_pos']) if point.get(
                        'left_pos',
                    ) else None,
                    right_pos=int(point['right_pos']) if point.get(
                        'right_pos',
                    ) else None,
                    left_end_pos=int(point['left_end_pos']) if point.get(
                        'left_end_pos',
                    ) else None,
                    right_end_pos=int(point['right_end_pos']) if point.get(
                        'right_end_pos',
                    ) else None,
                ) for point in data['long_point']
            ],
        )


@dataclass
class DRSTrack:
    seq_version: int
    info: DRSTrackInfo
    sequence_data: list[DRSTrackStep] = field(default_factory=list)
    extend_data = None  # TODO: Implement this ???
    rec_data = None  # TODO: Implement this ???

    @classmethod
    def from_xml_dict(cls, data: dict):
        data = data['data']
        return cls(
            int(data['seq_version']['#text']),
            DRSTrackInfo.from_xml_dict(data['info']),
            [
                DRSTrackStep.from_xml_dict(step)
                for step in data['sequence_data']['step']
            ],
        )

    @classmethod
    def from_xml(cls, path: str):
        data = open(path, encoding='utf-8').read()
        return cls.from_xml_dict(xmltodict.parse(data))

    @classmethod
    def from_json_dict(cls, data: dict):
        return cls(
            int(data['seq_version']),
            DRSTrackInfo.from_json_dict(data['info']),
            [
                DRSTrackStep.from_json_dict(step)
                for step in data['sequence_data']
            ],
        )
