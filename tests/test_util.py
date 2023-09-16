from __future__ import annotations

import os
from unittest.mock import Mock

import numpy as np
import pytest

from util import crop_frame
from util import get_song_metadata_remote
from util import L_TEMPLATE
from util import map_position_to_dd_x
from util import match_template
from util import R_TEMPLATE


@pytest.mark.parametrize(
    'image, template, threshold, expected_result',
    [
        (
            np.array(L_TEMPLATE),
            np.array(L_TEMPLATE),
            0.8,
            (0, 0, 60, 30),
        ),
        (
            np.array(L_TEMPLATE),
            np.array(R_TEMPLATE),
            0.8,
            None,
        ),
    ],
)
def test_match_template(image, template, threshold, expected_result):
    result = match_template(image, template, threshold)
    assert result == expected_result


@pytest.mark.parametrize(
    'input_number, expected_output', [
        (30, 1),  # Below minimum
        (31, 1),  # Minimum value
        (100, 2),  # Somewhere in between
        (155, 3),  # Somewhere in between
        (522, 9),  # Maximum value
        (523, 9),  # Above maximum
    ],
)
def test_map_position_to_dd_x(input_number, expected_output):
    result = map_position_to_dd_x(input_number)
    assert result == expected_output


def test_get_song_metadata_remote_remote_data(mocker):
    mocker.patch.dict(os.environ, {'REMOTE_DATA': 'True'})
    mock_requests_get = mocker.patch('requests.get')

    response_mock = Mock()
    response_mock.json.return_value = _SAMPLE_DRS_JSON_DATA
    mock_requests_get.return_value = response_mock

    result = get_song_metadata_remote('1')

    assert result is not None
    assert result.songId == '1'
    assert result.title == 'Song 1'


_SAMPLE_DRS_JSON_DATA = {
    'songs': [
        {
            'songId': '1',
            'title': 'Song 1',
            'category': 'Category 1',
            'artist': 'Artist 1',
            'bpm': 120,
            'imageName': 'song1.jpg',
        },
        {
            'songId': '2',
            'title': 'Song 2',
            'category': 'Category 2',
            'artist': 'Artist 2',
            'bpm': 140,
            'imageName': 'song2.jpg',
        },
    ],
}


def test_get_song_metadata_remote_local_data(mocker):
    mocker.patch.dict(os.environ, {'REMOTE_DATA': 'False'})

    result = get_song_metadata_remote('50th Memorial Songs -Beginning Story-')

    assert result is not None
    assert result.songId == '50th Memorial Songs -Beginning Story-'
    assert result.title == '50th Memorial Songs -Beginning Story-'


def test_get_song_metadata_remote_song_id_none(mocker):
    mocker.patch.dict(os.environ, {'REMOTE_DATA': 'False'})

    result = get_song_metadata_remote('does not exist')

    assert result is None


_TEST_FRAME = np.array(
    [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20],
        [21, 22, 23, 24, 25],
    ],
)


@pytest.mark.parametrize(
    'x, y, width, height, expected_result', [
        (
            1, 1, 3, 3, np.array(
                [
                    [7, 8, 9],
                    [12, 13, 14],
                    [17, 18, 19],
                ],
            ),
        ),
        (
            0, 0, 2, 2, np.array(
                [
                    [1, 2],
                    [6, 7],
                ],
            ),
        ),
        (
            2, 2, 2, 2, np.array(
                [
                    [13, 14],
                    [18, 19],
                ],
            ),
        ),
        (
            3, 3, 3, 3, np.array(
                [
                    [19, 20],
                    [24, 25],
                ],
            ),
        ),
    ],
)
def test_crop_frame(x, y, width, height, expected_result):
    result = crop_frame(_TEST_FRAME, x, y, width, height)
    np.testing.assert_array_equal(result, expected_result)


def test_find_l():
    assert True  # todo


def test_find_r():
    assert True  # todo


def test_find_stage():
    assert True  # todo
