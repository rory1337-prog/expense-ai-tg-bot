import os
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Entry
from db.session import Base
from repositories import entries as entries_repository_module
from repositories.entries import EntryRepository


@pytest.fixture()
def test_session_factory(tmp_path, monkeypatch):
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if test_database_url:
        engine = create_engine(test_database_url)
    else:
        database_path = tmp_path / "analytics_test.db"
        engine = create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False},
        )

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(
        entries_repository_module,
        "SessionLocal",
        session_factory,
    )

    with session_factory() as session:
        session.query(Entry).delete()
        session.commit()

    yield session_factory

    with session_factory() as session:
        session.query(Entry).delete()
        session.commit()

    engine.dispose()


def add_entry(
    session_factory,
    *,
    chat_id: str,
    name: str,
    amount: float,
    category: str,
    entry_type: str = "expense",
    created_at: datetime | None = None,
):
    entry = Entry(
        chat_id=chat_id,
        name=name,
        amount=amount,
        category=category,
        type=entry_type,
        created_at=created_at or datetime.now(),
    )

    with session_factory() as session:
        session.add(entry)
        session.commit()
        session.refresh(entry)

    return entry


def test_category_spending_for_month(test_session_factory):
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Bus ticket",
        amount=10,
        category="Transport",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Taxi",
        amount=40,
        category="transport",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Lunch",
        amount=25,
        category="Food",
    )

    result = EntryRepository.get_category_spending_for_period(
        "user-1",
        "TRANSPORT",
        "month",
    )

    assert result == pytest.approx(50)


def test_category_spending_excludes_income(test_session_factory):
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Transport refund",
        amount=100,
        category="Transport",
        entry_type="income",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Taxi",
        amount=30,
        category="Transport",
    )

    result = EntryRepository.get_category_spending_for_period(
        "user-1",
        "Transport",
        "month",
    )

    assert result == pytest.approx(30)


def test_top_category_for_month(test_session_factory):
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Groceries",
        amount=120,
        category="Food",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Restaurant",
        amount=80,
        category="Food",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Taxi",
        amount=50,
        category="Transport",
    )

    result = EntryRepository.get_top_category_for_period(
        "user-1",
        "month",
    )

    assert result is not None
    assert result.category == "Food"
    assert result.total == pytest.approx(200)


def test_biggest_expenses_are_sorted_and_limited(test_session_factory):
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Coffee",
        amount=15,
        category="Food",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Hotel",
        amount=500,
        category="Travel",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Taxi",
        amount=70,
        category="Transport",
    )

    result = EntryRepository.get_biggest_expenses_for_period(
        "user-1",
        "month",
        limit=2,
    )

    assert len(result) == 2
    assert [entry.name for entry in result] == ["Hotel", "Taxi"]
    assert [entry.amount for entry in result] == [500, 70]


def test_analytics_are_isolated_between_users(test_session_factory):
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="User one taxi",
        amount=40,
        category="Transport",
    )
    add_entry(
        test_session_factory,
        chat_id="user-2",
        name="User two taxi",
        amount=900,
        category="Transport",
    )

    category_total = EntryRepository.get_category_spending_for_period(
        "user-1",
        "Transport",
        "month",
    )
    biggest = EntryRepository.get_biggest_expenses_for_period(
        "user-1",
        "month",
    )

    assert category_total == pytest.approx(40)
    assert len(biggest) == 1
    assert biggest[0].name == "User one taxi"


def test_entries_outside_period_are_excluded(test_session_factory):
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Current expense",
        amount=50,
        category="Food",
    )
    add_entry(
        test_session_factory,
        chat_id="user-1",
        name="Old expense",
        amount=500,
        category="Food",
        created_at=datetime.now() - timedelta(days=60),
    )

    result = EntryRepository.get_category_spending_for_period(
        "user-1",
        "Food",
        "month",
    )

    assert result == pytest.approx(50)


def test_empty_database_returns_safe_values(test_session_factory):
    category_total = EntryRepository.get_category_spending_for_period(
        "user-1",
        "Food",
        "month",
    )
    top_category = EntryRepository.get_top_category_for_period(
        "user-1",
        "month",
    )
    biggest = EntryRepository.get_biggest_expenses_for_period(
        "user-1",
        "month",
    )

    assert category_total == 0
    assert top_category is None
    assert biggest == []


def test_invalid_period_returns_safe_values(test_session_factory):
    category_total = EntryRepository.get_category_spending_for_period(
        "user-1",
        "Food",
        "invalid",
    )
    top_category = EntryRepository.get_top_category_for_period(
        "user-1",
        "invalid",
    )
    biggest = EntryRepository.get_biggest_expenses_for_period(
        "user-1",
        "invalid",
    )

    assert category_total == 0
    assert top_category is None
    assert biggest == []
