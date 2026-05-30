from aiogram import Router, F
from aiogram.types import Message

from ai import ai_parse_question
from database import (
    get_total_spending,
    get_top_category,
    get_category_spending,
    get_user_settings,
)
from locales import t 

router = Router()


async def handle_finance_question(message: Message, question: str):
    result = await ai_parse_question(question)
    lang = result["language"]
    settings = get_user_settings(message.chat.id)
    currency = settings["currency"]

    if result["intent"] == "total_spending":
        total = get_total_spending(message.chat.id, result["period"])
        text = t("spent_period", lang).format(
            total=f"{total:.2f}", currency=currency, period=result["period"]
        )

    elif result["intent"] == "top_category":
        top = get_top_category(message.chat.id, result["period"])
        if not top:
            text = t("no_expenses_period", lang)
        else:
            text = t("top_category_period", lang).format(
                period=result["period"],
                category=top["category"],
                total=f"{top['total']:.2f}",
                currency=currency
            )

    elif result['intent'] == 'category_spending':
        category = result.get('category')

        if not category:
            text = t('unknown_question', lang)
        else:
            total = get_category_spending(
                message.chat.id,
                category,
                result['period']
            )

            text = (
                f'You spent {total:.2f} {currency}'
                f'on {category} during {result['period']}.'
            )
    else:
        text = t("unknown_question", lang)

    await message.answer(text)


@router.message(F.text.startswith("/ask"))
async def ask_handler(message: Message):
    question = message.text.replace("/ask", "").strip()

    if not question:
        await message.answer("Ask a finance question.")
        return

    await handle_finance_question(message, question)