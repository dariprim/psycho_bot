import pytest
from bot.services.db import get_random_book, get_random_game
from bot.models.db_models import Book

def test_get_random_book_with_stress_type(db_session):
    book1 = Book(title="Test1", author="A", description="Desc", stress_type="anxiety")
    book2 = Book(title="Test2", author="B", description="Desc", stress_type="stress")
    db_session.add_all([book1, book2])
    db_session.commit()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('bot.services.db.SessionLocal', lambda: db_session)
        result = get_random_book(stress_type="anxiety")
        assert result is not None
        assert result.stress_type == "anxiety"

def test_get_random_game_no_result(db_session):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('bot.services.db.SessionLocal', lambda: db_session)
        result = get_random_game(stress_type="nonexistent")
        assert result is None