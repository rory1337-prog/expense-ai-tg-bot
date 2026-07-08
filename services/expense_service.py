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
        return entry
    
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

        return updated_entry
    
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
        return EntryRepository.get_user_entries(str(chat_id))