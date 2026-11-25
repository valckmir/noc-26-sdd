from datetime import date, timedelta
from zoneinfo import ZoneInfo


def facility_today(timezone_name: str, *, now=None) -> date:
    zone = ZoneInfo(timezone_name)
    if now is None:
        from datetime import datetime

        now = datetime.now(zone)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=zone)
    return now.astimezone(zone).date()


def is_arrival_date_allowed(arrival_date: date, timezone_name: str, *, today: date | None = None) -> bool:
    return arrival_date >= (today or facility_today(timezone_name))


def cancellation_deadline(check_in: date) -> date:
    return check_in - timedelta(days=2)


def can_cancel(check_in: date, timezone_name: str, *, today: date | None = None) -> bool:
    current_date = today or facility_today(timezone_name)
    return current_date <= cancellation_deadline(check_in)
