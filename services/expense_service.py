from repositories.entries import EntryRepository
from parser import detect_category
from db.models import Entry

class ExpenseService:
    @staticmethod
    def delete_entry_by_number(chat_id, number):
        entries = EntryRepository.get_user_entries(str(chat_id))
        expense_items = [
            e for e in entries
            if e.type == "expense"
        ]
        if number < 1 or number > len(expense_items):
            return None
        entry = expense_items[number - 1]
        EntryRepository.delete(entry)
        return ExpenseService._entry_to_dict(entry)
    
    @staticmethod
    def update_entry_by_number(chat_id, number, name, amount):
        entries = EntryRepository.get_user_entries(str(chat_id))

        expense_items = [
            e for e in entries
            if e.type == "expense"
        ]

        if number < 1 or number > len(expense_items):
            return None

        entry = expense_items[number - 1]

        entry.name = name
        entry.amount = amount
        entry.category = detect_category(name)

        updated_entry = EntryRepository.update(entry)

        return {
            "name": updated_entry.name,
            "amount": updated_entry.amount,
            "category": updated_entry.category,
        }
    
    @staticmethod
    def save_entry(entry_data, chat_id):
        db_entry = Entry(
            chat_id=str(chat_id),
            name=entry_data["name"],
            amount=entry_data["amount"],
            category=entry_data["category"],
            type=entry_data["type"],
            created_at=entry_data["created_at"],
        )

        EntryRepository.save(db_entry)

        return True
    
    @staticmethod
    def get_user_entries(chat_id):
        entries = EntryRepository.get_user_entries(str(chat_id))
        return [ExpenseService._entry_to_dict(entry) for entry in entries]
    
    @staticmethod
    def _entry_to_dict(entry):
        return {
            "id": entry.id,
            "name": entry.name,
            "amount": entry.amount,
            "category": entry.category,
            "type": entry.type,
            "created_at": entry.created_at,
        }
    
    @staticmethod
    def delete_entry_by_id(chat_id, entry_id):
        entry = EntryRepository.get_by_id(str(chat_id), entry_id)

        if not entry:
            return None

        deleted_entry = ExpenseService._entry_to_dict(entry)

        EntryRepository.delete(entry)

        return deleted_entry
    
    @staticmethod
    def update_entry_by_id(chat_id, entry_id, name, amount):
        entry = EntryRepository.get_by_id(str(chat_id), entry_id)

        if not entry:
            return False

        entry.name = name
        entry.amount = amount
        entry.category = detect_category(name)

        EntryRepository.update(entry)

        return True
    