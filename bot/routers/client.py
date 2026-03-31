from html import escape
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from config import ADMIN_CHAT_ID, SITE_URL
import keyboards as kb
from core import users, services, orders

router = Router()
router.message.filter(F.from_user.id != ADMIN_CHAT_ID)
router.callback_query.filter(F.from_user.id != ADMIN_CHAT_ID)

PHOTO_DIR = '/var/www/app/public'

class OrderForm(StatesGroup):
    waiting_name = State()

async def show_main(target, name: str, edit: bool = False):
    text = f"Привіт, {escape(name)}! 👋\nЧим можу допомогти?"
    if edit and isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb.main_menu())
    else:
        msg = target.message if isinstance(target, CallbackQuery) else target
        await msg.answer(text, reply_markup=kb.main_menu())

async def show_services(target, edit: bool = False):
    all_services = await services.get_all()
    text = "Оберіть послугу:"
    if edit and isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb.services_menu(all_services))
    else:
        msg = target.message if isinstance(target, CallbackQuery) else target
        await msg.answer(text, reply_markup=kb.services_menu(all_services))

async def confirm_order(target, state: FSMContext, chat_id: int, bot=None):
    data = await state.get_data()
    user = await users.upsert_telegram(chat_id, data['name'])

    order_id = await orders.create(
        user_id        = user['id'],
        service_id     = data['service_id'],
        name           = data['name'],
        email          = '',
        client_chat_id = chat_id,
    )
    await state.clear()

    text = (
        f"✅ Заявку прийнято!\n"
        f"Послуга: <b>{escape(data['service_title'])}</b>\n"
        f"Зв'яжемося з вами найближчим часом."
    )

    if isinstance(target, CallbackQuery):
        # Якщо повідомлення з фото — не можна edit_text
        if target.message.photo:
            await target.message.delete()
            await target.message.answer(text, reply_markup=kb.after_order())
        else:
            await target.message.edit_text(text, reply_markup=kb.after_order())
        actual_bot = target.bot
    else:
        try:
            await target.delete()
        except Exception:
            pass
        await target.answer(text, reply_markup=kb.after_order())
        actual_bot = bot

    await actual_bot.send_message(
        ADMIN_CHAT_ID,
        f"🔔 <b>Нове замовлення #{order_id}</b>\n"
        f"Послуга: {escape(data['service_title'])}\n"
        f"Ім'я: {escape(data['name'])}\n"
        f"Telegram: tg://user?id={chat_id}",
        reply_markup=kb.order_actions(order_id)
    )

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await users.upsert_telegram(
        message.from_user.id,
        message.from_user.first_name or 'друже'
    )
    await show_main(message, user['name'])

@router.callback_query(F.data == kb.MAIN)
async def on_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await users.upsert_telegram(
        callback.from_user.id,
        callback.from_user.first_name or 'друже'
    )
    await show_main(callback, user['name'], edit=True)
    await callback.answer()

@router.callback_query(F.data == kb.SERVICES)
async def on_services(callback: CallbackQuery):
    await show_services(callback, edit=True)
    await callback.answer()

@router.callback_query(F.data.startswith("service:show:"))
async def on_service_show(callback: CallbackQuery):
    service_id = int(callback.data.split(":")[2])
    service    = await services.get_by_id(service_id)
    if not service:
        await callback.answer("Послугу не знайдено")
        return

    text = (
        f"<b>{escape(service['title'])}</b>\n\n"
        f"{escape(service['description'] or '')}\n\n"
        f"Вартість: <b>{service['price']:,} ₴</b>\n"
        f"<a href='{SITE_URL}/services/{service['slug']}'>Детальніше на сайті →</a>"
    ).replace(',', '\u00a0')

    # Якщо є фото — показуємо з фото
    if service['image']:
        photo_path = PHOTO_DIR + service['image']
        try:
            # Видаляємо старе повідомлення і шлємо нове з фото
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=FSInputFile(photo_path),
                caption=text,
                reply_markup=kb.service_detail(service_id)
            )
        except Exception:
            # Якщо файл не знайдено — показуємо без фото
            await callback.message.edit_text(text, reply_markup=kb.service_detail(service_id))
    else:
        await callback.message.edit_text(text, reply_markup=kb.service_detail(service_id))

    await callback.answer()

@router.callback_query(F.data.startswith("service:order:"))
async def on_service_order(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split(":")[2])
    service    = await services.get_by_id(service_id)
    await state.update_data(service_id=service_id, service_title=service['title'])

    saved_name = await users.get_saved_name(callback.from_user.id)
    text = f"Послуга: <b>{escape(service['title'])}</b>\n\nЯк вас звати?"

    if saved_name:
        await state.update_data(name=saved_name)
        await confirm_order(callback, state, callback.from_user.id)
        await callback.answer()
        return

    # Якщо повідомлення з фото — видаляємо і шлємо нове
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb.cancel(kb.SERVICES))
    else:
        await callback.message.edit_text(text, reply_markup=kb.cancel(kb.SERVICES))

    await state.set_state(OrderForm.waiting_name)
    await callback.answer()

@router.message(OrderForm.waiting_name)
async def on_name(message: Message, state: FSMContext, bot):
    name = message.text.strip()
    await users.save_name(message.from_user.id, name)
    await state.update_data(name=name)
    try:
        await message.delete()
    except Exception:
        pass
    await confirm_order(message, state, message.from_user.id, bot=bot)

@router.callback_query(F.data == kb.MY_ORDERS)
async def on_my_orders(callback: CallbackQuery):
    user        = await users.upsert_telegram(
        callback.from_user.id,
        callback.from_user.first_name or ''
    )
    user_orders = await orders.get_by_user(user['id'])

    STATUS = {
        'new':         '🆕 Нове',
        'in_progress': '🔄 В роботі',
        'done':        '🏁 Готово',
        'cancelled':   '❌ Скасовано',
    }

    if not user_orders:
        text = "У вас ще немає замовлень."
    else:
        lines = ["<b>Ваші замовлення:</b>\n"]
        for o in user_orders:
            lines.append(
                f"#{o['id']} {escape(o['service_title'])} — "
                f"{STATUS.get(o['status'], o['status'])}"
            )
        text = "\n".join(lines)

    # Якщо поточне повідомлення з фото — не можна edit_text
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb.cancel(kb.MAIN))
    else:
        await callback.message.edit_text(text, reply_markup=kb.cancel(kb.MAIN))

@router.message(F.text & ~F.text.startswith("/"))
async def on_unknown(message: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        user = await users.upsert_telegram(
            message.from_user.id,
            message.from_user.first_name or 'друже'
        )
        await show_main(message, user['name'])