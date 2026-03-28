from __future__ import annotations

import re

from .base import InlineKeyboardButton, InlineKeyboardMarkup, WEBAPP_URL, WebAppInfo


def _normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits


def _short_name(name: str, limit: int = 18) -> str:
    value = (name or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def get_cancel_keyboard(user_id: int, booking_id: int | None = None):
    callback_data = f"cancel_{user_id}_{booking_id}" if booking_id is not None else f"cancel_{user_id}"
    reschedule_callback = f"resched_{user_id}_{booking_id}" if booking_id is not None else f"resched_{user_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Отменить запись", callback_data=callback_data),
                InlineKeyboardButton(text="🔁 Перенести", callback_data=reschedule_callback),
            ]
        ]
    )


def get_booking_launch_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Открыть запись", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )


def get_portfolio_keyboard(url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✨ Открыть всю галерею", url=url)]
        ]
    )


def get_back_to_admin_menu_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_admin_menu"))
    return builder.as_markup()


def get_cancel_admin_action_keyboard(back_callback: str | None = None, back_text: str = "⬅️ Назад"):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    if back_callback:
        builder.row(InlineKeyboardButton(text=back_text, callback_data=back_callback))
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


def get_reschedule_dates_keyboard(booking_id: int, options: list[tuple[str, str]]):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for label, date_value in options:
        builder.row(InlineKeyboardButton(text=label, callback_data=f"resched_date_{booking_id}_{date_value}"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data=f"resched_cancel_{booking_id}"))
    return builder.as_markup()


def get_reschedule_times_keyboard(booking_id: int, date_value: str, times: list[str]):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    row: list[InlineKeyboardButton] = []
    for time_value in times:
        row.append(InlineKeyboardButton(text=time_value, callback_data=f"resched_time_{booking_id}_{date_value}_{time_value}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data=f"resched_cancel_{booking_id}"))
    return builder.as_markup()


def get_reschedule_confirm_keyboard(booking_id: int, date_value: str, time_value: str):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"resched_confirm_{booking_id}_{date_value}_{time_value}")
    )
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data=f"resched_cancel_{booking_id}"))
    return builder.as_markup()


def get_analytics_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 Сегодня", callback_data="stats_today"))
    builder.row(InlineKeyboardButton(text="🗓 За 7 дней", callback_data="stats_week"))
    builder.row(InlineKeyboardButton(text="📈 За 30 дней", callback_data="stats_month"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_excel_exports_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📋 Все записи", callback_data="excel_export_all"))
    builder.row(InlineKeyboardButton(text="✅ Выполненные услуги", callback_data="excel_export_completed"))
    builder.row(InlineKeyboardButton(text="👥 Клиентская база", callback_data="excel_export_clients"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_admin_service_picker_keyboard(services, *, prefix: str, page: int = 0, page_size: int = 12):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    total = len(services)
    start = page * page_size
    end = min(start + page_size, total)
    page_services = services[start:end]

    for service in page_services:
        category_name = service.get("category_name") or "Без категории"
        duration = int(service.get("duration") or 60)
        label = f"{service['name'][:22]} · {duration}м · {category_name[:14]}"
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"{prefix}_service_{page}_{service['id']}",
            )
        )

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{prefix}_service_page_{page - 1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"{prefix}_service_page_{page + 1}"))
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_admin_date_picker_keyboard(options: list[tuple[str, str]], *, prefix: str, back_callback: str):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for label, date_value in options:
        builder.row(InlineKeyboardButton(text=label, callback_data=f"{prefix}_date_{date_value}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_admin_time_picker_keyboard(date_value: str, times: list[str], *, prefix: str, back_callback: str):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    row: list[InlineKeyboardButton] = []
    for time_value in times:
        row.append(InlineKeyboardButton(text=time_value, callback_data=f"{prefix}_time_{date_value}_{time_value}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_manual_booking_source_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="WhatsApp", callback_data="manual_source_whatsapp"),
        InlineKeyboardButton(text="Instagram", callback_data="manual_source_instagram"),
    )
    builder.row(
        InlineKeyboardButton(text="Звонок", callback_data="manual_source_phone"),
        InlineKeyboardButton(text="Telegram", callback_data="manual_source_telegram"),
    )
    builder.row(
        InlineKeyboardButton(text="Офлайн", callback_data="manual_source_offline"),
        InlineKeyboardButton(text="Вручную", callback_data="manual_source_manual"),
    )
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_manual_booking_notes_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Пропустить", callback_data="manual_notes_skip"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_manual_booking_confirm_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить запись", callback_data="manual_confirm_submit"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_admin_booking_page_keyboard(bookings, context: str, page: int, total_pages: int):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    status_prefix = {
        "scheduled": "🟢",
        "completed": "✅",
        "no_show": "🟠",
        "cancelled": "❌",
    }
    for booking_id, name, _phone, date, time, _price, status in bookings:
        label = f"{status_prefix.get(status, '•')} {time} · {_short_name(name)}"
        if context == "all":
            label = f"{status_prefix.get(status, '•')} {date} · {time} · {_short_name(name)}"
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"booking_actions_{context}_{page}_{booking_id}",
            )
        )

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"bookings_page_{context}_{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"bookings_page_{context}_{page + 1}"))
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_action"))
    return builder.as_markup()


def get_admin_booking_actions_keyboard(
    booking_id: int,
    phone: str,
    context: str,
    page: int,
    *,
    status: str = "scheduled",
    telegram_user_id: int | None = None,
):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    digits = _normalize_phone(phone)

    contact_buttons = []
    if telegram_user_id:
        contact_buttons.append(InlineKeyboardButton(text="💬 Написать", url=f"tg://user?id={telegram_user_id}"))
    elif digits:
        contact_buttons.append(InlineKeyboardButton(text="💬 Написать", url=f"https://wa.me/{digits}"))

    if digits:
        contact_buttons.append(InlineKeyboardButton(text="📞 Показать номер", callback_data=f"show_phone_{digits}"))

    if contact_buttons:
        builder.row(*contact_buttons)

    if status == "scheduled":
        builder.row(
            InlineKeyboardButton(
                text="✅ Отметить выполненной",
                callback_data=f"admin_booking_status_{booking_id}_completed_{context}_{page}",
            ),
            InlineKeyboardButton(
                text="🟠 Не пришел",
                callback_data=f"admin_booking_status_{booking_id}_no_show_{context}_{page}",
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="❌ Отменить запись",
                callback_data=f"admin_booking_status_{booking_id}_cancelled_{context}_{page}",
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔄 Вернуть в активные",
                callback_data=f"admin_booking_status_{booking_id}_scheduled_{context}_{page}",
            )
        )

    builder.row(InlineKeyboardButton(text="⬅️ Назад к списку", callback_data=f"bookings_page_{context}_{page}"))
    return builder.as_markup()
