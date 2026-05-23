from aiogram import Router 
from aiogram.types import Message

router = Router()

@router.message(lambda message: message.text == "➕ Add expense")
async def add_expense_handler(message: Message):
    await message.answer("Send expense like:\ncoffee 15")

@router.message(lambda message: message.text == "✏️ Edit")
async def edit_handler(message: Message):
    await message.answer("Edit menu coming soon ✏️")

@router.message(lambda message: message.text == "⚙️ Settings")
async def settings_handler(message: Message):
    await message.answer("Settings menu coming soon ⚙️")