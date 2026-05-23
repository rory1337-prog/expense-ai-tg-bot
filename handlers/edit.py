from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import delete_entry_by_id

router = Router()

@router.callback_query(lambda c: c.data.startswith("edit_select:"))
async def edit_select_callback(callback: CallbackQuery):
    entry_id = callback.data.split(":")[1]

    actions_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_entry:{entry_id}"),
                InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete_entry:{entry_id}")
            ]
        ]
    )

    await callback.message.answer(
        f"What do you want to do with entry #{entry_id}?",
        reply_markup=actions_menu
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("delete_entry:"))
async def delete_entry_callback(callback: CallbackQuery):
    entry_id = int(callback.data.split(":")[1])

    deleted = delete_entry_by_id(callback.message.chat.id, entry_id)

    if deleted:
        await callback.message.answer(
            f"🗑 Deleted:\n{deleted['name']} — {deleted['amount']} PLN"
        )
    else:
        await callback.message.answer("❌ Entry not found.")

    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("edit_entry:"))
async def edit_entry_callback(callback: CallbackQuery):
    entry_id = callback.data.split(":")[1]

    await callback.message.answer(
        f"✏️ Edit flow for entry #{entry_id} coming next."
    )
    await callback.answer()