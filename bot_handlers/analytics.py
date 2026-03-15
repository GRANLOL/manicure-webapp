from __future__ import annotations

from .base import F, Router, build_analytics_report, getenv, keyboards, types

router = Router()


@router.message(F.text == "📊 Статистика")
async def analytics_menu_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(message.from_user.id) != admin_id:
        return
    await message.answer(
        "📊 <b>Выберите период для статистики:</b>",
        reply_markup=keyboards.get_analytics_keyboard(),
        parse_mode="HTML",
    )


async def build_stats_report(period_days: int, period_label: str) -> str:
    return await build_analytics_report(period_days, period_label)


async def _send_stats(callback: types.CallbackQuery, period_days: int, period_label: str):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await callback.answer()
    await callback.message.edit_text("⏳ Считаю...", parse_mode="HTML")
    report = await build_stats_report(period_days, period_label)
    await callback.message.edit_text(report, parse_mode="HTML", reply_markup=keyboards.get_analytics_keyboard())


@router.callback_query(F.data == "stats_today")
async def stats_today_callback(callback: types.CallbackQuery):
    await _send_stats(callback, 0, "Сегодня")


@router.callback_query(F.data == "stats_week")
async def stats_week_callback(callback: types.CallbackQuery):
    await _send_stats(callback, 7, "За 7 дней")


@router.callback_query(F.data == "stats_month")
async def stats_month_callback(callback: types.CallbackQuery):
    await _send_stats(callback, 30, "За 30 дней")
