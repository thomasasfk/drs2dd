from __future__ import annotations

import pytest

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
