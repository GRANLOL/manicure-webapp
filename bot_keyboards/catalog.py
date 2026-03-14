from __future__ import annotations

from .base import InlineKeyboardButton, InlineKeyboardMarkup, datetime, timedelta

def get_services_keyboard(services, page: int = 0, page_size: int = 20):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    total = len(services)
    start = page * page_size
    end = min(start + page_size, total)
    page_services = services[start:end]
    
    for s in page_services:
        if isinstance(s, dict):
            name = s['name']
            s_id = s['id']
            cat_name = s.get('category_name')
        else:
            s_id = s[0]
            name = s[1]
            cat_name = s[5] if len(s) > 5 else None
            
        cat_info = f" [{cat_name}]" if cat_name else " [Своб.]"
        builder.row(InlineKeyboardButton(text=f"✏️ {name[:20]}{cat_info}", callback_data=f"edit_srv_{s_id}_{page}"))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"srv_page_{page - 1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"srv_page_{page + 1}"))
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton(text="➕ Добавить услугу", callback_data="add_service"))
    return builder.as_markup()

def get_service_edit_keyboard(service):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    s_id = service['id']
    cur_dur = service.get('duration', 60)
    builder.row(InlineKeyboardButton(text="📝 Изменить название", callback_data=f"eds_name_{s_id}"))
    builder.row(InlineKeyboardButton(text="💸 Изменить цену", callback_data=f"eds_price_{s_id}"))
    builder.row(InlineKeyboardButton(text=f"⏱ Изменить длительность ({cur_dur} м)", callback_data=f"eds_dur_{s_id}"))
    builder.row(InlineKeyboardButton(text="📁 Изменить категорию", callback_data=f"eds_cat_{s_id}"))
    builder.row(InlineKeyboardButton(text="❌ Удалить услугу", callback_data=f"del_srv_{s_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_services"))
    return builder.as_markup()

def get_time_slots_keyboard(time_slots):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for ts in time_slots:
        val = ts['time_value'] if isinstance(ts, dict) else ts[1]
        ts_id = ts['id'] if isinstance(ts, dict) else ts[0]
        builder.row(InlineKeyboardButton(text=f"❌ Удалить {val}", callback_data=f"del_ts_{ts_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить слоты", callback_data="add_time_slot"))
    return builder.as_markup()

def build_category_tree(categories, parent_id=None, depth=0, branch=None):
    if branch is None:
        branch = set()

    tree = []
    for c in categories:
        c_id = c['id'] if isinstance(c, dict) else c[0]
        p_id = c.get('parent_id') if isinstance(c, dict) else (c[2] if len(c) > 2 else None)

        if p_id == parent_id:
            if c_id in branch:
                continue
            tree.append((c, depth))
            tree.extend(build_category_tree(categories, c_id, depth + 1, branch | {c_id}))
    return tree

def get_categories_keyboard(categories):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    tree = build_category_tree(categories)
    for c, depth in tree:
        name = c['name'] if isinstance(c, dict) else c[1]
        c_id = c['id'] if isinstance(c, dict) else c[0]
        prefix = "  " * depth + ("↳ " if depth > 0 else "📁 ")
        builder.row(InlineKeyboardButton(text=f"✏️ {prefix}{name[:20]}", callback_data=f"edit_cat_{c_id}"))
    builder.row(InlineKeyboardButton(text="➕ Создать категорию", callback_data="add_category"))
    builder.row(InlineKeyboardButton(text="➕ Создать подкатегорию", callback_data="add_subcategory_existing"))
    return builder.as_markup()

def get_category_edit_keyboard(category):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    c_id = category['id']
    builder.row(InlineKeyboardButton(text="📝 Изменить название", callback_data=f"edc_name_{c_id}"))
    builder.row(InlineKeyboardButton(text="🔄 Переместить", callback_data=f"move_cat_{c_id}"))
    builder.row(InlineKeyboardButton(text="➕ Создать подкатегорию", callback_data=f"wiz_addsub_{c_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить услугу", callback_data=f"wiz_addsrv_{c_id}"))
    builder.row(InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_cat_{c_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_categories"))
    return builder.as_markup()

def get_select_category_keyboard(categories):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    tree = build_category_tree(categories)
    for c, depth in tree:
        name = c['name'] if isinstance(c, dict) else c[1]
        c_id = c['id'] if isinstance(c, dict) else c[0]
        prefix = "  " * depth + ("↳ " if depth > 0 else "📁 ")
        builder.row(InlineKeyboardButton(text=f"{prefix}{name[:20]}", callback_data=f"sel_cat_{c_id}"))
        
    builder.row(InlineKeyboardButton(text="Без категории", callback_data="sel_cat_0"))
    return builder.as_markup()

def get_parent_category_keyboard(categories):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    tree = build_category_tree(categories)
    for c, depth in tree:
        name = c['name'] if isinstance(c, dict) else c[1]
        c_id = c['id'] if isinstance(c, dict) else c[0]
        prefix = "  " * depth + ("↳ " if depth > 0 else "📁 ")
        builder.row(InlineKeyboardButton(text=f"{prefix}{name[:20]}", callback_data=f"sel_parent_{c_id}"))
        
    builder.row(InlineKeyboardButton(text="Сделать основной (без родителя)", callback_data="sel_parent_0"))
    return builder.as_markup()

def get_wizard_keyboard(main_id, main_name, sub_id=None, sub_name=None, has_free_services=False):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    if sub_id:
        if has_free_services:
            builder.row(InlineKeyboardButton(text=f"📎 Добавить свободные услуги в '{sub_name[:15]}'", callback_data=f"wiz_attach_{sub_id}"))
        builder.row(InlineKeyboardButton(text=f"➕ Добавить новую услугу в '{sub_name[:15]}'", callback_data=f"wiz_addsrv_{sub_id}"))
        builder.row(InlineKeyboardButton(text=f"➕ Добавить еще подкатегорию в '{main_name[:15]}'", callback_data=f"wiz_addsub_{main_id}"))
    else:
        builder.row(InlineKeyboardButton(text=f"➕ Создать подкатегорию (внутри '{main_name[:15]}')", callback_data=f"wiz_addsub_{main_id}"))
        if has_free_services:
            builder.row(InlineKeyboardButton(text=f"📎 Добавить свободные услуги в '{main_name[:15]}'", callback_data=f"wiz_attach_{main_id}"))
        builder.row(InlineKeyboardButton(text=f"➕ Добавить новую услугу в '{main_name[:15]}'", callback_data=f"wiz_addsrv_{main_id}"))
            
    builder.row(InlineKeyboardButton(text="✅ Завершить", callback_data="wiz_finish"))
    return builder.as_markup()

def get_free_services_keyboard(free_services, selected_ids):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for s in free_services:
        s_id = s['id'] if isinstance(s, dict) else s[0]
        s_name = s['name'] if isinstance(s, dict) else s[1]
        
        # Check if selected
        is_selected = s_id in selected_ids
        prefix = "✅ " if is_selected else "⬜️ "
        
        builder.row(InlineKeyboardButton(text=f"{prefix}{s_name}", callback_data=f"toggle_srv_{s_id}"))
        
    builder.row(InlineKeyboardButton(text="Завершить выбор", callback_data="finish_service_selection"))
    return builder.as_markup()
