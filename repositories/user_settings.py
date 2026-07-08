from sqlalchemy import select
from db.models import UserSettings
from db.session import SessionLocal

class UserSettingsRepository:
    @staticmethod
    def get_by_chat_id(chat_id: str):
        with SessionLocal() as session:
            stmt = select(UserSettings).where(UserSettings.chat_id == str(chat_id))
            return session.execute(stmt).scalar_one_or_none()
        
    @staticmethod
    def create(chat_id: str, language: str = "en", currency: str = "PLN"):
        with SessionLocal() as session:
            settings = UserSettings(
                chat_id=str(chat_id),
                language=language,
                currency=currency,
            )
            session.add(settings)
            session.commit()
            session.refresh(settings)
            return settings
        
    @staticmethod
    def update(settings: UserSettings):
        with SessionLocal() as session:
            managed = session.merge(settings)
            session.commit()
            session.refresh(managed)
            return managed