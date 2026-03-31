from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Константи — ніяких магічних рядків в роутерах
MAIN        = "menu:main"
SERVICES    = "menu:services"
MY_ORDERS   = "menu:my_orders"

def cb(action: str, *args) -> str:
    if args:
        return f"{action}:{':'.join(str(a) for a in args)}"
    return action

def parse(data: str) -> tuple:
    parts = data.split(":")
    return parts[0] + ":" + parts[1], parts[2:]

# Головне меню
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Послуги",       callback_data=SERVICES)],
        [InlineKeyboardButton(text="📋 Мої замовлення", callback_data=MY_ORDERS)],
    ])

# Список послуг
def services_menu(services) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{s['title']} — {s['price']:,} ₴".replace(',', '\u00a0'),
            callback_data=cb("service:show", s['id'])
        )]
        for s in services
    ]
    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data=MAIN)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Сторінка послуги
def service_detail(service_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Замовити",  callback_data=cb("service:order", service_id))],
        [InlineKeyboardButton(text="⬅ Назад",     callback_data=SERVICES)],
    ])

# Скасувати поточну дію
def cancel(back_to: str = MAIN) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data=back_to)]
    ])

# Кнопки статусу замовлення для адміна
def order_actions(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 В роботі", callback_data=cb("order:status", order_id, "in_progress")),
            InlineKeyboardButton(text="🏁 Готово",    callback_data=cb("order:status", order_id, "done")),
        ],
        [
            InlineKeyboardButton(text="❌ Скасувати", callback_data=cb("order:status", order_id, "cancelled")),
        ]
    ])

# Після оформлення замовлення
def after_order() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мої замовлення", callback_data=MY_ORDERS)],
        [InlineKeyboardButton(text="🏠 Головне меню",   callback_data=MAIN)],
    ])