import aiosqlite
from config import DB_PATH

async def get_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE id = ?', (user_id,)) as cur:
            return await cur.fetchone()

async def upsert_telegram(chat_id: int, name: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Шукаємо існуючого юзера по telegram провайдеру
        async with db.execute('''
            SELECT u.* FROM users u
            JOIN auth_providers ap ON ap.user_id = u.id
            WHERE ap.provider = 'telegram' AND ap.provider_id = ?
        ''', (str(chat_id),)) as cur:
            user = await cur.fetchone()

        if user:
            # Оновлюємо ім'я якщо змінилось
            await db.execute(
                'UPDATE users SET name = ? WHERE id = ?',
                (name, user['id'])
            )
            await db.commit()
            # Повертаємо оновленого
            async with db.execute('SELECT * FROM users WHERE id = ?', (user['id'],)) as cur:
                return await cur.fetchone()

        # Створюємо нового
        cur = await db.execute(
            'INSERT INTO users (name, role) VALUES (?, ?)',
            (name, 'client')
        )
        user_id = cur.lastrowid

        await db.execute(
            'INSERT INTO auth_providers (user_id, provider, provider_id) VALUES (?, ?, ?)',
            (user_id, 'telegram', str(chat_id))
        )
        await db.commit()

        async with db.execute('SELECT * FROM users WHERE id = ?', (user_id,)) as cur:
            return await cur.fetchone()

async def get_saved_name(chat_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT u.name FROM users u
            JOIN auth_providers ap ON ap.user_id = u.id
            WHERE ap.provider = 'telegram' AND ap.provider_id = ?
        ''', (str(chat_id),)) as cur:
            row = await cur.fetchone()
            return row['name'] if row else None

async def save_name(chat_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users SET name = ?
            WHERE id = (
                SELECT user_id FROM auth_providers
                WHERE provider = 'telegram' AND provider_id = ?
            )
        ''', (name, str(chat_id)))
        await db.commit()