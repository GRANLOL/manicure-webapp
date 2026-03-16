from __future__ import annotations

import re

from .base import Command, F, Router, FSMContext, datetime, getenv, keyboards, database, types
from .states import ClearBookingsForm

router = Router()


@router.message(Command("clear_bookings"))
@router.message(F.text == "🗑 Очистить")
async def clear_bookings_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(message.from_user.id) != admin_id:
        return

    await message.answer(
        "🗑 <b>Очистка записей</b>\n\nВыберите, какие записи нужно удалить.",
        parse_mode="HTML",
        reply_markup=keyboards.get_clear_options_keyboard(),
    )


@router.callback_query(F.data == "clear_today")
async def clear_today_cb(callback: types.CallbackQuery):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await callback.message.edit_text(
        "⚠️ <b>Подтверждение</b>\n\nУдалить <b>все записи за сегодня</b>?",
        parse_mode="HTML",
        reply_markup=keyboards.get_confirm_clear_keyboard("today"),
    )


@router.callback_query(F.data == "clear_past")
async def clear_past_cb(callback: types.CallbackQuery):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await callback.message.edit_text(
        "⚠️ <b>Подтверждение</b>\n\nУдалить все <b>прошедшие записи</b>?",
        parse_mode="HTML",
        reply_markup=keyboards.get_confirm_clear_keyboard("past"),
    )


@router.callback_query(F.data == "clear_all")
async def clear_all_cb(callback: types.CallbackQuery):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await callback.message.edit_text(
        "⚠️ <b>Подтверждение</b>\n\nУдалить <b>все записи</b> из базы?",
        parse_mode="HTML",
        reply_markup=keyboards.get_confirm_clear_keyboard("all"),
    )


@router.callback_query(F.data == "clear_date")
async def clear_date_cb(callback: types.CallbackQuery, state: FSMContext):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await state.set_state(ClearBookingsForm.waiting_for_date)
    await callback.message.edit_text(
        "📅 <b>Очистка по дате</b>\n\nВведите дату в формате <code>ДД.ММ.ГГГГ</code>.",
        parse_mode="HTML",
        reply_markup=keyboards.get_cancel_admin_action_keyboard(),
    )


@router.message(ClearBookingsForm.waiting_for_date)
async def process_clear_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str):
        await message.answer("Неверный формат. Используйте <code>ДД.ММ.ГГГГ</code>.", parse_mode="HTML")
        return
    await state.clear()
    await message.answer(
        f"⚠️ <b>Подтверждение</b>\n\nУдалить все записи за <b>{date_str}</b>?",
        parse_mode="HTML",
        reply_markup=keyboards.get_confirm_clear_keyboard("date", date_str),
    )


@router.callback_query(F.data == "clear_period")
async def clear_period_cb(callback: types.CallbackQuery, state: FSMContext):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await state.set_state(ClearBookingsForm.waiting_for_period_start)
    await callback.message.edit_text(
        "📆 <b>Очистка по периоду</b>\n\nВведите <b>начальную дату</b> в формате <code>ДД.ММ.ГГГГ</code>.",
        parse_mode="HTML",
        reply_markup=keyboards.get_cancel_admin_action_keyboard(),
    )


@router.message(ClearBookingsForm.waiting_for_period_start)
async def process_clear_period_start(message: types.Message, state: FSMContext):
    start_str = message.text.strip()
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", start_str):
        await message.answer("Неверный формат. Введите начальную дату в формате <code>ДД.ММ.ГГГГ</code>.", parse_mode="HTML")
        return
    await state.update_data(clear_start=start_str)
    await state.set_state(ClearBookingsForm.waiting_for_period_end)
    await message.answer(
        f"📆 <b>Начальная дата:</b> {start_str}\n\nТеперь введите <b>конечную дату</b> в формате <code>ДД.ММ.ГГГГ</code>.",
        parse_mode="HTML",
        reply_markup=keyboards.get_cancel_admin_action_keyboard(),
    )


@router.message(ClearBookingsForm.waiting_for_period_end)
async def process_clear_period_end(message: types.Message, state: FSMContext):
    end_str = message.text.strip()
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", end_str):
        await message.answer("Неверный формат. Введите конечную дату в формате <code>ДД.ММ.ГГГГ</code>.", parse_mode="HTML")
        return
    data = await state.get_data()
    start_str = data.get("clear_start")
    await state.clear()

    payload = f"{start_str}-{end_str}"
    await message.answer(
        f"⚠️ <b>Подтверждение</b>\n\nУдалить все записи с <b>{start_str}</b> по <b>{end_str}</b>?",
        parse_mode="HTML",
        reply_markup=keyboards.get_confirm_clear_keyboard("period", payload),
    )


@router.callback_query(F.data.startswith("confirm_clear_"))
async def confirm_clear_cb(callback: types.CallbackQuery):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return

    parts = callback.data.split("_", 3)
    action = parts[2]
    payload = parts[3] if len(parts) > 3 else ""

    deleted = 0
    if action == "today":
        today_str = datetime.now().strftime("%d.%m.%Y")
        deleted = await database.delete_bookings_by_date(today_str)
        text = f"✅ Удалено <b>{deleted}</b> записей за <b>{today_str}</b>."
    elif action == "past":
        deleted = await database.delete_past_bookings()
        text = f"✅ Удалено <b>{deleted}</b> прошедших записей."
    elif action == "all":
        await database.clear_bookings()
        text = "✅ Все записи удалены из базы."
    elif action == "date":
        deleted = await database.delete_bookings_by_date(payload)
        text = f"✅ Удалено <b>{deleted}</b> записей за <b>{payload}</b>."
    elif action == "period":
        start_str, end_str = payload.split("-")
        deleted = await database.delete_bookings_by_period(start_str, end_str)
        text = f"✅ Удалено <b>{deleted}</b> записей за период с <b>{start_str}</b> по <b>{end_str}</b>."
    else:
        text = "Произошла ошибка: неизвестное действие."

    await callback.message.edit_text(text, parse_mode="HTML")
