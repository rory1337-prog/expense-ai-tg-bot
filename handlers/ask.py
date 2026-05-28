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
        lang = result["language"]
        currency = settings["currency"]

        if lang == "ru":
            text = f"Ты потратил {total:.2f} {currency} за период: {result['period']}."
        elif lang == "pl":
            text = f"Wydałeś {total:.2f} {currency} za okres: {result['period']}."
        else:
            text = f"You spent {total:.2f} {currency} this {result['period']}."

        await message.answer(text)

        return
    
    if result["intent"] == "top_category":
        top = get_top_category(
            message.chat.id,
            result["period"]
        )

        settings = get_user_settings(message.chat.id)
        lang = result["language"]
        currency = settings["currency"]

        if not top:
            await message.answer("No expenses found for this period.")
            return

        if lang == "ru":
            text = (
                f"Твоя топ категория за период {result['period']}: "
                f"{top['category']} ({top['total']:.2f} {currency})."
            )
        elif lang == "pl":
            text = (
                f"Twoja top kategoria za okres {result['period']} to "
                f"{top['category']} ({top['total']:.2f} {currency})."
            )
        else:
            text = (
                f"Your top category this {result['period']} is "
                f"{top['category']} ({top['total']:.2f} {currency})."
            )

        await message.answer(text)

        return

    await message.answer("I couldn't understand this finance question yet.")


@router.message(F.text.startswith("/ask"))
async def ask_handler(message: Message):
    question = message.text.replace("/ask", "").strip()

    if not question:
        await message.answer("Ask a finance question.")
        return

    await handle_finance_question(message, question)