from bot.models.db_models import Base, Book, Game
from bot.services.db import engine
from sqlalchemy.orm import sessionmaker

def init_db():
    Base.metadata.create_all(engine)
    print("Tables created.")

def populate_sample_data():
    Session = sessionmaker(bind=engine)
    session = Session()
    books = [
        Book(title="Как перестать беспокоиться и начать жить", author="Дейл Карнеги",
             description="Классическая книга по преодолению тревоги.", stress_type="anxiety"),
        Book(title="Терапия настроения", author="Дэвид Бернс",
             description="Когнитивно-поведенческая терапия для борьбы с депрессией.", stress_type="sadness"),
        Book(title="Медитация и осознанность", author="Энди Паддикомб",
             description="Практическое руководство по медитации для снижения стресса.", stress_type="stress"),
    ]
    games = [
        Game(name="Stardew Valley", platform="PC, Mobile, Switch",
             description="Расслабляющая фермерская игра, помогающая отвлечься от тревог.", stress_type="anxiety"),
        Game(name="Journey", platform="PS, PC",
             description="Красивая и успокаивающая игра с глубоким сюжетом.", stress_type="stress"),
        Game(name="Gris", platform="PC, Switch",
             description="Игра о преодолении печали через искусство.", stress_type="sadness"),
    ]
    session.add_all(books + games)
    session.commit()
    print("Sample data inserted.")

if __name__ == "__main__":
    init_db()
    populate_sample_data()