from html import escape
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from config import ADMIN_CHAT_ID, SITE_URL
import keyboards as kb
from core import use_cases

router = Router()
router.message.filter(F.from_user.id != ADMIN_CHAT_ID)
router.callback_query.filter(F.from_user.id != ADMIN_CHAT_ID)

PHOTO_DIR = '/var/www/app/public'

STATUS = {
    'new':         '🆕 Нове',
    'in_progress': '🔄 В роботі',
    'done':        '🏁 Готово',
    'cancelled':   '❌ Скасовано',
}

class OrderForm(StatesGroup):
    waiting_name = State()

# ─── Хелпери ─────────────────────────────────────────────────

async def show_main(target, name: str, edit: bool = False):
    text = f"Привіт, {escape(name)}! 👋\nЧим можу допомогти?"
    if edit and isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb.main_menu())
    else:
        msg = target.message if isinstance(target, CallbackQuery) else target
        await msg.answer(text, reply_markup=kb.main_menu())

async def show_services(target, edit: bool = False):
    result = await use_cases.get_catalog()
    text   = "Оберіть послугу:"
    kb_    = kb.services_menu(result.data)
    if edit and isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb_)
    else:
        msg = target.message if isinstance(target, CallbackQuery) else target
        await msg.answer(text, reply_markup=kb_)

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Редагує повідомлення — текст або caption якщо фото."""
    try:
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(text, reply_markup=reply_markup)
        else:
            await callback.message.edit_text(text, reply_markup=reply_markup)
    except Exception:
        await callback.message.answer(text, reply_markup=reply_markup)

# ─── Старт ───────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    args = message.text.split()

    # Прив'язка TG до акаунту сайту
    if len(args) > 1 and args[1].startswith('link_'):
        token   = args[1][5:]
        success = await use_cases.link_telegram(token, message.from_user.id)
        if success.ok:
            await message.answer("✅ Telegram успішно прив'язано до акаунту!")
        else:
            await message.answer("❌ Посилання недійсне або вже використане.")
        return

    result = await use_cases.get_or_create_tg_user(
        message.from_user.id,
        message.from_user.first_name or 'друже'
    )
    await show_main(message, result.data['name'])

# ─── Навігація ───────────────────────────────────────────────

@router.callback_query(F.data == kb.MAIN)
async def on_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    result = await use_cases.get_or_create_tg_user(
        callback.from_user.id,
        callback.from_user.first_name or 'друже'
    )
    await safe_edit(callback, f"Привіт, {escape(result.data['name'])}! 👋\nЧим можу допомогти?", kb.main_menu())
    await callback.answer()

@router.callback_query(F.data == kb.SERVICES)
async def on_services(callback: CallbackQuery):
    result = await use_cases.get_catalog()
    await safe_edit(callback, "Оберіть послугу:", kb.services_menu(result.data))
    await callback.answer()

# ─── Картка послуги ──────────────────────────────────────────

@router.callback_query(F.data.startswith("service:show:"))
async def on_service_show(callback: CallbackQuery):
    service_id = int(callback.data.split(":")[2])
    result     = await use_cases.get_service(service_id)

    if not result.ok:
        await callback.answer(result.error)
        return

    s = result.data
    text = (
        f"<b>{escape(s['title'])}</b>\n\n"
        f"{escape(s['description'] or '')}\n\n"
        f"Вартість: <b>{s['price']:,} ₴</b>\n"
        f"<a href='{SITE_URL}/services/{s['slug']}'>Детальніше на сайті →</a>"
    ).replace(',', '\u00a0')

    if s.get('image'):
        photo_path = PHOTO_DIR + s['image']
        try:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=FSInputFile(photo_path),
                caption=text,
                reply_markup=kb.service_detail(service_id)
            )
        except Exception:
            await safe_edit(callback, text, kb.service_detail(service_id))
    else:
        await safe_edit(callback, text, kb.service_detail(service_id))

    await callback.answer()

# ─── Замовлення ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("service:order:"))
async def on_service_order(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split(":")[2])
    result     = await use_cases.get_service(service_id)
    if not result.ok:
        await callback.answer(result.error)
        return

    await state.update_data(
        service_id    = service_id,
        service_title = result.data['title'],
    )

    name_result = await use_cases.get_saved_name(callback.from_user.id)
    saved_name  = name_result.data

    if saved_name:
        await state.update_data(name=saved_name)
        user_result = await use_cases.get_or_create_tg_user(
            callback.from_user.id,
            callback.from_user.first_name or ''
        )
        await _finish_order(callback, state, callback.from_user.id)
    else:
        await safe_edit(
            callback,
            f"Послуга: <b>{escape(result.data['title'])}</b>\n\nЯк вас звати?",
            kb.cancel(kb.SERVICES)
        )
        await state.set_state(OrderForm.waiting_name)

    await callback.answer()

@router.message(OrderForm.waiting_name)
async def on_name(message: Message, state: FSMContext, bot):
    name = message.text.strip()
    await use_cases.save_name(message.from_user.id, name)
    await state.update_data(name=name)
    try:
        await message.delete()
    except Exception:
        pass
    await _finish_order(message, state, message.from_user.id, bot=bot)

async def _finish_order(target, state: FSMContext, chat_id: int, bot=None):
    data   = await state.get_data()
    result = await use_cases.create_order(
        user_id        = (await use_cases.get_or_create_tg_user(chat_id, data.get('name', ''))).data['id'],
        service_id     = data['service_id'],
        name           = data['name'],
        source         = 'telegram',
        client_chat_id = chat_id,
    )
    await state.clear()

    if not result.ok:
        msg = target.message if isinstance(target, CallbackQuery) else target
        await msg.answer(f"Помилка: {result.error}")
        return

    text = (
        f"✅ Заявку прийнято!\n"
        f"Послуга: <b>{escape(result.data['service_title'])}</b>\n"
        f"Зв'яжемося з вами найближчим часом."
    )

    if isinstance(target, CallbackQuery):
        if target.message.photo:
            await target.message.delete()
            await target.message.answer(text, reply_markup=kb.after_order())
        else:
            await target.message.edit_text(text, reply_markup=kb.after_order())
        actual_bot = target.bot
    else:
        await target.answer(text, reply_markup=kb.after_order())
        actual_bot = bot

    # Сповіщення адміну
    await actual_bot.send_message(
        ADMIN_CHAT_ID,
        f"🔔 <b>Нове замовлення #{result.data['order_id']}</b>\n"
        f"Послуга: {escape(result.data['service_title'])}\n"
        f"Ім'я: {escape(result.data['name'])}\n"
        f"Telegram: tg://user?id={chat_id}",
        reply_markup=kb.order_actions(result.data['order_id'])
    )

# ─── Мої замовлення ──────────────────────────────────────────

@router.callback_query(F.data == kb.MY_ORDERS)
async def on_my_orders(callback: CallbackQuery):
    user_result   = await use_cases.get_or_create_tg_user(
        callback.from_user.id,
        callback.from_user.first_name or ''
    )
    orders_result = await use_cases.get_user_orders(user_result.data['id'])

    if not orders_result.data:
        text = "У вас ще немає замовлень."
    else:
        lines = ["<b>Ваші замовлення:</b>\n"]
        for o in orders_result.data:
            lines.append(
                f"#{o['id']} {escape(o['service_title'])} — "
                f"{STATUS.get(o['status'], o['status'])}"
            )
        text = "\n".join(lines)

    await safe_edit(callback, text, kb.cancel(kb.MAIN))
    await callback.answer()

# ─── Невідоме повідомлення ───────────────────────────────────

@router.message(F.text & ~F.text.startswith("/"))
async def on_unknown(message: Message, state: FSMContext):
    if await state.get_state() is None:
        result = await use_cases.get_or_create_tg_user(
            message.from_user.id,
            message.from_user.first_name or 'друже'
        )
        await show_main(message, result.data['name'])