from __future__ import annotations

from .base import F, Router, database, getenv, keyboards, salon_config, types

router = Router()

@router.message(F.text == "💼 Панель мастера")
async def master_panel_handler(message: types.Message):
    master = await database.get_master_by_telegram_id(str(message.from_user.id))
    if not master:
        return
    await message.answer("Вы перешли в панель мастера.", reply_markup=keyboards.master_menu)

@router.message(F.text == "📅 Мои записи на сегодня")
async def master_today_bookings_handler(message: types.Message):
    master = await database.get_master_by_telegram_id(str(message.from_user.id))
    if not master:
        return
        
    today = datetime.now().strftime("%d.%m.%Y")
    bookings = await database.get_bookings_by_master_and_date(master['id'], today)
    
    if not bookings:
        await message.answer("🏖 На сегодня у вас нет записей.")
        return
    
    text = "🗓 <b>Ваши записи на сегодня:</b>\n\n"
    for idx, (name, phone, date, time) in enumerate(bookings, 1):
        text += f"<b>{idx}.</b> {time} — {name} ({phone})\n"
        
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🗓 Мои все записи")
async def master_all_bookings_handler(message: types.Message):
    master = await database.get_master_by_telegram_id(str(message.from_user.id))
    if not master:
        return
        
    bookings = await database.get_bookings_by_master(master['id'])
    
    if not bookings:
        await message.answer("У вас пока нет записей. 🤷‍♀️")
        return
    
    text = "🗓 <b>Все ваши записи:</b>\n\n"
    for idx, (name, phone, date, time) in enumerate(bookings, 1):
        text += f"<b>{idx}.</b> {date} в {time} — {name} ({phone})\n"
        
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🔔 Настройка уведомлений")
async def master_notifications_handler(message: types.Message):
    master = await database.get_master_by_telegram_id(str(message.from_user.id))
    if not master:
        return
    await message.answer(
        "🔔 Уведомления о записях активны.\n\nВы будете получать сообщение каждый раз, когда клиент записывается к вам или отменяет запись."
    )
