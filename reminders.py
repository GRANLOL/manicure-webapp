import asyncio
import logging
from html import escape

from aiogram import Bot

from config import salon_config
from database import (
    get_due_first_reminders,
    get_due_second_reminders,
    mark_first_reminder_sent,
    mark_second_reminder_sent,
    sync_completed_bookings,
)
from keyboards import get_reminder_keyboard
from time_utils import get_salon_now


def format_reminder(template: str, name: str, date: str, time: str) -> str:
    return template.replace("{name}", escape(name))\
                   .replace("{date}", escape(date))\
                   .replace("{time}", escape(time))


async def check_reminders(bot: Bot):
    try:
        await sync_completed_bookings()
        now = get_salon_now()
        now_iso = now.isoformat()

        first_due = await get_due_first_reminders(now_iso)
        for booking_id, user_id, name, date_str, time_str in first_due:
            template_1 = salon_config.get(
                "reminder_1_text",
                "Здравствуйте, {name}! Напоминаем о вашей записи завтра ({date}) в {time}.",
            )
            msg = format_reminder(template_1, name, date_str, time_str)
            try:
                await bot.send_message(user_id, text=msg, reply_markup=get_reminder_keyboard(booking_id), parse_mode="HTML")
                await mark_first_reminder_sent(booking_id, now_iso)
            except Exception as exc:
                logging.error("Failed to send 24h reminder to %s: %s", user_id, exc)

        second_due = await get_due_second_reminders(now_iso)
        for booking_id, user_id, name, date_str, time_str in second_due:
            template_2 = salon_config.get(
                "reminder_2_text",
                "Здравствуйте, {name}! Напоминаем, ваша запись состоится сегодня ({date}) в {time}.",
            )
            msg = format_reminder(template_2, name, date_str, time_str)
            try:
                await bot.send_message(user_id, text=msg, reply_markup=get_reminder_keyboard(booking_id), parse_mode="HTML")
                await mark_second_reminder_sent(booking_id, now_iso)
            except Exception as exc:
                logging.error("Failed to send configurable reminder to %s: %s", user_id, exc)
    except Exception as exc:
        logging.error("Error in check_reminders: %s", exc)


async def start_scheduler(bot: Bot):
    logging.info("Reminder scheduler started.")
    while True:
        try:
            await check_reminders(bot)
        except Exception as exc:
            logging.error("Scheduler loop error: %s", exc)

        await asyncio.sleep(15 * 60)
