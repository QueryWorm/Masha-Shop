from html import escape
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from config import ADMIN_CHAT_ID
import keyboards as kb
from core import use_cases, services

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
    result = await use_cases.get_orders_by_status('new')
    if not result.data:
        await callback.message.edit_text("Нових замовлень немає.", reply_markup=back_to_admin())
        await callback.answer()
        return

    await callback.message.edit_text(
        f"🆕 <b>Нових замовлень: {len(result.data)}</b>",
        reply_markup=back_to_admin()
    )
    for o in result.data:
        await callback.message.answer(
            f"📋 <b>#{o['id']} {escape(o['service_title'])}</b>\n"
            f"Ім'я: {escape(o['name'] or '—')}\n"
            f"Email: {escape(o['email'] or '—')}\n"
            f"Дата: {o['created_at']}",
            reply_markup=kb.order_actions(o['id'])
        )
    await callback.answer()

@router.callback_query(F.data == "admin:orders:all")
async def on_all_orders(callback: CallbackQuery):
    result = await use_cases.get_orders_by_status()
    if not result.data:
        text = "Замовлень ще немає."
    else:
        lines = ["<b>Всі замовлення:</b>\n"]
        for o in result.data:
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
    result = await use_cases.get_catalog()
    lines  = ["<b>Послуги:</b>\n"]
    for s in result.data:
        lines.append(
            f"#{s['id']} {escape(s['title'])} — "
            f"{s['price']:,} ₴".replace(',', '\u00a0')
        )
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_admin())
    await callback.answer()

@router.callback_query(F.data.startswith("order:status:"))
async def on_status(callback: CallbackQuery, bot):
    _, _, order_id, status = callback.data.split(":")
    order_id = int(order_id)

    result = await use_cases.change_status(order_id, status, actor='admin')
    if not result.ok:
        await callback.answer(result.error)
        return

    await callback.message.edit_text(
        callback.message.text + f"\n\n<b>Статус:</b> {STATUS_LABELS[status]}"
    )
    await callback.answer("Статус оновлено")

    # Сповіщення клієнту
    d = result.data
    if d.get('client_chat_id'):
        try:
            await bot.send_message(
                d['client_chat_id'],
                f"{CLIENT_MESSAGES[status]}\n"
                f"Замовлення: <b>{escape(d['service_title'])}</b>",
                reply_markup=kb.after_order()
            )
        except Exception:
            pass

@router.callback_query(F.data == "admin:addservice")
async def on_addservice(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Назва нової послуги:", reply_markup=back_to_admin())
    await state.set_state(AddService.title)
    await callback.answer()

@router.message(AddService.title)
async def on_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("Опис (короткий, для превью):")
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