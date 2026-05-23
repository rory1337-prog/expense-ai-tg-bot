# ===== IMPORTS =====
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message 
from dotenv import load_dotenv
from database import init_db
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()

BOT_TOKEN = os.getenv('BOTTOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Add expense")],
        [KeyboardButton(text="📊 Reports"), KeyboardButton(text="✏️ Edit")],
        [KeyboardButton(text="⚙️ Settings")]
    ],
    resize_keyboard=True
)

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
    await message.answer("Reports menu coming soon 📊")


@dp.message(lambda message: message.text == "✏️ Edit")
async def edit_handler(message: Message):
    await message.answer("Edit menu coming soon ✏️")


@dp.message(lambda message: message.text == "⚙️ Settings")
async def settings_handler(message: Message):
    await message.answer("Settings menu coming soon ⚙️")

async def main():
    init_db()
    print('Database initialized...')
    print('Bot started...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())