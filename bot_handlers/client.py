from __future__ import annotations

import json

from .base import F, Router, FSMContext, escape, format_user_booking_text, finalize_web_booking, cancel_booking_and_notify, service_validate_web_booking, getenv, keyboards, database, salon_config, types

router = Router()

def format_price_list_page(services, page: int, page_size: int = 20):
    from collections import defaultdict
    categories = defaultdict(list)
    for s in services:
        cat_name = s.get('category_name') or "Без категории"
        categories[cat_name].append(s)
        
    sorted_cats = sorted(categories.keys())
    
    # Flatten into a list of lines so we can paginate them
    lines = []
    lines.append(f"<b>💰 ПРАЙС-ЛИСТ | {salon_config.get('salon_name', 'Ноготочки')}</b>")
    lines.append("______________________________\n")
    
    for cat in sorted_cats:
        lines.append(f"<b>📁 {cat}</b>")
        for s in categories[cat]:
            lines.append(f"▪️ {s['name']} — {s['price']}₽")
        lines.append("") # Empty line between categories
        
    total_lines = len(lines)
    
    import math
    total_pages = math.ceil(total_lines / page_size) if total_lines else 1
    
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, total_lines)
    
    page_text = "\n".join(lines[start_idx:end_idx])
    if total_pages > 1:
        page_text += f"\n<i>Страница {page + 1} из {total_pages}</i>"
        
    return page_text, total_pages

@router.message(F.text == "💸 Прайс-лист")
async def handle_price(message: types.Message):
    services = await database.get_all_services()
    if not services:
        await message.answer("Прайс-лист пока не заполнен.")
        return
        
    # We will paginate by 25 lines of text
    text, total_pages = format_price_list_page(services, page=0, page_size=25)
    
    await message.answer(
        text, 
        parse_mode="HTML",
        reply_markup=keyboards.get_client_price_keyboard(0, total_pages)
    )

@router.callback_query(F.data.startswith("client_price_page_"))
async def price_page_cb(callback: types.CallbackQuery):
    page_str = callback.data.split("_")[3]
    try:
        page = int(page_str)
    except ValueError:
        return
        
    services = await database.get_all_services()
    if not services:
        await callback.answer("Прайс-лист пуст", show_alert=True)
        return
        
    text, total_pages = format_price_list_page(services, page=page, page_size=25)
    
    await callback.message.edit_text(
        text, 
        parse_mode="HTML",
        reply_markup=keyboards.get_client_price_keyboard(page, total_pages)
    )

@router.message(F.text == "📍 Адрес")
async def handle_address(message: types.Message):
    address = salon_config.get('address', 'Адрес не указан.')
    hours = salon_config.get('working_hours', '')
    map_url = salon_config.get('map_url', '')
    
    text = f"<b>📍 Наш адрес</b>\n\n🏠 {address}\n"
    if hours:
        text += f"⏱ <i>{hours}</i>\n"
    if map_url:
        text += f"\n👉 <a href='{map_url}'>Открыть в картах</a>"
        
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=False)

@router.message(F.text == "💅 Портфолио")
async def handle_portfolio(message: types.Message):
    caption = "<b>📸 Наши работы</b>\n\n"
    portfolio_url = salon_config.get('portfolio_url', '')
    if portfolio_url:
        caption += f"🔗 <a href='{portfolio_url}'>Перейти в наше портфолио</a>"
    else:
        caption += "Портфолио не указано."
        
    await message.answer(caption, parse_mode="HTML")


@router.message(F.text == "🌸 Записаться")
async def launch_booking_webapp(message: types.Message):
    await message.answer(
        "Нажмите кнопку ниже, чтобы открыть запись.",
        reply_markup=keyboards.get_booking_launch_keyboard(),
    )

@router.message(F.web_app_data)
async def process_web_app_data(message: types.Message, state: FSMContext):
    try:
        data = json.loads(message.web_app_data.data)
        validated, error_text = await service_validate_web_booking(data)
        if error_text:
            await message.answer(error_text)
            return

        service = validated["service"]["name"]
        date = validated["date"]
        time = validated["time"]
        duration = validated["duration"]
        phone = validated["phone"]
        name = validated["name"]
        price = validated["price"]
        
        # Extract master_id from web app data
        admin_id = getenv("ADMIN_ID")
        is_admin = bool(admin_id and str(message.from_user.id) == admin_id)
        
        use_masters = salon_config.get("use_masters", False)
        is_master = False
        master_id = None
        
        if use_masters:
            master = await database.get_master_by_telegram_id(str(message.from_user.id))
            is_master = bool(master)
            master_id = validated["master_id"]
        
        await finalize_web_booking(
            message,
            service=service,
            date=date,
            time=time,
            duration=duration,
            phone=phone,
            name=name,
            price=price,
            master_id=master_id,
            is_admin=is_admin,
            is_master=is_master,
        )
        await state.clear()
        return

    except Exception as e:
        print(f"Error parsing web_app_data: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке данных. Попробуйте еще раз.")

@router.message(F.text == "📋 Мои записи")
async def my_bookings_handler(message: types.Message):
    bookings = await database.get_user_bookings(message.from_user.id)

    if not bookings:
        await message.answer("У вас нет активных записей. 🤷‍♀️")
        return

    for booking_id, name, phone, date, time, _master_id in bookings:
        await message.answer(
            format_user_booking_text(name, phone, date, time),
            reply_markup=keyboards.get_cancel_keyboard(message.from_user.id, booking_id),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_booking_callback(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    user_id_str = parts[1]

    if str(callback.from_user.id) != user_id_str:
        await callback.answer("Это не ваша запись!", show_alert=True)
        return

    booking_id = None
    if len(parts) > 2:
        try:
            booking_id = int(parts[2])
        except ValueError:
            booking_id = None

    if booking_id is not None:
        booking = await database.get_booking_record_by_id(booking_id)
    else:
        booking = await database.get_user_booking(int(user_id_str))
        booking_id = booking[4] if booking else None

    if not booking:
        await callback.answer("Запись уже отменена или не найдена.", show_alert=True)
        return

    if len(parts) > 2 and booking_id is not None:
        _id, _user_id, name, phone, date, time, master_id = booking
    else:
        name, phone, date, time, booking_id = booking[:5]
        master_id = None

    await cancel_booking_and_notify(
        callback,
        booking_id=booking_id,
        name=name,
        phone=phone,
        date=date,
        time=time,
        master_id=master_id,
    )
