import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, MenuButtonCommands
from config import TG_TOKEN
from routers import client, admin

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(
        token=TG_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(client.router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Головне меню"),
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())