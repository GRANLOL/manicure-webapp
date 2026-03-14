from __future__ import annotations

from .base import InlineKeyboardButton, InlineKeyboardMarkup, salon_config

def get_working_days_keyboard(working_days, blacklisted_dates=[]):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Map for JS day index -> Russian Name
    days_map = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 0: "Вс"}
    
    # We will build rows of 3 buttons for days
    row = []
    for day_idx in [1, 2, 3, 4, 5, 6, 0]:
        name = days_map[day_idx]
        is_active = day_idx in working_days
        text = f"{name} {'✅' if is_active else '❌'}"
        row.append(InlineKeyboardButton(text=text, callback_data=f"toggle_day_{day_idx}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
        
    builder.row(InlineKeyboardButton(text="➕ Добавить выходную дату", callback_data="add_blacklist_date"))
    
    for date_str in blacklisted_dates:
        builder.row(InlineKeyboardButton(text=f"❌ Удалить выходной {date_str}", callback_data=f"del_bl_{date_str}"))
        
    return builder.as_markup()

def get_system_settings_keyboard(use_masters: bool):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    status_text = "ВКЛ" if use_masters else "ВЫКЛ"
    builder.row(InlineKeyboardButton(text=f"Режим мастеров: {status_text}", callback_data="toggle_use_masters"))
    if use_masters:
        builder.row(InlineKeyboardButton(text="👥 Управление мастерами", callback_data="manage_masters"))
    builder.row(InlineKeyboardButton(text="📬 Настройки напоминаний", callback_data="settings_reminders"))
    builder.row(InlineKeyboardButton(text="🌍 Часовой пояс (UTC)", callback_data="settings_timezone"))
    builder.row(InlineKeyboardButton(text="🕒 Часы работы", callback_data="settings_working_hours"))
    builder.row(InlineKeyboardButton(text="⏳ Шаг/Интервал записи", callback_data="settings_interval"))
    return builder.as_markup()

def get_reminder_settings_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✏️ Текст за 24 часа", callback_data="edit_rem_text_1"))
    builder.row(InlineKeyboardButton(text="✏️ Текст второго увед.", callback_data="edit_rem_text_2"))
    builder.row(InlineKeyboardButton(text="🕒 Время второго увед.", callback_data="edit_rem_time_2"))
    builder.row(InlineKeyboardButton(text="◀️ Назад в настройки", callback_data="back_to_settings"))
    return builder.as_markup()

def get_masters_keyboard(masters):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for m in masters:
        m_id = m['id']
        name = m['name']
        builder.row(InlineKeyboardButton(text=f"❌ Удалить {name}", callback_data=f"del_master_{m_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить мастера", callback_data="add_master"))
    builder.row(InlineKeyboardButton(text="◀️ Назад в настройки", callback_data="back_to_settings"))
    return builder.as_markup()

def get_clear_options_keyboard(use_masters: bool):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 Очистить за сегодня", callback_data="clear_today"))
    builder.row(InlineKeyboardButton(text="📆 Очистить за дату", callback_data="clear_date"))
    builder.row(InlineKeyboardButton(text="🗓️ Очистить за период", callback_data="clear_period"))
    if use_masters:
        builder.row(InlineKeyboardButton(text="👤 Очистить по мастеру", callback_data="clear_master"))
    builder.row(InlineKeyboardButton(text="🧹 Очистить прошедшие (до сегодня)", callback_data="clear_past"))
    builder.row(InlineKeyboardButton(text="🗑 Очистить ВСЕ записи", callback_data="clear_all"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()

def get_confirm_clear_keyboard(action: str, payload: str = ""):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    cb_data = f"confirm_clear_{action}"
    if payload:
        # Append payload to callback. E.g. confirm_clear_date_12.12.2023
        cb_data = f"confirm_clear_{action}_{payload}"
    builder.row(InlineKeyboardButton(text="⚠️ ДА, ОЧИСТИТЬ", callback_data=cb_data))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()

def get_clear_master_selection_keyboard(masters):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for m in masters:
        builder.row(InlineKeyboardButton(text=f"👤 {m['name']}", callback_data=f"clear_master_id_{m['id']}"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()
