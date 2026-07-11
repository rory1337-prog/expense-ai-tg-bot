from sqlalchemy import select, func, case
from datetime import datetime, time, timedelta
from db.models import Entry
from db.session import SessionLocal

class EntryRepository:
    @staticmethod
    def get_user_entries(chat_id: str):
        with SessionLocal() as session:
            stmt = (
                select(Entry)
                .where(Entry.chat_id == str(chat_id))
                .order_by(Entry.id.desc())
            )
            return session.execute(stmt).scalars().all()
        
    @staticmethod
    def get_by_id(chat_id: str, entry_id: int):
        with SessionLocal() as session:
            stmt = select(Entry).where(
                Entry.chat_id == str(chat_id),
                Entry.id == entry_id,
            )
            return session.execute(stmt).scalar_one_or_none()
        
    @staticmethod
    def save(entry: Entry):
        with SessionLocal() as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)

            return entry
        
    @staticmethod
    def delete(entry: Entry):
        with SessionLocal() as session:
            managed = session.merge(entry)
            session.delete(managed)
            session.commit()

    @staticmethod
    def update(entry: Entry):
        with SessionLocal() as session:
            managed = session.merge(entry)
            session.commit()
            session.refresh(managed)
            return managed
        
    @staticmethod
    def get_balance_data(chat_id: str):
        with SessionLocal() as session:
            stmt = select(
                func.sum(case((Entry.type == "income", Entry.amount), else_=0)),
                func.sum(case((Entry.type == "expense", Entry.amount), else_=0)),
            ).where(Entry.chat_id == str(chat_id))

            income_total, expense_total = session.execute(stmt).one()

            return {
                "income_total": income_total or 0,
                "expense_total": expense_total or 0,
            }

    @staticmethod
    def get_expense_sum_from_date(chat_id: str, start_date: str):
        with SessionLocal() as session:
            stmt = select(func.sum(Entry.amount)).where(
                Entry.chat_id == str(chat_id),
                Entry.type == "expense",
                Entry.created_at >= start_date,
            )

            return session.execute(stmt).scalar() or 0
        
    @staticmethod
    def get_expense_sum_by_date(chat_id: str, date_value: str):
        with SessionLocal() as session:
            stmt = select(func.sum(Entry.amount)).where(
                Entry.chat_id == str(chat_id),
                Entry.type == "expense",
                func.date(Entry.created_at) == date_value,
            )

            return session.execute(stmt).scalar() or 0
        
    @staticmethod
    def get_top_categories(chat_id: str, limit: int = 3):
        with SessionLocal() as session:
            stmt = (
                select(Entry.category, func.sum(Entry.amount).label("total"))
                .where(
                    Entry.chat_id == str(chat_id),
                    Entry.type == "expense",
                )
                .group_by(Entry.category)
                .order_by(func.sum(Entry.amount).desc())
                .limit(limit)
            )

            return session.execute(stmt).all()
        
    @staticmethod
    def get_last_expenses(chat_id: str, limit: int = 5):
        with SessionLocal() as session:
            stmt = (
                select(Entry.name, Entry.amount)
                .where(
                    Entry.chat_id == str(chat_id),
                    Entry.type == "expense",
                )
                .order_by(Entry.id.desc())
                .limit(limit)
            )

            return session.execute(stmt).all()
        
    @staticmethod
    def _get_period_bounds(period: str):
        now = datetime.now()
        today = now.date()

        if period == "today":
            start = datetime.combine(today, time.min)
            end = start + timedelta(days=1)

        elif period == "week":
            start = datetime.combine(today - timedelta(days=6), time.min)
            end = datetime.combine(today + timedelta(days=1), time.min)

        elif period == "month":
            start = datetime.combine(today.replace(day=1), time.min)

            if today.month == 12:
                next_month = today.replace(
                    year=today.year + 1,
                    month=1,
                    day=1,
                )
            else:
                next_month = today.replace(
                    month=today.month + 1,
                    day=1,
                )

            end = datetime.combine(next_month, time.min)

        else:
            return None

        return start, end

    @staticmethod
    def get_expenses_for_period(chat_id: str, period: str):
        bounds = EntryRepository._get_period_bounds(period)

        if bounds is None:
            return []

        start, end = bounds

        with SessionLocal() as session:
            stmt = (
                select(Entry)
                .where(
                    Entry.chat_id == str(chat_id),
                    Entry.type == "expense",
                    Entry.created_at >= start,
                    Entry.created_at < end,
                )
                .order_by(Entry.id.desc())
            )

            return session.execute(stmt).scalars().all()

    @staticmethod
    def get_expense_sum_for_period(chat_id: str, period: str):
        bounds = EntryRepository._get_period_bounds(period)

        if bounds is None:
            return 0

        start, end = bounds

        with SessionLocal() as session:
            stmt = select(func.sum(Entry.amount)).where(
                Entry.chat_id == str(chat_id),
                Entry.type == "expense",
                Entry.created_at >= start,
                Entry.created_at < end,
            )

            return session.execute(stmt).scalar() or 0