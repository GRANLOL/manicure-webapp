from __future__ import annotations

from .base import aiosqlite

async def add_master(name: str, telegram_id: str, category_id: int | None = None):
    async with aiosqlite.connect("bookings.db") as db:
        await db.execute("INSERT INTO masters (name, telegram_id, category_id) VALUES (?, ?, ?)", (name, telegram_id, category_id))
        await db.commit()

async def get_all_masters():
    async with aiosqlite.connect("bookings.db") as db:
        async with db.execute("SELECT id, name, telegram_id, category_id FROM masters") as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "name": r[1], "telegram_id": r[2], "category_id": r[3]} for r in rows]

async def delete_master(master_id: int):
    async with aiosqlite.connect("bookings.db") as db:
        await db.execute("DELETE FROM masters WHERE id = ?", (master_id,))
        await db.commit()

async def get_master_by_telegram_id(telegram_id: str):
    async with aiosqlite.connect("bookings.db") as db:
        async with db.execute("SELECT id, name, telegram_id, category_id FROM masters WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "telegram_id": row[2], "category_id": row[3]}
            return None

async def get_master_by_id(master_id: int):
    async with aiosqlite.connect("bookings.db") as db:
        async with db.execute("SELECT id, name, telegram_id, category_id FROM masters WHERE id = ?", (master_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "telegram_id": row[2], "category_id": row[3]}
            return None
