from html import escape
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from config import ADMIN_CHAT_ID
import keyboards as kb
from core import orders, services

router = Router()
router.message.filter(F.from_user.id == ADMIN_CHAT_ID)
router.callback_query.filter(F.from_user.id == ADMIN_CHAT_ID)

STATUS_LABELS = {
    'new':         '🆕 Нове',
    'in_progress': '🔄 В роботі',
    'done':        '🏁 Готово',
    'cancelled':   '❌ Скасовано',
}

CLIENT_MESSAGES = {
    'in_progress': '🔄 Ваше замовлення взято в роботу!',
    'done':        '🏁 Ваше замовлення виконано! Дякуємо.',
    'cancelled':   '❌ Ваше замовлення скасовано.',
}

class AddService(StatesGroup):
    title       = State()
    description = State()
    price       = State()

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Нові замовлення",  callback_data="admin:orders:new")],
        [InlineKeyboardButton(text="📊 Всі замовлення",   callback_data="admin:orders:all")],
        [InlineKeyboardButton(text="🛍 Послуги",          callback_data="admin:services")],
        [InlineKeyboardButton(text="➕ Додати послугу",   callback_data="admin:addservice")],
    ])

def back_to_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="admin:main")]
    ])

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⚙️ <b>Адмін-панель</b>", reply_markup=admin_menu())

@router.callback_query(F.data == "admin:main")
async def on_admin_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("⚙️ <b>Адмін-панель</b>", reply_markup=admin_menu())
    await callback.answer()

@router.callback_query(F.data == "admin:orders:new")
async def on_new_orders(callback: CallbackQuery):
    new_orders = await orders.get_all('new')
    if not new_orders:
        await callback.message.edit_text(
            "Нових замовлень немає.",
            reply_markup=back_to_admin()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"🆕 <b>Нових замовлень: {len(new_orders)}</b>",
        reply_markup=back_to_admin()
    )
    for o in new_orders:
        await callback.message.answer(
            f"📋 <b>#{o['id']} {escape(o['service_title'])}</b>\n"
            f"Ім'я: {escape(o['name'] or '—')}\n"
            f"Email: {escape(o['email'])}\n"
            f"Дата: {o['created_at']}",
            reply_markup=kb.order_actions(o['id'])
        )
    await callback.answer()

@router.callback_query(F.data == "admin:orders:all")
async def on_all_orders(callback: CallbackQuery):
    all_orders = await orders.get_all()
    if not all_orders:
        text = "Замовлень ще немає."
    else:
        lines = ["<b>Всі замовлення:</b>\n"]
        for o in all_orders:
            lines.append(
                f"#{o['id']} {escape(o['service_title'])} — "
                f"{escape(o['name'] or '—')} — "
                f"{STATUS_LABELS.get(o['status'], o['status'])}"
            )
        text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=back_to_admin())
    await callback.answer()

@router.callback_query(F.data == "admin:services")
async def on_services(callback: CallbackQuery):
    all_services = await services.get_all()
    lines = ["<b>Послуги:</b>\n"]
    for s in all_services:
        lines.append(
            f"#{s['id']} {escape(s['title'])} — "
            f"{s['price']:,} ₴".replace(',', '\u00a0')
        )
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_admin()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("order:status:"))
async def on_status(callback: CallbackQuery, bot):
    _, _, order_id, status = callback.data.split(":")
    order_id = int(order_id)

    await orders.update_status(order_id, status)
    await callback.message.edit_text(
        callback.message.text + f"\n\n<b>Статус:</b> {STATUS_LABELS[status]}"
    )
    await callback.answer("Статус оновлено")

    order = await orders.get_by_id(order_id)
    if order and order['client_chat_id']:
        try:
            await bot.send_message(
                order['client_chat_id'],
                f"{CLIENT_MESSAGES[status]}\n"
                f"Замовлення: <b>{escape(order['service_title'])}</b>",
                reply_markup=kb.after_order()
            )
        except Exception:
            pass

@router.callback_query(F.data == "admin:addservice")
async def on_addservice(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Назва нової послуги:",
        reply_markup=back_to_admin()
    )
    await state.set_state(AddService.title)
    await callback.answer()

@router.message(AddService.title)
async def on_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("Опис:")
    await state.set_state(AddService.description)

@router.message(AddService.description)
async def on_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await message.answer("Ціна (число, у гривнях):")
    await state.set_state(AddService.price)

@router.message(AddService.price)
async def on_price(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("Тільки число:")
        return
    data = await state.get_data()
    slug = data['title'].lower().replace(' ', '_')
    await services.create(slug, data['title'], data['description'], int(message.text.strip()))
    await state.clear()
    await message.answer(
        f"✅ Послугу «{escape(data['title'])}» додано.",
        reply_markup=admin_menu()
    )