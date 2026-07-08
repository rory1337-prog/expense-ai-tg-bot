# ===== IMPORTS =====
import logging
from db.session import Base, engine
from services.expense_service import ExpenseService
from services.settings_service import SettingsService

logger = logging.getLogger(__name__)

# ===== DATABASE INIT =====
def init_db():
    Base.metadata.create_all(bind=engine)

# ===== SAVE OPERATIONS =====
def save_entry(entry, chat_id):
    try:
        return ExpenseService.save_entry(entry, chat_id)

    except Exception:
        logger.exception("Failed to save entry")
        return False
    
# ===== GET OPERATIONS =====
def get_user_entries(chat_id):
    return ExpenseService.get_user_entries(chat_id)

# ===== DELETE OPERATIONS =====
def delete_entry_by_id(chat_id, entry_id):
    return ExpenseService.delete_entry_by_id(chat_id, entry_id)


def delete_entry_by_number(chat_id, number):
    return ExpenseService.delete_entry_by_number(chat_id, number)


# ===== UPDATE OPERATIONS =====
def update_entry_by_number(chat_id, number, name, amount):
    return ExpenseService.update_entry_by_number(chat_id, number, name, amount)

def update_entry_by_id(chat_id, entry_id, name, amount):
    return ExpenseService.update_entry_by_id(
        chat_id,
        entry_id,
        name,
        amount,
    )


def get_user_settings(chat_id):
    return SettingsService.get_user_settings(chat_id)


def set_user_language(chat_id, language):
    SettingsService.set_user_language(chat_id, language)



def set_user_currency(chat_id, currency):
    SettingsService.set_user_currency(chat_id, currency)


def ensure_user_settings(chat_id, language="en", currency="PLN"):
    SettingsService.ensure_user_settings(chat_id, language, currency)

