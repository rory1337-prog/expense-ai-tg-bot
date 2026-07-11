from aiogram import Router
from aiogram.types import Message

from keyboards.buttons import b
from keyboards.edit_menu import build_edit_menu
from locales import t
from services.expense_service import ExpenseService
from services.settings_service import SettingsService

router = Router()


@router.message(
    lambda message: (
        message.text
        in [
            b("add_expense", "en"),
            b("add_expense", "ru"),
            b("add_expense", "pl"),
        ]
    )
)
async def add_expense_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(t("send_expense_example", lang))


@router.message(
    lambda message: (
        message.text
        in [
            b("edit", "en"),
            b("edit", "ru"),
            b("edit", "pl"),
        ]
    )
)
async def edit_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    entries = ExpenseService.get_user_entries(message.chat.id)

    if not entries:
        await message.answer(t("no_entries_to_edit", lang))
        return

    await message.answer(t("select_entry", lang), reply_markup=build_edit_menu(entries))
