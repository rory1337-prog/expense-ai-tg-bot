from aiogram.fsm.state import State, StatesGroup


class EditEntry(StatesGroup):
    waiting_for_new_value = State()
