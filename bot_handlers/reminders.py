from __future__ import annotations

from .base import F, Router, database, getenv, types

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
        msg = f"Клиент {booking[0]} подтвердил запись на {booking[2]} в {booking[3]}."
        try:
            await callback.bot.send_message(admin_id, msg)
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

    await database.delete_booking_by_id(booking_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Ваша запись отменена. Будем рады видеть вас снова.")

    admin_id = getenv("ADMIN_ID")
    if admin_id:
        msg = f"Клиент {booking[0]} отменил запись на {booking[2]} в {booking[3]} через напоминание."
        try:
            await callback.bot.send_message(admin_id, msg)
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

    await database.delete_booking_by_id(booking_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Предыдущая запись отменена. Откройте запись заново и выберите другое время.")

    admin_id = getenv("ADMIN_ID")
    if admin_id:
        msg = f"Клиент {booking[0]} отменил запись на {booking[2]} в {booking[3]} и собирается выбрать новое время."
        try:
            await callback.bot.send_message(admin_id, msg)
        except Exception:
            pass
