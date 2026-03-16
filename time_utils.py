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
