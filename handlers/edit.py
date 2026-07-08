from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext

from services.expense_service import ExpenseService
from services.settings_service import SettingsService
from states.edit_states import EditEntry
from locales import t

router = Router()


@router.callback_query(lambda c: c.data.startswith("edit_select:"))
async def edit_select_callback(callback: CallbackQuery):
    entry_id = callback.data.split(":")[1]

    settings = SettingsService.get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    actions_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("edit", lang), callback_data=f"edit_entry:{entry_id}"),
                InlineKeyboardButton(text=t("delete", lang), callback_data=f"delete_entry:{entry_id}")
            ]
        ]
    )

    await callback.message.answer(
        f"{t('edit_entry_question', lang)} #{entry_id}?",
        reply_markup=actions_menu
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("delete_entry:"))
async def delete_entry_callback(callback: CallbackQuery):
    entry_id = int(callback.data.split(":")[1])

    deleted = ExpenseService.delete_entry_by_id(callback.message.chat.id, entry_id)
    settings = SettingsService.get_user_settings(callback.message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    if deleted:
        await callback.message.answer(
            f"{t('deleted', lang)}:\n{deleted['name']} — {deleted['amount']} {currency}"
        )
    else:
        await callback.message.answer(t("entry_not_found", lang))

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("edit_entry:"))
async def edit_entry_callback(callback: CallbackQuery, state: FSMContext):
    entry_id = int(callback.data.split(":")[1])

    settings = SettingsService.get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    await state.update_data(entry_id=entry_id)

    await callback.message.answer(t("send_new_value_example", lang))

    await state.set_state(EditEntry.waiting_for_new_value)
    await callback.answer()


@router.message(EditEntry.waiting_for_new_value)
async def process_new_entry_value(message: Message, state: FSMContext):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    parts = message.text.rsplit(" ", 1)

    if len(parts) != 2:
        await message.answer(t("wrong_edit_format", lang))
        return

    name = parts[0]
    amount_text = parts[1]

    try:
        amount = float(amount_text)
    except ValueError:
        await message.answer(t("amount_must_be_number", lang))
        return

    data = await state.get_data()
    entry_id = data["entry_id"]

    ok = ExpenseService.update_entry_by_id(message.chat.id, entry_id, name, amount)

    if ok:
        await message.answer(f"{t('updated', lang)}:\n{name} — {amount} {currency}")
    else:
        await message.answer(t("failed_update_entry", lang))

    await state.clear()