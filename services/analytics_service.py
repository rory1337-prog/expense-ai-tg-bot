from datetime import datetime

from repositories.entries import EntryRepository


class AnalyticsService:
    @staticmethod
    def get_balance_data(chat_id):
        data = EntryRepository.get_balance_data(str(chat_id))
        income_total = data["income_total"]
        expense_total = data["expense_total"]

        return {
            "income_total": income_total,
            "expense_total": expense_total,
            "balance": income_total - expense_total,
        }

    @staticmethod
    def get_today_expense(chat_id):
        today = datetime.now().date().isoformat()
        return EntryRepository.get_expense_sum_by_date(str(chat_id), today)

    @staticmethod
    def get_month_expense(chat_id):
        month_start = datetime.now().strftime("%Y-%m-01")
        return EntryRepository.get_expense_sum_from_date(str(chat_id), month_start)

    @staticmethod
    def get_top_categories(chat_id, limit=3):
        return EntryRepository.get_top_categories(str(chat_id), limit)

    @staticmethod
    def get_last_expenses(chat_id, limit=5):
        return EntryRepository.get_last_expenses(str(chat_id), limit)
    
    @staticmethod
    def get_expenses_for_period(chat_id, period):
        entries = EntryRepository.get_expenses_for_period(str(chat_id), period)

        return [
            {
                "id": entry.id,
                "name": entry.name,
                "amount": entry.amount,
                "category": entry.category,
                "created_at": entry.created_at,
            }
            for entry in entries
        ]