import unittest
from datetime import datetime
from unittest.mock import patch

from time_utils import build_reminder_schedule, get_salon_timezone


class ReminderScheduleTests(unittest.TestCase):
    def test_build_reminder_schedule_plans_both_when_created_early(self):
        tz = get_salon_timezone()
        booking_dt = datetime(2026, 3, 20, 18, 0, tzinfo=tz)
        created_at = datetime(2026, 3, 18, 10, 0, tzinfo=tz)

        with patch.dict("time_utils.salon_config", {"reminder_2_hours": 3}, clear=False):
            schedule = build_reminder_schedule(booking_dt, created_at)

        self.assertIsNotNone(schedule["first_reminder_due_at"])
        self.assertIsNotNone(schedule["second_reminder_due_at"])

    def test_build_reminder_schedule_skips_first_when_created_inside_24h_window(self):
        tz = get_salon_timezone()
        booking_dt = datetime(2026, 3, 20, 18, 0, tzinfo=tz)
        created_at = datetime(2026, 3, 20, 10, 0, tzinfo=tz)

        with patch.dict("time_utils.salon_config", {"reminder_2_hours": 3}, clear=False):
            schedule = build_reminder_schedule(booking_dt, created_at)

        self.assertIsNone(schedule["first_reminder_due_at"])
        self.assertIsNotNone(schedule["second_reminder_due_at"])

    def test_build_reminder_schedule_skips_all_when_created_inside_second_window(self):
        tz = get_salon_timezone()
        booking_dt = datetime(2026, 3, 20, 18, 0, tzinfo=tz)
        created_at = datetime(2026, 3, 20, 16, 30, tzinfo=tz)

        with patch.dict("time_utils.salon_config", {"reminder_2_hours": 3}, clear=False):
            schedule = build_reminder_schedule(booking_dt, created_at)

        self.assertIsNone(schedule["first_reminder_due_at"])
        self.assertIsNone(schedule["second_reminder_due_at"])
