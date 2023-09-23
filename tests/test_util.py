from __future__ import annotations

import os
import subprocess
import zipfile
from datetime import datetime

import pytest

from util import create_valid_filename
from util import get_ogg_and_duration
from util import get_song_cover_path


@pytest.mark.parametrize(
    'file_names, expected_output', [
        # Both .ogg and clip1.ogg exists
        (['file1.ogg', 'file2.clip1.ogg'], ('file2.clip1.ogg', '10')),
        (['file1.ogg'], (None, None)),  # Only .ogg exists, no clip1.ogg
        ([], (None, None)),  # No files
    ],
)
def test_get_ogg_and_duration(file_names, expected_output, tmpdir, mocker):
    folder_path = tmpdir.mkdir('audio_files')
    for file_name in file_names:
        folder_path.join(file_name).write('fake_audio_data')

    mocker.patch('subprocess.check_output', return_value='10')

    ogg_file, duration_str = get_ogg_and_duration(str(folder_path))

    if ogg_file:
        ogg_file = os.path.basename(ogg_file)

    assert (ogg_file, duration_str) == expected_output


def test_get_ogg_and_duration_subprocess_error(tmpdir, mocker):
    folder_path = tmpdir.mkdir('audio_files')
    folder_path.join('file.clip1.ogg').write('fake_audio_data')

    mocker.patch(
        'subprocess.check_output',
        side_effect=subprocess.CalledProcessError(1, 'cmd'),
    )

    ogg_file, duration_str = get_ogg_and_duration(str(folder_path))

    assert (ogg_file, duration_str) == (None, None)


@pytest.mark.parametrize(
    'file_names, expected_output', [
        (
            ['jk_song1_b.png', 'jk_song2_b.png'],
            'jk_song1_b.png',
        ),  # Multiple matching files
        (['jk_song1_b.png'], 'jk_song1_b.png'),  # Single matching file
        (['song1_b.png', 'jk_song1.png'], None),  # No matching files
        ([], None),  # Empty folder
    ],
)
def test_get_song_cover_path(file_names, expected_output, tmpdir):
    folder_path = tmpdir.mkdir('cover_files')
    for file_name in file_names:
        folder_path.join(file_name).write('fake_image_data')

    cover_file = get_song_cover_path(str(folder_path))

    if cover_file:
        cover_file = os.path.basename(cover_file)

    assert cover_file == expected_output


@pytest.mark.parametrize(
    'input_string, expected_output', [
        # Special characters should be removed
        ('file$name1.txt', 'filename1txt'),
        # Spaces should remain, trailing spaces should be removed
        ('  file name  ', '  file name'),
        # Slash should be preserved as it's in valid_chars
        ('file/name', 'filename'),
        # File name should be truncated to 255 characters
        ('long' * 80, 'long' * 63 + 'lon'),
    ],
)
def test_create_valid_filename(input_string, expected_output):
    result = create_valid_filename(input_string)
    assert result == expected_output


def datetime_to_ticks(dt):
    epoch = datetime(1, 1, 1)
    dt_delta = dt - epoch
    ticks = dt_delta.total_seconds() * 10 ** 7
    return int(ticks)


def yyyymmdd_to_ticks(date_str: str):
    dt = datetime.strptime(date_str, '%Y%m%d')
    return datetime_to_ticks(dt)


def zipdir(path, ziph, archiveroot):
    for root, dirs, files in os.walk(path):
        for file in files:
            actual_file_path = os.path.join(root, file)
            archive_file_path = os.path.join(
                archiveroot, os.path.relpath(actual_file_path, path),
            )
            ziph.write(actual_file_path, archive_file_path)


@pytest.mark.parametrize(
    'input_datetime, expected_ticks', [
        (datetime(1, 1, 1), 0),
        (datetime(1970, 1, 1), 621355968000000000),
    ],
)
def test_datetime_to_ticks(input_datetime, expected_ticks):
    assert datetime_to_ticks(input_datetime) == expected_ticks


@pytest.mark.parametrize(
    'input_date_str, expected_ticks', [
        ('00010101', 0),
        ('19700101', 621355968000000000),
    ],
)
def test_yyyymmdd_to_ticks(input_date_str, expected_ticks):
    assert yyyymmdd_to_ticks(input_date_str) == expected_ticks


def test_zipdir(tmp_path):
    test_folder = tmp_path / 'test_folder'
    test_folder.mkdir()
    test_file = test_folder / 'test_file.txt'
    test_file.write_text('Hello, world!')

    zip_path = tmp_path / 'test_folder.zip'
    with zipfile.ZipFile(zip_path, 'w') as ziph:
        zipdir(test_folder, ziph, 'archive_root')

    with zipfile.ZipFile(zip_path, 'r') as ziph:
        with ziph.open('archive_root/test_file.txt') as f:
            assert f.read().decode() == 'Hello, world!'
