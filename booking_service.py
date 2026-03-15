from os import getenv
from html import escape
import logging

from aiogram import types

import database
import keyboards

logger = logging.getLogger(__name__)


async def create_booking_and_notify(
    *,
    bot,
    user_id: int,
    user_full_name: str,
    service: str,
    date: str,
    time: str,
    duration: int,
    phone: str,
    name: str,
    price: int,
    master_id: int | None,
) -> tuple[bool, str]:
    full_name_service = f"{name} ({service})" if name else f"{user_full_name} ({service})"

    booking_created = await database.create_booking_if_available(
        user_id=user_id,
        name=full_name_service,
        phone=phone,
        date=date,
        time=time,
        master_id=master_id,
        duration=duration,
        service_name=service,
        price=price,
    )
    if not booking_created:
        return False, "Выбранный слот уже заняли. Обновите форму и выберите другое время."

    msg_text = (
        f"🔔 НОВАЯ ЗАПИСЬ!\n\n"
        f"👤 Клиент: {full_name_service}\n"
        f"📞 Тел: {phone}\n"
        f"📅 Дата: {date}\n"
        f"⏰ Время: {time}"
    )
    admin_id = getenv("ADMIN_ID")
    if admin_id and bot is not None:
        try:
            await bot.send_message(admin_id, msg_text)
        except Exception:
            logger.exception("Failed to send booking notification to admin", extra={"admin_id": admin_id})

    if master_id and bot is not None:
        try:
            master = await database.get_master_by_id(master_id)
            if master and master.get("telegram_id"):
                await bot.send_message(master["telegram_id"], msg_text)
        except Exception:
            logger.exception("Failed to send booking notification to master", extra={"master_id": master_id})

    return True, (
        f"✅ Запись подтверждена!\n\n"
        f"Услуга: {service}\n"
        f"📅 Дата: {date}\n"
        f"⏰ Время: {time}\n"
        f"📞 Телефон: {phone}\n\n"
        f"Ждем вас!"
    )


async def finalize_web_booking(
    message: types.Message,
    *,
    service: str,
    date: str,
    time: str,
    duration: int,
    phone: str,
    name: str,
    price: int,
    master_id: int | None,
    is_admin: bool,
    is_master: bool,
) -> None:
    success, result_text = await create_booking_and_notify(
        bot=message.bot,
        user_id=message.from_user.id,
        user_full_name=message.from_user.full_name,
        service=service,
        date=date,
        time=time,
        duration=duration,
        phone=phone,
        name=name,
        price=price,
        master_id=master_id,
    )
    if not success:
        await message.answer(result_text)
        return

    remove_msg = await message.answer("⏳ Загрузка...", reply_markup=types.ReplyKeyboardRemove())
    await remove_msg.delete()

    await message.answer(
        result_text,
        reply_markup=keyboards.get_main_menu(is_admin=is_admin, is_master=is_master),
    )


def format_user_booking_text(name: str, phone: str, date: str, time: str) -> str:
    safe_name = escape(name)
    safe_phone = escape(phone)
    safe_date = escape(date)
    safe_time = escape(time)
    text = "🗓 <b>Ваша запись:</b>\n\n"
    text += f"👤 <b>Имя/Услуга:</b> {safe_name}\n"
    text += f"📅 <b>Дата:</b> {safe_date}\n"
    text += f"⏰ <b>Время:</b> {safe_time}\n"
    text += f"📞 <b>Телефон:</b> {safe_phone}\n"
    return text


async def cancel_booking_and_notify(callback: types.CallbackQuery, *, booking_id: int, name: str, phone: str, date: str, time: str, master_id: int | None) -> None:
    await database.delete_booking_by_id(booking_id)
    await callback.message.edit_text("✅ Ваша запись успешно отменена.")

    msg_text = f"⚠️ ОТМЕНА ЗАПИСИ\n\nКлиент: {name}\nДата: {date}\nВремя: {time}\nТелефон: {phone}"
    admin_id = getenv("ADMIN_ID")
    if admin_id:
        try:
            await callback.bot.send_message(admin_id, msg_text)
        except Exception:
            logger.exception("Failed to send cancellation notification to admin", extra={"admin_id": admin_id})

    if master_id:
        try:
            master = await database.get_master_by_id(master_id)
            if master and master.get("telegram_id"):
                await callback.bot.send_message(master["telegram_id"], msg_text)
        except Exception:
            logger.exception("Failed to send cancellation notification to master", extra={"master_id": master_id})
