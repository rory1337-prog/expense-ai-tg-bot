from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext  

from database import delete_entry_by_id
from database import update_entry_by_id
from states.edit_states import EditEntry

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
async def edit_entry_callback(callback: CallbackQuery, state: FSMContext):
    entry_id = int(callback.data.split(":")[1])

    await state.update_data(entry_id=entry_id)

    await callback.message.answer(
        "✏️ Send new value like:\ncoffee 20"
    )

    await state.set_state(EditEntry.waiting_for_new_value)
    await callback.answer()


@router.message(EditEntry.waiting_for_new_value)
async def process_new_entry_value(message: Message, state: FSMContext):
    parts = message.text.rsplit(" ", 1)

    if len(parts) != 2:
        await message.answer("Wrong format. Try: coffee 20")
        return

    name = parts[0]
    amount_text = parts[1]

    try:
        amount = float(amount_text)
    except ValueError:
        await message.answer("Amount must be a number. Try: coffee 20")
        return

    data = await state.get_data()
    entry_id = data["entry_id"]
    print("FSM EDIT TRIGGERED")
    print("message:", message.text)
    print("entry_id:", entry_id)

    ok = update_entry_by_id(message.chat.id, entry_id, name, amount)
    print("update ok:", ok)

    if ok:
        await message.answer(f"✅ Updated:\n{name} — {amount} PLN")
    else:
        await message.answer("❌ Failed to update entry.")

    await state.clear()