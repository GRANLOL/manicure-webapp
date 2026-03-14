from __future__ import annotations

import os

from .base import Command, FSInputFile, F, Router, escape, getenv, get_user_roles, keyboards, pd, database, salon_config, types

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    is_admin = bool(admin_id and str(message.from_user.id) == admin_id)
    
    use_masters = salon_config.get("use_masters", False)
    is_master = False
    
    if use_masters:
        master = await database.get_master_by_telegram_id(str(message.from_user.id))
        if master:
            is_master = True
            
    if is_master and not is_admin:
        await message.answer("Добро пожаловать в панель мастера!", reply_markup=keyboards.master_menu)
        return
    
    if is_admin:
        await message.answer("Добро пожаловать в панель администратора!", reply_markup=keyboards.admin_menu)
    else:
        await message.answer(
            salon_config.get("welcome_text", "Привет! Выберите нужное действие:"),
            reply_markup=keyboards.get_main_menu(is_admin=is_admin, is_master=is_master)
        )

@router.message(F.text == "👤 Главное меню")
@router.message(F.text == "👤 Меню клиента")
async def client_menu_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    is_admin = bool(admin_id and str(message.from_user.id) == admin_id)
    
    use_masters = salon_config.get("use_masters", False)
    is_master = False
    if use_masters:
        master = await database.get_master_by_telegram_id(str(message.from_user.id))
        is_master = bool(master)
        
    if not is_admin and not is_master:
        return
        
    await message.answer(
        "Вы переключились в главное меню клиента.",
        reply_markup=keyboards.get_main_menu(is_admin=is_admin, is_master=is_master)
    )

@router.message(Command("admin"))
@router.message(F.text == "⚙️ Панель управления")
async def admin_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(message.from_user.id) != admin_id:
        return # Игнорим всех, кроме админа
        
    await message.answer("Добро пожаловать в панель администратора!", reply_markup=keyboards.admin_menu)

@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu_callback(callback: types.CallbackQuery, state: FSMContext):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await state.clear()
    
    # Safely delete if possible, otherwise answer
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer("Добро пожаловать в панель администратора!", reply_markup=keyboards.admin_menu)

@router.callback_query(F.data == "cancel_admin_action")
async def cancel_admin_action_callback(callback: types.CallbackQuery, state: FSMContext):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(callback.from_user.id) != admin_id:
        return
    await state.clear()
    await callback.message.edit_text("Действие отменено.")

@router.message(Command("export_excel"))
@router.message(F.text == "📁 Excel")
async def export_excel_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(message.from_user.id) != admin_id:
        return
        
    bookings = await database.get_all_bookings()
    
    if not bookings:
        await message.answer("Пока нет ни одной записи для выгрузки. 🤷‍♀️")
        return
        
    # Преобразуем данные в DataFrame
    df = pd.DataFrame(bookings, columns=["Имя", "Телефон", "Дата", "Время", "Мастер"])
    file_path = "bookings_export.xlsx"
    
    # Сохраняем в Excel
    df.to_excel(file_path, index=False)
    
    # Отправляем файл
    excel_file = FSInputFile(file_path)
    await message.answer_document(excel_file, caption="📁 Ваши записи")
    
    # Удаляем временный файл
    os.remove(file_path)

@router.message(F.text == "🗓 Все записи")
async def view_all_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(message.from_user.id) != admin_id:
        return # Игнорим всех, кроме админа
        
    bookings = await database.get_all_bookings()
    
    if not bookings:
        await message.answer("Пока нет ни одной записи. 🤷‍♀️")
        return
        
    use_masters = salon_config.get("use_masters", False)
    text = "🗓 <b>Все записи:</b>\n\n"
    for idx, (name, phone, date, time, master_name) in enumerate(bookings, 1):
        safe_name = escape(name)
        safe_phone = escape(phone)
        safe_date = escape(date)
        safe_time = escape(time)
        safe_master = escape(master_name) if master_name else ""
        master_str = f" [Мастер: {safe_master}]" if use_masters and master_name else ""
        text += f"<b>{idx}.</b> {safe_date} в {safe_time} — {safe_name} ({safe_phone}){master_str}\n"
        
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🗓 На сегодня")
async def todays_bookings_handler(message: types.Message):
    admin_id = getenv("ADMIN_ID")
    if not admin_id or str(message.from_user.id) != admin_id:
        return
    
    today_str = datetime.now().strftime("%d.%m.%Y")
    bookings = await database.get_bookings_by_date_full(today_str)
    
    if not bookings:
        await message.answer(f"На сегодня ({today_str}) записей нет. 🧘‍♀️")
        return
        
    use_masters = salon_config.get("use_masters", False)
    text = f"🗓 <b>Записи на сегодня ({today_str}):</b>\n\n"
    

    for idx, (name, phone, date, time, master_name) in enumerate(bookings, 1):
        safe_name = escape(name)
        safe_phone = escape(phone)
        safe_time = escape(time)
        safe_master = escape(master_name) if master_name else ""
        master_str = f" [Мастер: {safe_master}]" if use_masters and master_name else ""
        text += f"<b>{idx}.</b> {safe_time} — {safe_name} ({safe_phone}){master_str}\n"
        
    await message.answer(text, parse_mode="HTML")
