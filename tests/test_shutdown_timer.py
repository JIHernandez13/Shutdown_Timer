"""Tests for the pure helpers in :mod:`shutdown_timer`."""

import pytest

from shutdown_timer import (
    MAX_DELAY_SECONDS,
    abort_args,
    format_hms,
    parse_delay,
    shutdown_args,
)


@pytest.mark.parametrize(
    ("hours", "minutes", "expected"),
    [
        ("0", "1", 60),
        ("", "30", 1800),
        ("1", "", 3600),
        ("1", "30", 5400),
        ("2", "0", 7200),
        (" 1 ", " 5 ", 3900),
    ],
)
def test_parse_delay_valid(hours: str, minutes: str, expected: int) -> None:
    assert parse_delay(hours, minutes) == expected


@pytest.mark.parametrize(
    ("hours", "minutes", "message"),
    [
        ("0", "0", "at least one minute"),
        ("", "", "at least one minute"),
        ("0", "0.5", "whole numbers"),
        ("abc", "0", "whole numbers"),
        ("-1", "0", "negative"),
        ("0", "-5", "negative"),
        ("100000", "0", "too large"),
    ],
)
def test_parse_delay_invalid(hours: str, minutes: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_delay(hours, minutes)


def test_parse_delay_upper_bound_is_inclusive() -> None:
    hours = MAX_DELAY_SECONDS // 3600
    assert parse_delay(str(hours), "0") == hours * 3600
    with pytest.raises(ValueError, match="too large"):
        parse_delay(str(hours + 1), "0")


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "00:00"),
        (5, "00:05"),
        (65, "01:05"),
        (3600, "1:00:00"),
        (3661, "1:01:01"),
        (-10, "00:00"),
    ],
)
def test_format_hms(seconds: int, expected: str) -> None:
    assert format_hms(seconds) == expected


def test_shutdown_args() -> None:
    assert shutdown_args(90) == ["shutdown", "/s", "/t", "90"]


def test_abort_args() -> None:
    assert abort_args() == ["shutdown", "/a"]
