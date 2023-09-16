from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class DRSSheetData:
    type: str
    difficulty: str
    level: str
    levelValue: int


@dataclass
class DRSSongData:
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
    sheets: list[DRSSheetData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data_dict):
        sheets_data = data_dict.get('sheets') or []
        sheets = [DRSSheetData(**sheet) for sheet in sheets_data]
        return cls(**{**data_dict, 'sheets': sheets})
