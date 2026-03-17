import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import reminders
from backup_service import run_scheduled_backup_if_due
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


class ReminderMaintenanceTests(unittest.IsolatedAsyncioTestCase):
    async def test_check_reminders_sends_fresh_first_reminder(self):
        bot = SimpleNamespace(send_message=AsyncMock())
        fake_now = datetime(2026, 3, 17, 10, 5, tzinfo=get_salon_timezone())
        first_due = [(55, 10, "Alice", "18.03.2026", "10:00", "2026-03-17T10:00:00+05:00")]

        with patch.object(reminders, "get_salon_now", return_value=fake_now), \
             patch.object(reminders, "sync_completed_bookings", AsyncMock()), \
             patch.object(reminders, "get_due_first_reminders", AsyncMock(return_value=first_due)), \
             patch.object(reminders, "get_due_second_reminders", AsyncMock(return_value=[])), \
             patch.object(reminders, "mark_first_reminder_sent", AsyncMock()) as mark_first_mock, \
             patch.object(reminders, "get_reminder_keyboard", return_value="kb"), \
             patch.dict("reminders.salon_config", {"reminder_grace_minutes": 30}, clear=False):
            await reminders.check_reminders(bot)

        bot.send_message.assert_awaited_once()
        mark_first_mock.assert_awaited_once_with(55, fake_now.isoformat())

    async def test_check_reminders_skips_stale_first_reminder_after_restart(self):
        bot = SimpleNamespace(send_message=AsyncMock())
        fake_now = datetime(2026, 3, 17, 20, 55, tzinfo=get_salon_timezone())
        first_due = [(55, 10, "Alice", "18.03.2026", "10:00", "2026-03-17T10:00:00+05:00")]

        with patch.object(reminders, "get_salon_now", return_value=fake_now), \
             patch.object(reminders, "sync_completed_bookings", AsyncMock()), \
             patch.object(reminders, "get_due_first_reminders", AsyncMock(return_value=first_due)), \
             patch.object(reminders, "get_due_second_reminders", AsyncMock(return_value=[])), \
             patch.object(reminders, "mark_first_reminder_sent", AsyncMock()) as mark_first_mock, \
             patch.dict("reminders.salon_config", {"reminder_grace_minutes": 30}, clear=False):
            await reminders.check_reminders(bot)

        bot.send_message.assert_not_awaited()
        mark_first_mock.assert_awaited_once_with(55, fake_now.isoformat())

    async def test_send_admin_daily_digest_sends_summary_once(self):
        bot = SimpleNamespace(send_message=AsyncMock())
        bookings = [("Alice", "+100", "17.03.2026", "10:00", 2500)]
        fake_now = datetime(2026, 3, 17, 10, 0, tzinfo=get_salon_timezone())

        with patch.object(reminders, "get_salon_now", return_value=fake_now), \
             patch.object(reminders, "get_runtime_value", return_value=None), \
             patch.object(reminders, "set_runtime_value") as set_runtime_mock, \
             patch.object(reminders, "get_bookings_by_date_full", AsyncMock(return_value=bookings)), \
             patch.dict("reminders.salon_config", {"admin_digest_hour": 9}, clear=False), \
             patch.dict("os.environ", {"ADMIN_ID": "777"}, clear=False):
            await reminders.send_admin_daily_digest(bot)

        bot.send_message.assert_awaited_once()
        set_runtime_mock.assert_called_once()


class BackupServiceTests(unittest.TestCase):
    def test_run_scheduled_backup_if_due_skips_before_target_hour(self):
        fake_now = datetime(2026, 3, 17, 1, 0, tzinfo=get_salon_timezone())

        with patch("backup_service.get_salon_now", return_value=fake_now), \
             patch.dict("backup_service.salon_config", {"backup_hour": 3}, clear=False):
            self.assertIsNone(run_scheduled_backup_if_due())
