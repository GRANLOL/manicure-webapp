import asyncio
import logging
from datetime import datetime
from html import escape
from aiogram import Bot

from database import get_bookings_for_reminders, update_reminder_level
from keyboards import get_reminder_keyboard
from config import salon_config
from time_utils import combine_salon_datetime, get_salon_now

def format_reminder(template: str, name: str, date: str, time: str) -> str:
    return template.replace("{name}", escape(name))\
                   .replace("{date}", escape(date))\
                   .replace("{time}", escape(time))

async def check_reminders(bot: Bot):
    try:
        now = get_salon_now()
        # Fetch bookings that haven't received the final reminder yet (level < 2)
        bookings = await get_bookings_for_reminders(2)

        for b in bookings:
            b_id, user_id, name, date_str, time_str, reminder_level = b
            try:
                booking_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                booking_time = datetime.strptime(time_str, "%H:%M").time()
                booking_dt = combine_salon_datetime(booking_date, booking_time)
            except ValueError:
                continue
                
            time_diff = booking_dt - now
            hours_until = time_diff.total_seconds() / 3600.0

            if hours_until < 0:
                continue

            # 24-hour reminder
            if reminder_level == 0 and hours_until <= 24:
                template_1 = salon_config.get(
                    "reminder_1_text",
                    "Здравствуйте, {name}! Напоминаем о вашей записи завтра ({date}) в {time}."
                )
                msg = format_reminder(template_1, name, date_str, time_str)
                try:
                    await bot.send_message(user_id, text=msg, reply_markup=get_reminder_keyboard(b_id), parse_mode="HTML")
                    await update_reminder_level(b_id, 1)
                except Exception as e:
                    logging.error(f"Failed to send 24h reminder to {user_id}: {e}")

            # Second reminder (configurable hours)
            h2 = salon_config.get("reminder_2_hours", 3)
            if reminder_level == 1 and hours_until <= h2:
                template_2 = salon_config.get(
                    "reminder_2_text",
                    "Здравствуйте, {name}! Напоминаем, ваша запись состоится сегодня ({date}) в {time}."
                )
                msg = format_reminder(template_2, name, date_str, time_str)
                try:
                    await bot.send_message(user_id, text=msg, reply_markup=get_reminder_keyboard(b_id), parse_mode="HTML")
                    await update_reminder_level(b_id, 2)
                except Exception as e:
                    logging.error(f"Failed to send configurable reminder to {user_id}: {e}")
                    
    except Exception as e:
        logging.error(f"Error in check_reminders: {e}")

async def start_scheduler(bot: Bot):
    """Background task to check for upcoming bookings periodically."""
    logging.info("Reminder scheduler started.")
    while True:
        try:
            await check_reminders(bot)
        except Exception as e:
            logging.error(f"Scheduler loop error: {e}")
        
        # Checking every 15 minutes
        await asyncio.sleep(15 * 60)
