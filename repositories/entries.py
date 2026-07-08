from sqlalchemy import select
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

