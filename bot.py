# ===== IMPORTS =====
import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from database import init_db
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.reports import router as reports_router
from handlers.expenses import router as expenses_router

load_dotenv()

BOT_TOKEN = os.getenv('BOTTOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(reports_router)
dp.include_router(expenses_router)

async def main():
    init_db()
    print('Database initialized...')
    print('Bot started...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())