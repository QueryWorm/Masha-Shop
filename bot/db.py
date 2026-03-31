import aiosqlite
from config import DB_PATH

async def get_services():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM services') as cursor:
            return await cursor.fetchall()

async def get_service(service_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM services WHERE id = ?', (service_id,)) as cursor:
            return await cursor.fetchone()

async def create_order(service_id: int, name: str, email: str, client_chat_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO orders (service_id, name, email, client_chat_id) VALUES (?, ?, ?, ?)',
            (service_id, name, email, client_chat_id)
        )
        await db.commit()
        return cursor.lastrowid

async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT o.*, s.title FROM orders o JOIN services s ON o.service_id = s.id WHERE o.id = ?',
            (order_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_orders(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = 'SELECT o.*, s.title FROM orders o JOIN services s ON o.service_id = s.id'
        if status:
            query += ' WHERE o.status = ?'
            async with db.execute(query + ' ORDER BY o.id DESC', (status,)) as cursor:
                return await cursor.fetchall()
        async with db.execute(query + ' ORDER BY o.id DESC') as cursor:
            return await cursor.fetchall()

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def add_service(slug: str, title: str, description: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO services (slug, title, description, price) VALUES (?, ?, ?, ?)',
            (slug, title, description, price)
        )
        await db.commit()

async def ensure_user_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tg_users (
                chat_id    INTEGER PRIMARY KEY,
                first_name TEXT,
                username   TEXT,
                saved_name TEXT
            )
        ''')
        await db.commit()

async def get_user(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tg_users WHERE chat_id = ?', (chat_id,)) as cursor:
            return await cursor.fetchone()

async def upsert_user(chat_id: int, first_name: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO tg_users (chat_id, first_name, username)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                first_name = excluded.first_name,
                username   = excluded.username
        ''', (chat_id, first_name, username))
        await db.commit()

async def save_user_name(chat_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE tg_users SET saved_name = ? WHERE chat_id = ?',
            (name, chat_id)
        )
        await db.commit()