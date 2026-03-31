import aiosqlite
from config import DB_PATH

async def create(user_id: int, service_id: int, name: str, email: str, client_chat_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            'INSERT INTO orders (service_id, user_id, name, email, client_chat_id) VALUES (?,?,?,?,?)',
            (service_id, user_id, name, email, client_chat_id)
        )
        await db.commit()
        return cur.lastrowid

async def get_by_id(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT o.*, s.title as service_title
            FROM orders o JOIN services s ON o.service_id = s.id
            WHERE o.id = ?
        ''', (order_id,)) as cur:
            return await cur.fetchone()

async def get_all(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = '''
            SELECT o.*, s.title as service_title
            FROM orders o JOIN services s ON o.service_id = s.id
        '''
        if status:
            query += ' WHERE o.status = ?'
            async with db.execute(query + ' ORDER BY o.id DESC', (status,)) as cur:
                return await cur.fetchall()
        async with db.execute(query + ' ORDER BY o.id DESC') as cur:
            return await cur.fetchall()

async def get_by_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT o.*, s.title as service_title
            FROM orders o JOIN services s ON o.service_id = s.id
            WHERE o.user_id = ?
            ORDER BY o.id DESC
        ''', (user_id,)) as cur:
            return await cur.fetchall()

async def update_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()