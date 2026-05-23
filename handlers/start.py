from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import main_menu

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "💸 ExpensesAI\n\nChoose an action:",
        reply_markup=main_menu
    )