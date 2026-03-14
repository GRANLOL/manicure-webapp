from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from datetime import datetime, timedelta
from config import WEBAPP_URL, salon_config

# Главное меню (обычные кнопки под строкой ввода)
def get_main_menu(is_admin: bool = False, is_master: bool = False):
    kb = [
        [KeyboardButton(text="🌸 Записаться", web_app=WebAppInfo(url=WEBAPP_URL))],
        [KeyboardButton(text="💸 Прайс-лист"), KeyboardButton(text="💅 Портфолио")],
        [KeyboardButton(text="📍 Адрес"), KeyboardButton(text="📋 Мои записи")]
    ]
    if is_admin:
        kb.append([KeyboardButton(text="⚙️ Панель управления")])
    if is_master:
        kb.append([KeyboardButton(text="💼 Панель мастера")])
        
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Меню администратора
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗓 На сегодня"), KeyboardButton(text="🗓 Все записи"), KeyboardButton(text="📁 Категории")],
        [KeyboardButton(text="⚙️ Услуги"), KeyboardButton(text="📅 Окно брони")],
        [KeyboardButton(text="📅 График"), KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="📁 Excel")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🗑 Очистить"), KeyboardButton(text="👤 Меню клиента")]
    ],
    resize_keyboard=True
)

master_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Мои записи на сегодня"), KeyboardButton(text="🗓 Мои все записи")],
        [KeyboardButton(text="🔔 Настройка уведомлений")],
        [KeyboardButton(text="👤 Главное меню")]
    ],
    resize_keyboard=True
)
