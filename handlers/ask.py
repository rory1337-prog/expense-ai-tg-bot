from aiogram import F, Router
from aiogram.types import Message

from ai import ai_parse_question
from locales import t
from services.analytics_service import AnalyticsService
from services.settings_service import SettingsService

router = Router()


async def handle_finance_question(message: Message, question: str):
    result = await ai_parse_question(question)
    lang = result["language"]
    settings = SettingsService.get_user_settings(message.chat.id)
    currency = settings["currency"]

    if result["intent"] == "total_spending":
        total = AnalyticsService.get_total_spending(message.chat.id, result["period"])
        text = t("spent_period", lang).format(
            total=f"{total:.2f}", currency=currency, period=result["period"]
        )

    elif result["intent"] == "top_category":
        top = AnalyticsService.get_top_category(message.chat.id, result["period"])
        if not top:
            text = t("no_expenses_period", lang)
        else:
            text = t("top_category_period", lang).format(
                period=result["period"],
                category=top["category"],
                total=f"{top['total']:.2f}",
                currency=currency,
            )

    elif result["intent"] == "category_spending":
        category = result.get("category")

        if not category:
            text = t("unknown_question", lang)
        else:
            total = AnalyticsService.get_category_spending(
                message.chat.id, category, result["period"]
            )

            text = (
                f"You spent {total:.2f} {currency}"
                f"on {category} during {result['period']}."
            )

    elif result["intent"] == "biggest_expenses":
        expenses = AnalyticsService.get_biggest_expenses(
            message.chat.id, result["period"]
        )
        if not expenses:
            text = t("no_expenses_period", lang)
        else:
            lines = [
                (
                    f"{i}. {item['name']} — "
                    f"{item['amount']:.2f} "
                    f"{currency} "
                    f"({item['category']})"
                )
                for i, item in enumerate(expenses, start=1)
            ]
            text = f"Biggest expenses during {result['period']}:\n\n" + "\n".join(lines)

    elif result["intent"] == "average_daily_spending":
        average = AnalyticsService.get_average_daily_spending(
            message.chat.id, result["period"]
        )
        text = (
            f"Your average daily spending during "
            f"{result['period']} is "
            f"{average:.2f} {currency}."
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
