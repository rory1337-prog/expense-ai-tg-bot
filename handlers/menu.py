from aiogram import Router 
from aiogram.types import Message
from database import get_user_entries
from keyboards.edit_menu import build_edit_menu

router = Router()

@router.message(lambda message: message.text == "➕ Add expense")
async def add_expense_handler(message: Message):
    await message.answer("Send expense like:\ncoffee 15")

@router.message(lambda message: message.text == '✏️ Edit')
async def edit_handler(message: Message):
    entries = get_user_entries(message.chat.id)

    if not entries:
        await message.answer("No entries to edit yet.")
        return
    
    await message.answer(
        "✏️ Select entry:",
        reply_markup=build_edit_menu(entries)
    )


