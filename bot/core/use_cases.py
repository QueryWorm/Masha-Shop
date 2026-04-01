"""
USE CASE LAYER — єдиний мозок системи.
Всі фронти (Web, TG, WebApp) викликають тільки це.
Ніякої логіки у фронтах.
"""
import aiosqlite
from datetime import datetime
from config import DB_PATH
from core import users, services, orders

# ─── Типи результатів ────────────────────────────────────────

class Result:
    def __init__(self, ok: bool, data=None, error: str = None):
        self.ok    = ok
        self.data  = data
        self.error = error

def ok(data=None) -> Result:
    return Result(ok=True, data=data)

def err(message: str) -> Result:
    return Result(ok=False, error=message)

#Також треба додати link_telegram в use_cases.py:
async def link_telegram(token: str, chat_id: int) -> Result:
    from core.users import link_telegram as _link
    success = await _link(token, chat_id)
    return ok() if success else err("Токен недійсний або застарів")
    
# ─── Замовлення ──────────────────────────────────────────────

async def create_order(
    user_id:        int,
    service_id:     int,
    name:           str,
    source:         str,          # 'web' | 'telegram' | 'webapp'
    client_chat_id: int = None,
    email:          str = '',
) -> Result:
    """
    Створити замовлення. Єдина точка входу для всіх фронтів.
    source — звідки прийшов запит, для логування і аналітики.
    """
    service = await services.get_by_id(service_id)
    if not service:
        return err("Послугу не знайдено")

    if not name or not name.strip():
        return err("Вкажіть ім'я")

    order_id = await orders.create(
        user_id        = user_id,
        service_id     = service_id,
        name           = name.strip(),
        email          = email.strip(),
        client_chat_id = client_chat_id,
    )

    order = await orders.get_by_id(order_id)

    # Логуємо подію
    await _log_event('order_created', order_id, {
        'source':       source,
        'service_title': service['title'],
        'name':         name,
    })

    return ok({
        'order_id':      order_id,
        'service_title': service['title'],
        'name':          name,
        'status':        'new',
    })

async def change_status(
    order_id: int,
    status:   str,
    actor:    str = 'admin',   # 'admin' | 'system'
) -> Result:
    """
    Змінити статус замовлення.
    Єдина точка зміни статусу для адміна в TG і в Web.
    """
    allowed = {'new', 'in_progress', 'done', 'cancelled'}
    if status not in allowed:
        return err(f"Невідомий статус: {status}")

    order = await orders.get_by_id(order_id)
    if not order:
        return err("Замовлення не знайдено")

    await orders.update_status(order_id, status)

    await _log_event('status_changed', order_id, {
        'old_status': order['status'],
        'new_status': status,
        'actor':      actor,
    })

    return ok({
        'order_id':      order_id,
        'new_status':    status,
        'client_chat_id': order['client_chat_id'],
        'service_title': order['service_title'],
    })

async def get_order(order_id: int) -> Result:
    order = await orders.get_by_id(order_id)
    if not order:
        return err("Замовлення не знайдено")
    return ok(dict(order))

async def get_user_orders(user_id: int) -> Result:
    user_orders = await orders.get_by_user(user_id)
    return ok([dict(o) for o in user_orders])

async def get_orders_by_status(status: str = None) -> Result:
    all_orders = await orders.get_all(status)
    return ok([dict(o) for o in all_orders])

# ─── Каталог ─────────────────────────────────────────────────

async def get_catalog() -> Result:
    all_services = await services.get_all()
    return ok([dict(s) for s in all_services])

async def get_service(service_id: int) -> Result:
    service = await services.get_by_id(service_id)
    if not service:
        return err("Послугу не знайдено")
    return ok(dict(service))

# ─── Користувач ──────────────────────────────────────────────

async def get_or_create_tg_user(chat_id: int, name: str) -> Result:
    """
    Знайти або створити користувача по Telegram chat_id.
    Оновлює ім'я якщо змінилось.
    """
    user = await users.upsert_telegram(chat_id, name)
    return ok(dict(user))

async def get_saved_name(chat_id: int) -> Result:
    name = await users.get_saved_name(chat_id)
    return ok(name)

async def save_name(chat_id: int, name: str) -> Result:
    await users.save_name(chat_id, name)
    return ok(name)

# ─── Внутрішнє логування подій ───────────────────────────────

async def _log_event(event_type: str, order_id: int, payload: dict):
    """
    Проста таблиця подій. Потім можна повісити будь-який хендлер.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            import json
            await db.execute('''
                INSERT INTO events (event_type, order_id, payload)
                VALUES (?, ?, ?)
            ''', (event_type, order_id, json.dumps(payload, ensure_ascii=False)))
            await db.commit()
    except Exception:
        pass  # логування не має валити основну логіку