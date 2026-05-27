from aiogram import Router, F
from aiogram.types import Message

from ai import ai_parse_question
from database import get_total_spending, get_top_category, get_user_settings

router = Router()


async def handle_finance_question(message: Message, question: str):
    result = await ai_parse_question(question)

    if result["intent"] == "total_spending":
        total = get_total_spending(
            message.chat.id,
            result["period"]
        )

        settings = get_user_settings(message.chat.id)
        currency = settings["currency"]

        await message.answer(
            f"You spent {total:.2f} {currency} this {result['period']}."
        )

        return
    
    if result["intent"] == "top_category":
        top = get_top_category(
            message.chat.id,
            result["period"]
        )

        settings = get_user_settings(message.chat.id)
        currency = settings["currency"]

        if not top:
            await message.answer("No expenses found for this period.")
            return

        await message.answer(
            f"Your top category this {result['period']} is "
            f"{top['category']} ({top['total']:.2f} {currency})."
        )

        return

    await message.answer("I couldn't understand this finance question yet.")


@router.message(F.text.startswith("/ask"))
async def ask_handler(message: Message):
    question = message.text.replace("/ask", "").strip()

    if not question:
        await message.answer("Ask a finance question.")
        return

    await handle_finance_question(message, question)