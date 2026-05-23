from aiogram import Router
from aiogram.types import Message

from database import save_entry
from parser import parse_expense, parse_income

router = Router()

@router.message(lambda message: message.text and message.text.startswith('income '))
async def income_handler(message: Message):
    entry = parse_income(message.text)

    if not entry:
        await message.answer("Could not parse income. Try: income salary 3000")
        return
    
    ok = save_entry(entry, message.chat.id)

    if ok:
        await message.answer(
            f"✅ Income saved:\n{entry['name']} — {entry['amount']} PLN"
        )
    else:
        await message.answer("❌ Failed to save income.")

@router.message(
    lambda message:
    message.text
    and not message.text.startswith('/')
    and message.text not in [
        "➕ Add expense",
        "📊 Reports",
        "✏️ Edit",
        "⚙️ Settings"
    ]
)
async def expense_text_handler(message: Message):
    entry = parse_expense(message.text)

    if not entry:
        await message.answer("Could not parse expense. Try: coffee 15")
        return
    
    ok = save_entry(entry, message.chat.id)

    if ok:
        await message.answer(
            f"✅ Expense saved:\n{entry['name']} — {entry['amount']} PLN\nCategory: {entry['category']}"
        )
    else:
        await message.answer("❌ Failed to save expense.")
        