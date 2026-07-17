from datetime import datetime
from unittest.mock import patch

import pytest

from services.analytics_service import AnalyticsService


def test_average_daily_spending_today():
    with patch.object(
        AnalyticsService,
        "get_total_spending",
        return_value=120,
    ):
        result = AnalyticsService.get_average_daily_spending(
            "user-1",
            "today",
        )

    assert result == pytest.approx(120)


def test_average_daily_spending_current_week():
    fixed_now = datetime(2026, 7, 15, 12, 0, 0)  # Wednesday

    with (
        patch(
            "services.analytics_service.datetime",
        ) as mocked_datetime,
        patch.object(
            AnalyticsService,
            "get_total_spending",
            return_value=300,
        ),
    ):
        mocked_datetime.now.return_value = fixed_now

        result = AnalyticsService.get_average_daily_spending(
            "user-1",
            "week",
        )

    assert result == pytest.approx(100)


def test_average_daily_spending_current_month():
    fixed_now = datetime(2026, 7, 15, 12, 0, 0)

    with (
        patch(
            "services.analytics_service.datetime",
        ) as mocked_datetime,
        patch.object(
            AnalyticsService,
            "get_total_spending",
            return_value=1500,
        ),
    ):
        mocked_datetime.now.return_value = fixed_now

        result = AnalyticsService.get_average_daily_spending(
            "user-1",
            "month",
        )

    assert result == pytest.approx(100)


def test_average_daily_spending_first_day_of_month():
    fixed_now = datetime(2026, 2, 1, 12, 0, 0)

    with (
        patch(
            "services.analytics_service.datetime",
        ) as mocked_datetime,
        patch.object(
            AnalyticsService,
            "get_total_spending",
            return_value=90,
        ),
    ):
        mocked_datetime.now.return_value = fixed_now

        result = AnalyticsService.get_average_daily_spending(
            "user-1",
            "month",
        )

    assert result == pytest.approx(90)


def test_average_daily_spending_invalid_period():
    with patch.object(
        AnalyticsService,
        "get_total_spending",
        return_value=100,
    ):
        result = AnalyticsService.get_average_daily_spending(
            "user-1",
            "year",
        )

    assert result == 0
