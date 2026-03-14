from __future__ import annotations

from .base import InlineKeyboardButton, InlineKeyboardMarkup

def get_cancel_keyboard(user_id: int, booking_id: int | None = None):
    callback_data = f"cancel_{user_id}_{booking_id}" if booking_id is not None else f"cancel_{user_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить запись", callback_data=callback_data)]
        ]
    )

def get_back_to_admin_menu_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_admin_menu"))
    return builder.as_markup()

def get_cancel_admin_action_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()

def get_client_price_keyboard(page: int, total_pages: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    if total_pages <= 1:
        return None
        
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"client_price_page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"client_price_page_{page + 1}"))
        
    if nav_buttons:
        builder.row(*nav_buttons)
        
    return builder.as_markup()

def get_reminder_keyboard(booking_id: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"rem_conf_{booking_id}"))
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"rem_canc_{booking_id}"),
        InlineKeyboardButton(text="🔄 Перенести", callback_data=f"rem_resched_{booking_id}")
    )
    return builder.as_markup()

def get_analytics_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 Сегодня", callback_data="stats_today"))
    builder.row(InlineKeyboardButton(text="📆 За 7 дней", callback_data="stats_week"))
    builder.row(InlineKeyboardButton(text="🗓 За 30 дней", callback_data="stats_month"))
    return builder.as_markup()
