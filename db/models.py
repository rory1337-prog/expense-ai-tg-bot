from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.session import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    chat_id: Mapped[str] = mapped_column(String, primary_key=True)
    language: Mapped[str] = mapped_column(String, default="en")
    currency: Mapped[str] = mapped_column(String, default="PLN")
