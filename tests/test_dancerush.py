from __future__ import annotations

import pytest

from model.dancerush import DRSTrackStepPositionInfo
from model.dancerush import MAX_POS
from model.dancerush import MIN_POS
from model.dancerush import safe_int


@pytest.mark.parametrize(
    'input_value, expected_output', [
        ('42', 42),
        ('0', 0),
        ('-100', -100),
        (None, None),
        ('abc', None),
        ([1, 2, 3], None),
    ],
)
def test_safe_int(input_value, expected_output):
    assert safe_int(input_value) == expected_output


@pytest.mark.parametrize(
    'input_values, expected_output', [
        ((MIN_POS, MIN_POS), 1),
        ((MAX_POS/2, MAX_POS/2), 5),
        ((MAX_POS, MAX_POS), 9),
    ],
)
def test_DRSTrackStepPositionInfo_to_dance_dance_x(input_values, expected_output):
    left_pos, right_pos = input_values
    track_info = DRSTrackStepPositionInfo(left_pos, right_pos)
    assert track_info.to_dance_dash_x == expected_output
