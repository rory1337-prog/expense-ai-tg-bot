from aiogram import Router
from aiogram.types import Message

from ai import ai_classify_message
from handlers.ask import handle_finance_question
from keyboards.buttons import b
from locales import t
from locales.categories import localize_category
from parser import parse_expense, parse_income
from services.expense_service import ExpenseService
from services.settings_service import SettingsService

router = Router()


@router.message(
    lambda message: (
        message.text
        and message.text.lower().strip().split()[0]
        in [
            "income",
            "salary",
            "зарплата",
            "зп",
            "доход",
            "pensja",
            "przychod",
            "przychód",
        ]
    )
)
async def income_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    if message.text.lower().strip() in [
        "income",
        "salary",
        "зарплата",
        "зп",
        "доход",
        "pensja",
        "przychod",
        "przychód",
    ]:
        await message.answer(t("send_income_example", lang))
        return

    entry = parse_income(message.text)

    if not entry:
        await message.answer(t("failed_parse_income", lang))
        return

    ok = ExpenseService.save_entry(entry, message.chat.id)

    if ok:
        await message.answer(
            f"{t('income_saved', lang)}:\n"
            f"{entry['name']} — {entry['amount']} {currency}"
        )
    else:
        await message.answer(t("failed_save_income", lang))


@router.message(
    lambda message: (
        message.text
        and not message.text.startswith("/")
        and message.text.lower().strip().split()[0]
        not in [
            "income",
            "salary",
            "зарплата",
            "зп",
            "доход",
            "pensja",
            "przychod",
            "przychód",
        ]
        and message.text
        not in [
            b("add_expense", "en"),
            b("add_expense", "ru"),
            b("add_expense", "pl"),
            b("reports", "en"),
            b("reports", "ru"),
            b("reports", "pl"),
            b("edit", "en"),
            b("edit", "ru"),
            b("edit", "pl"),
            b("settings", "en"),
            b("settings", "ru"),
            b("settings", "pl"),
        ]
    )
)
async def expense_text_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    entry = parse_expense(message.text)

    if entry:
        ok = ExpenseService.save_entry(entry, message.chat.id)

        if ok:
            await message.answer(
                f"{t('expense_saved', lang)}:\n"
                f"{entry['name']} — {entry['amount']} {currency}\n"
                f"{t('category', lang)}: {localize_category(entry['category'], lang)}"
            )
        else:
            await message.answer(t("failed_save_expense", lang))

        return

    message_type = await ai_classify_message(message.text)

    if message_type == "question":
        await handle_finance_question(message, message.text)
        return

    if message_type == "income":
        await income_handler(message)
        return

    await message.answer(t("failed_parse_expense", lang))
