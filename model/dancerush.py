from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

import xmltodict

MIN_POS = 0
MAX_POS = 65536

DRS_LEFT = 1
DRS_RIGHT = 2
DRS_DOWN = 3
DRS_JUMP = 4

DRS_ALBUM_ID = 2022121400
ALBUM_NAME = f'DANCERUSH STARDOM ({DRS_ALBUM_ID})'
DEFAULT_TRACK_DIR = f'tracks/{ALBUM_NAME}/'
OUTPUT_ZIP_NAME = 'DANCERUSH_STARDOM.zip'


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

    @property
    def ogg(self) -> str:
        return f'{str(self.song_id)}.ogg'

    @property
    def png(self) -> str:
        return f'{str(self.song_id)}.png'

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
    tick: int | None = None
    time: int | None = None
    delta_time: int | None = None


@dataclass
class DRSTrackMeasureInfo:
    denomi: int
    num: int
    tick: int | None = None
    time: int | None = None
    delta_time: int | None = None


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
            drs_track_measure_info = []
            for measure in data['measure_info']['measure']:
                has_tick = 'tick' in measure
                has_time = 'time' in measure
                has_delta_time = 'delta_time' in measure
                measure_info = DRSTrackMeasureInfo(
                    int(measure['denomi']['#text']),
                    int(measure['num']['#text']),
                    int(measure['tick']['#text']) if has_tick else None,
                    int(measure['time']['#text']) if has_time else None,
                    int(
                        measure['delta_time']['#text'],
                    ) if has_delta_time else None,
                )
                drs_track_measure_info.append(measure_info)
        else:
            has_tick = 'tick' in data['measure_info']['measure']
            has_time = 'time' in data['measure_info']['measure']
            has_delta_time = 'delta_time' in data['measure_info']['measure']
            drs_track_measure_info = [
                DRSTrackMeasureInfo(
                    int(data['measure_info']['measure']['denomi']['#text']),
                    int(data['measure_info']['measure']['num']['#text']),
                    int(
                        data['measure_info']['measure']['tick']
                        ['#text'],
                    ) if has_tick else None,
                    int(
                        data['measure_info']['measure']['time']
                        ['#text'],
                    ) if has_time else None,
                    int(
                        data['measure_info']['measure']['delta_time']
                        ['#text'],
                    ) if has_delta_time else None,
                ),
            ]

        if type(data['bpm_info']['bpm']) is list:
            drs_track_bpm_info = []
            for bpm in data['bpm_info']['bpm']:
                has_tick = 'tick' in bpm
                has_time = 'time' in bpm
                has_delta_time = 'delta_time' in bpm
                bmp_info = DRSTrackBPMInfo(
                    int(bpm['bpm']['#text']),
                    int(bpm['tick']['#text']) if has_tick else None,
                    int(bpm['time']['#text']) if has_time else None,
                    int(
                        bpm['delta_time']['#text'],
                    ) if has_delta_time else None,
                )
                drs_track_bpm_info.append(bmp_info)
        else:
            has_tick = 'tick' in data['bpm_info']['bpm']
            has_time = 'time' in data['bpm_info']['bpm']
            has_delta_time = 'delta_time' in data['bpm_info']['bpm']
            drs_track_bpm_info = [
                DRSTrackBPMInfo(
                    int(data['bpm_info']['bpm']['bpm']['#text']),
                    int(
                        data['bpm_info']['bpm']['tick']
                        ['#text'],
                    ) if has_tick else None,
                    int(
                        data['bpm_info']['bpm']['time']
                        ['#text'],
                    ) if has_time else None,
                    int(
                        data['bpm_info']['bpm']['delta_time']
                        ['#text'],
                    ) if has_delta_time else None,
                ),
            ]

        if 'time_unit' in data:
            time_unit = int(data['time_unit']['#text'])
        elif 'tick' in data:
            time_unit = int(data['tick']['#text'])
        else:
            time_unit = 480

        return cls(
            end_tick=int(
                data['end_tick']['#text'],
            ) if 'end_tick' in data else None,
            time_unit=DRSTrackTimeInfo(time_unit),
            bpm_info=drs_track_bpm_info,
            measure_info=drs_track_measure_info,
        )

    @classmethod
    def from_json_dict(cls, data: dict):

        return cls(
            end_tick=int(data['end_tick']) if data.get(
                'end_tick',
            ) is not None else None,
            time_unit=DRSTrackTimeInfo(int(data['time_unit']['time_unit'])),
            bpm_info=[
                DRSTrackBPMInfo(
                    bpm=int(bpm['bpm']) if bpm.get(
                        'bpm',
                    ) is not None else None,
                    tick=int(bpm['tick']) if bpm.get(
                        'tick',
                    ) is not None else None,
                ) for bpm in data['bpm_info']
            ],
            measure_info=[
                DRSTrackMeasureInfo(
                    denomi=int(measure['denomi']),
                    num=int(measure['num']),
                    tick=int(measure['tick']) if measure.get(
                        'tick',
                    ) is not None else None,
                ) for measure in data['measure_info']
            ],
        )


@dataclass
class DRSTrackStepTickInfo:
    start_tick: int | None = None
    end_tick: int | None = None
    stime_ms: int | None = None
    etime_ms: int | None = None
    stime_dt: int | None = None
    etime_dt: int | None = None


@dataclass
class DRSTrackStepPositionInfo:
    left_pos: int
    right_pos: int

    @property
    def to_dance_dash_x(self):
        center_pos = (self.left_pos + self.right_pos) / 2
        mapped_value = 1 + (center_pos / MAX_POS) * 8
        return round(mapped_value)


@dataclass
class DRSTrackPoint(DRSTrackStepPositionInfo):
    tick: int
    left_end_pos: int | None = None
    right_end_pos: int | None = None
    point_time: int | None = None

    @property
    def to_dance_dash_end_x(self):
        center_pos = (self.left_end_pos + self.right_end_pos) / 2
        mapped_value = 1 + (center_pos / MAX_POS) * 8
        return round(mapped_value)

    @property
    def tail(self):
        end_x = self.to_dance_dash_end_x
        if end_x in range(2, 9):
            return end_x + (end_x - self.to_dance_dash_x)
        return end_x


@dataclass
class DRSTrackStepPlayerInfo:
    player_id: int


@dataclass
class DRSTrackStep:
    tick_info: DRSTrackStepTickInfo
    kind: DRS_LEFT | DRS_RIGHT | DRS_DOWN | DRS_JUMP
    position_info: DRSTrackStepPositionInfo
    player_info: DRSTrackStepPlayerInfo
    long_point: list[DRSTrackPoint] = field(default_factory=list)

    @property
    def is_down_or_up(self):
        return self.kind in (DRS_DOWN, DRS_JUMP)

    @classmethod
    def from_xml_dict(cls, data: dict):

        points = []
        if long_point := data.get('long_point'):
            if points := long_point.get('point'):
                if not isinstance(points, list):
                    points = [points]

        has_start_tick = 'start_tick' in data
        has_end_tick = 'end_tick' in data

        has_stime_ms = 'stime_ms' in data
        has_etime_ms = 'etime_ms' in data
        has_stime_dt = 'stime_dt' in data
        has_etime_dt = 'etime_dt' in data

        main_left_pos = int(data['left_pos']['#text']) if 'left_pos' in data else int(
            data['pos_left']['#text'],
        )
        main_right_pos = int(data['right_pos']['#text']) if 'right_pos' in data else int(
            data['pos_right']['#text'],
        )

        track_points = []
        for point in points:
            if 'left_pos' in point:
                left_pos = safe_int(point['left_pos']['#text'])
            elif 'pos_left' in point:
                left_pos = safe_int(point['pos_left']['#text'])

            if 'right_pos' in point:
                right_pos = safe_int(point['right_pos']['#text'])
            elif 'pos_right' in point:
                right_pos = safe_int(point['pos_right']['#text'])

            left_end_pos = None
            if 'left_end_pos' in point:
                left_end_pos = safe_int(point['left_end_pos']['#text'])
            elif 'pos_lend' in point:
                left_end_pos = safe_int(point['pos_lend']['#text'])

            right_end_pos = None
            if 'right_end_pos' in point:
                right_end_pos = safe_int(point['right_end_pos']['#text'])
            elif 'pos_rend' in point:
                right_end_pos = safe_int(point['pos_rend']['#text'])

            drs_track_point = DRSTrackPoint(
                tick=safe_int(point.get('tick', {}).get('#text')),
                left_pos=left_pos,
                right_pos=right_pos,
                left_end_pos=left_end_pos,
                right_end_pos=right_end_pos,
                point_time=safe_int(
                    point.get('point_time', {}).get('#text'),
                ),
            )
            track_points.append(drs_track_point)

        return cls(
            DRSTrackStepTickInfo(
                start_tick=int(
                    data['start_tick']['#text'],
                ) if has_start_tick else None,
                end_tick=int(
                    data['end_tick']['#text'],
                ) if has_end_tick else None,
                stime_ms=int(
                    data['stime_ms']['#text'],
                ) if has_stime_ms else None,
                etime_ms=int(
                    data['etime_ms']['#text'],
                ) if has_etime_ms else None,
                stime_dt=int(
                    data['stime_dt']['#text'],
                ) if has_stime_dt else None,
                etime_dt=int(
                    data['etime_dt']['#text'],
                ) if has_etime_dt else None,
            ),
            int(data['kind']['#text']),
            DRSTrackStepPositionInfo(
                left_pos=main_left_pos,
                right_pos=main_right_pos,
            ),
            DRSTrackStepPlayerInfo(int(data['player_id']['#text'])),
            track_points,
        )

    @classmethod
    def from_json_dict(cls, data: dict):

        track_points = []
        for point in data['long_point']:
            if 'left_pos' in point:
                left_pos = safe_int(point['left_pos'])
            elif 'pos_left' in point:
                left_pos = safe_int(point['pos_left'])
            if 'right_pos' in point:
                right_pos = safe_int(point['right_pos'])
            elif 'pos_right' in point:
                right_pos = safe_int(point['pos_right'])

            track_point = DRSTrackPoint(
                tick=safe_int(point['tick']),
                left_pos=left_pos,
                right_pos=right_pos,
                left_end_pos=int(point['left_end_pos']) if point.get(
                    'left_end_pos',
                ) is not None else None,
                right_end_pos=int(point['right_end_pos']) if point.get(
                    'right_end_pos',
                ) is not None else None,
                point_time=safe_int(point['point_time']),
            )
            track_points.append(track_point)

        return cls(
            DRSTrackStepTickInfo(
                start_tick=int(data['tick_info']['start_tick']) if data['tick_info'].get(
                    'start_tick',
                ) is not None else None,
                end_tick=int(data['tick_info']['end_tick']) if data['tick_info'].get(
                    'end_tick',
                ) is not None else None,
                stime_ms=int(data['tick_info']['stime_ms']) if data['tick_info'].get(
                    'stime_ms',
                ) is not None else None,
                etime_ms=int(data['tick_info']['etime_ms']) if data['tick_info'].get(
                    'etime_ms',
                ) is not None else None,
                stime_dt=int(data['tick_info']['stime_dt']) if data['tick_info'].get(
                    'stime_dt',
                ) is not None else None,
                etime_dt=int(data['tick_info']['etime_dt']) if data['tick_info'].get(
                    'etime_dt',
                ) is not None else None,
            ),
            int(data['kind']),
            DRSTrackStepPositionInfo(
                int(data['position_info']['left_pos']),
                int(data['position_info']['right_pos']),
            ),
            DRSTrackStepPlayerInfo(int(data['player_info']['player_id'])),
            track_points,
        )


@dataclass
class DRSClip:
    start_time: int
    end_time: int

    @classmethod
    def from_xml_dict(cls, data: dict):
        start_time = None
        if 'start_time' in data:
            start_time = int(data['start_time']['#text'])
        elif 'stime_ms' in data:
            start_time = int(data['stime_ms']['#text'])

        end_time = None
        if 'end_time' in data:
            end_time = int(data['end_time']['#text'])
        elif 'etime_ms' in data:
            end_time = int(data['etime_ms']['#text'])

        return cls(start_time, end_time)

    @classmethod
    def from_json_dict(cls, data: dict):
        return cls(
            int(data['start_time']),
            int(data['end_time']),
        )


@dataclass
class DRSTrack:
    seq_version: int
    info: DRSTrackInfo
    sequence_data: list[DRSTrackStep] = field(default_factory=list)
    clip: DRSClip = None

    @classmethod
    def from_xml_dict(cls, data: dict):
        data = data['data']

        # not really representing the data properly, but we need this for timings on 9 songs (i think)
        clip = None
        if 'rec_data' in data and data['rec_data'] and type(data['rec_data']['clip']) is not list:
            clip = DRSClip.from_xml_dict(data['rec_data']['clip'])

        return cls(
            int(data['seq_version']['#text']),
            DRSTrackInfo.from_xml_dict(data['info']),
            [
                DRSTrackStep.from_xml_dict(step)
                for step in data['sequence_data']['step']
            ],
            clip,
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
            clip=DRSClip.from_json_dict(data['clip']) if data.get(
                'clip',
            ) is not None else None,
        )


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
