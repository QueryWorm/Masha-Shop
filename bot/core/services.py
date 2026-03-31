import aiosqlite
from config import DB_PATH

async def get_all():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM services ORDER BY id') as cur:
            return await cur.fetchall()

async def get_by_id(service_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM services WHERE id = ?', (service_id,)) as cur:
            return await cur.fetchone()

async def update(service_id: int, title: str, description: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE services SET title=?, description=?, price=? WHERE id=?',
            (title, description, price, service_id)
        )
        await db.commit()

async def create(slug: str, title: str, description: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO services (slug, title, description, price) VALUES (?,?,?,?)',
            (slug, title, description, price)
        )
        await db.commit()