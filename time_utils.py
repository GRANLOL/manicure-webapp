from __future__ import annotations

from datetime import date as date_type
from datetime import datetime, time as time_type, timedelta, timezone

from config import salon_config


def get_salon_timezone() -> timezone:
    offset_hours = int(salon_config.get("timezone_offset", 3) or 3)
    return timezone(timedelta(hours=offset_hours))


def get_salon_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(get_salon_timezone())


def get_salon_today() -> date_type:
    return get_salon_now().date()


def combine_salon_datetime(target_date: date_type, target_time: time_type) -> datetime:
    return datetime.combine(target_date, target_time, tzinfo=get_salon_timezone())


def parse_salon_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=get_salon_timezone())
    return parsed.astimezone(get_salon_timezone())


def build_reminder_schedule(booking_dt: datetime, created_at: datetime | None = None, second_hours: int | None = None) -> dict[str, str | None]:
    created_at = created_at or get_salon_now()
    second_hours = int(second_hours if second_hours is not None else (salon_config.get("reminder_2_hours", 3) or 3))

    first_due = booking_dt - timedelta(hours=24)
    second_due = booking_dt - timedelta(hours=second_hours)

    return {
        "created_at": created_at.isoformat(),
        "first_reminder_due_at": first_due.isoformat() if created_at < first_due else None,
        "second_reminder_due_at": second_due.isoformat() if created_at < second_due else None,
    }
