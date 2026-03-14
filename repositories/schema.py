from __future__ import annotations

from .base import aiosqlite

async def init_db():
    async with aiosqlite.connect("bookings.db") as db:
        # Создаем таблицу, если её нет
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                phone TEXT,
                date TEXT,
                time TEXT,
                master_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price TEXT,
                description TEXT,
                category_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                parent_id INTEGER
            )
        """)
        try:
            await db.execute("ALTER TABLE services ADD COLUMN category_id INTEGER")
        except aiosqlite.OperationalError:
            # Column already exists
            pass
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN master_id INTEGER")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN reminder_level INTEGER DEFAULT 0")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE services ADD COLUMN duration INTEGER DEFAULT 60")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN duration INTEGER DEFAULT 60")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN service_name TEXT")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN price INTEGER DEFAULT 0")
        except aiosqlite.OperationalError:
            pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS time_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS masters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                telegram_id TEXT,
                category_id INTEGER
            )
        """)
        await db.commit()
