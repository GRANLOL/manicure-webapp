from __future__ import annotations

from .base import F, Router, database, escape, getenv, types

router = Router()


@router.callback_query(F.data.startswith("rem_conf_"))
async def reminder_confirm_cb(callback: types.CallbackQuery):
    booking_id = int(callback.data.split("_")[2])
    booking = await database.get_booking_by_id(booking_id)
    if booking and callback.from_user.id != booking[4]:
        await callback.answer("Эта кнопка не относится к вашей записи.", show_alert=True)
        return
    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Спасибо за подтверждение! Ждём вас в назначенное время.")

    admin_id = getenv("ADMIN_ID")
    if admin_id:
        msg = (
            "✅ <b>Запись подтверждена</b>\n\n"
            f"👤 <b>Клиент:</b> {escape(booking[0])}\n"
            f"📅 <b>Дата:</b> {booking[2]}\n"
            f"⏰ <b>Время:</b> {booking[3]}"
        )
        try:
            await callback.bot.send_message(admin_id, msg, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data.startswith("rem_canc_"))
async def reminder_cancel_cb(callback: types.CallbackQuery):
    booking_id = int(callback.data.split("_")[2])
    booking = await database.get_booking_by_id(booking_id)
    if booking and callback.from_user.id != booking[4]:
        await callback.answer("Эта кнопка не относится к вашей записи.", show_alert=True)
        return
    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    await database.cancel_booking_by_id(booking_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Ваша запись отменена. Будем рады видеть вас снова.")

    admin_id = getenv("ADMIN_ID")
    if admin_id:
        msg = (
            "❌ <b>Запись отменена</b>\n\n"
            f"👤 <b>Клиент:</b> {escape(booking[0])}\n"
            f"📅 <b>Дата:</b> {booking[2]}\n"
            f"⏰ <b>Время:</b> {booking[3]}\n"
            "<i>Отменено через кнопку в напоминании.</i>"
        )
        try:
            await callback.bot.send_message(admin_id, msg, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data.startswith("rem_resched_"))
async def reminder_resched_cb(callback: types.CallbackQuery):
    booking_id = int(callback.data.split("_")[2])
    booking = await database.get_booking_by_id(booking_id)
    if booking and callback.from_user.id != booking[4]:
        await callback.answer("Эта кнопка не относится к вашей записи.", show_alert=True)
        return
    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    await database.cancel_booking_by_id(booking_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Предыдущая запись отменена. Откройте запись заново и выберите другое время.")

    admin_id = getenv("ADMIN_ID")
    if admin_id:
        msg = (
            "🔄 <b>Перенос записи</b>\n\n"
            f"👤 <b>Клиент:</b> {escape(booking[0])}\n"
            f"📅 <b>Старая дата:</b> {booking[2]}\n"
            f"⏰ <b>Старое время:</b> {booking[3]}\n"
            "<i>Клиент отменил эту запись и выбирает новое окно.</i>"
        )
        try:
            await callback.bot.send_message(admin_id, msg, parse_mode="HTML")
        except Exception:
            pass
