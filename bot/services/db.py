import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models.db_models import Book, Game
from bot.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_random_book(stress_type: str = None):
    session = SessionLocal()
    try:
        query = session.query(Book)
        if stress_type:
            query = query.filter(Book.stress_type == stress_type)
        count = query.count()
        if count == 0:
            return None
        random_index = random.randint(0, count - 1)
        return query.offset(random_index).first()
    finally:
        session.close()

def get_random_game(stress_type: str = None):
    session = SessionLocal()
    try:
        query = session.query(Game)
        if stress_type:
            query = query.filter(Game.stress_type == stress_type)
        count = query.count()
        if count == 0:
            return None
        random_index = random.randint(0, count - 1)
        return query.offset(random_index).first()
    finally:
        session.close()