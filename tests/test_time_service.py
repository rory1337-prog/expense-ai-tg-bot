from datetime import UTC, datetime
from unittest.mock import patch

from services.time_service import TimeService


def test_today_bounds_are_converted_from_warsaw_to_utc():
    local_now = datetime.fromisoformat("2026-07-17T12:00:00+02:00")

    with patch.object(TimeService, "local_now", return_value=local_now):
        bounds = TimeService.get_period_bounds("today")

    assert bounds is not None
    start, end = bounds

    assert start == datetime(2026, 7, 16, 22, 0)
    assert end == datetime(2026, 7, 17, 22, 0)


def test_month_bounds_cross_year_boundary():
    local_now = datetime.fromisoformat("2026-12-15T12:00:00+01:00")

    with patch.object(TimeService, "local_now", return_value=local_now):
        bounds = TimeService.get_period_bounds("month")

    assert bounds is not None
    start, end = bounds

    assert start == datetime(2026, 11, 30, 23, 0)
    assert end == datetime(2026, 12, 31, 23, 0)


def test_february_leap_year_bounds():
    local_now = datetime.fromisoformat("2028-02-15T12:00:00+01:00")

    with patch.object(TimeService, "local_now", return_value=local_now):
        bounds = TimeService.get_period_bounds("month")

    assert bounds is not None
    start, end = bounds

    assert start == datetime(2028, 1, 31, 23, 0)
    assert end == datetime(2028, 2, 29, 23, 0)


def test_dst_month_boundary_uses_correct_utc_offsets():
    local_now = datetime.fromisoformat("2026-03-30T12:00:00+02:00")

    with patch.object(TimeService, "local_now", return_value=local_now):
        bounds = TimeService.get_period_bounds("month")

    assert bounds is not None
    start, end = bounds

    assert start == datetime(2026, 2, 28, 23, 0)
    assert end == datetime(2026, 3, 31, 22, 0)


def test_utc_now_naive_returns_naive_datetime():
    result = TimeService.utc_now_naive()

    assert result.tzinfo is None


def test_to_utc_naive_converts_aware_datetime():
    value = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)

    result = TimeService.to_utc_naive(value)

    assert result == datetime(2026, 7, 17, 12, 0)
    assert result.tzinfo is None


def test_invalid_period_returns_none():
    assert TimeService.get_period_bounds("year") is None
