# ===== IMPORTS =====
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message 
from dotenv import load_dotenv
from database import init_db
from aiogram.types import CallbackQuery
from keyboards.main_menu import main_menu
from keyboards.reports_menu import reports_menu

load_dotenv()

BOT_TOKEN = os.getenv('BOTTOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "💸 ExpensesAI\n\nChoose an action:",
        reply_markup=main_menu
    )

@dp.message(lambda message: message.text == "➕ Add expense")
async def add_expense_handler(message: Message):
    await message.answer("Send expense like:\ncoffee 15")


@dp.message(lambda message: message.text == "📊 Reports")
async def reports_handler(message: Message):
    await message.answer(
        "📊 Reports Menu",
        reply_markup=reports_menu
    )


@dp.message(lambda message: message.text == "✏️ Edit")
async def edit_handler(message: Message):
    await message.answer("Edit menu coming soon ✏️")


@dp.message(lambda message: message.text == "⚙️ Settings")
async def settings_handler(message: Message):
    await message.answer("Settings menu coming soon ⚙️")

@dp.callback_query(lambda c: c.data == "today")
async def today_callback(callback: CallbackQuery):
    await callback.message.answer("Today's report coming soon 📅")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "week")
async def week_callback(callback: CallbackQuery):
    await callback.message.answer("Weekly report coming soon 📊")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "month")
async def month_callback(callback: CallbackQuery):
    await callback.message.answer("Monthly report coming soon 📈")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "all")
async def all_callback(callback: CallbackQuery):
    await callback.message.answer("All expenses report coming soon 📋")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "balance")
async def balance_callback(callback: CallbackQuery):
    await callback.message.answer("Balance report coming soon 💰")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "analytics")
async def analytics_callback(callback: CallbackQuery):
    await callback.message.answer("Analytics coming soon 📊")
    await callback.answer()

async def main():
    init_db()
    print('Database initialized...')
    print('Bot started...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())