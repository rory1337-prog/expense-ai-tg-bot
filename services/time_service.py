from datetime import UTC, datetime, time, timedelta

from config import APP_TIMEZONE


class TimeService:
    @staticmethod
    def utc_now_naive() -> datetime:
        """Return current UTC time for storage in TIMESTAMP WITHOUT TIME ZONE."""
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def local_now() -> datetime:
        return datetime.now(APP_TIMEZONE)

    @staticmethod
    def to_utc_naive(value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=APP_TIMEZONE)

        return value.astimezone(UTC).replace(tzinfo=None)

    @staticmethod
    def get_period_bounds(period: str) -> tuple[datetime, datetime] | None:
        now_local = TimeService.local_now()
        today = now_local.date()

        if period == "today":
            start_local = datetime.combine(
                today,
                time.min,
                tzinfo=APP_TIMEZONE,
            )
            end_local = start_local + timedelta(days=1)

        elif period == "week":
            start_date = today - timedelta(days=6)

            start_local = datetime.combine(
                start_date,
                time.min,
                tzinfo=APP_TIMEZONE,
            )
            end_local = datetime.combine(
                today + timedelta(days=1),
                time.min,
                tzinfo=APP_TIMEZONE,
            )

        elif period == "month":
            month_start = today.replace(day=1)

            if today.month == 12:
                next_month = today.replace(
                    year=today.year + 1,
                    month=1,
                    day=1,
                )
            else:
                next_month = today.replace(
                    month=today.month + 1,
                    day=1,
                )

            start_local = datetime.combine(
                month_start,
                time.min,
                tzinfo=APP_TIMEZONE,
            )
            end_local = datetime.combine(
                next_month,
                time.min,
                tzinfo=APP_TIMEZONE,
            )

        else:
            return None

        return (
            TimeService.to_utc_naive(start_local),
            TimeService.to_utc_naive(end_local),
        )
