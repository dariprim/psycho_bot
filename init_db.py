from bot.models.db_models import Base, Category, ContentItem, StressType
from bot.services.db import engine
from sqlalchemy.orm import sessionmaker

def init_db():
    """Создание всех таблиц"""
    Base.metadata.create_all(engine)
    print("✅ Tables created.")

def populate_sample_data():
    """Заполнение тестовыми данными"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # === Категории ===
    categories = [
        Category(
            name="Книги",
            description="Книги по психологии и самопомощи",
            content_type="book",
            stress_types=["anxiety", "sadness", "stress"],
            sort_order=1
        ),
        Category(
            name="Игры",
            description="Расслабляющие игры для снятия стресса",
            content_type="game",
            stress_types=["anxiety", "stress", "fatigue"],
            sort_order=2
        ),
        Category(
            name="Техники",
            description="Дыхательные и медитативные практики",
            content_type="technique",
            stress_types=["anxiety", "stress", "anger"],
            sort_order=3
        ),
        Category(
            name="Упражнения",
            description="Практические упражнения для работы с эмоциями",
            content_type="exercise",
            stress_types=["sadness", "fatigue", "stress"],
            sort_order=4
        ),
    ]
    
    # === Контент ===
    content_items = [
        # Книги
        ContentItem(
            category_id=1,
            title="Как перестать беспокоиться и начать жить",
            author="Дейл Карнеги",
            description="Классическая книга по преодолению тревоги.",
            stress_type="anxiety",
            metadata={"author": "Дейл Карнеги", "year": 1948}
        ),
        ContentItem(
            category_id=1,
            title="Терапия настроения",
            author="Дэвид Бернс",
            description="Когнитивно-поведенческая терапия для борьбы с депрессией.",
            stress_type="sadness",
            metadata={"author": "Дэвид Бернс", "year": 1980}
        ),
        ContentItem(
            category_id=1,
            title="Медитация и осознанность",
            author="Энди Паддикомб",
            description="Практическое руководство по медитации для снижения стресса.",
            stress_type="stress",
            metadata={"author": "Энди Паддикомб", "year": 2015}
        ),
        # Игры
        ContentItem(
            category_id=2,
            title="Stardew Valley",
            description="Расслабляющая фермерская игра, помогающая отвлечься от тревог.",
            stress_type="anxiety",
            metadata={"platform": "PC, Mobile, Switch", "genre": "Simulation"}
        ),
        ContentItem(
            category_id=2,
            title="Journey",
            description="Красивая и успокаивающая игра с глубоким сюжетом.",
            stress_type="stress",
            metadata={"platform": "PS, PC", "genre": "Adventure"}
        ),
        ContentItem(
            category_id=2,
            title="Gris",
            description="Игра о преодолении печали через искусство.",
            stress_type="sadness",
            metadata={"platform": "PC, Switch", "genre": "Platformer"}
        ),
        # Техники
        ContentItem(
            category_id=3,
            title="Квадратное дыхание",
            description="Дыхательная техника для быстрого снятия тревоги.",
            stress_type="anxiety",
            content_text="1. Вдохните на 4 счёта\n2. Задержите дыхание на 4 счёта\n3. Выдохните на 4 счёта\n4. Задержите дыхание на 4 счёта\n\nПовторите 4-5 циклов."
        ),
        ContentItem(
            category_id=3,
            title="Техника заземления 5-4-3-2-1",
            description="Метод для возвращения в настоящий момент при панике.",
            stress_type="anxiety",
            content_text="Найдите:\n• 5 вещей, которые вы видите\n• 4 вещи, которые вы можете потрогать\n• 3 вещи, которые вы слышите\n• 2 вещи, которые вы можете понюхать\n• 1 вещь, которую вы можете попробовать на вкус"
        ),
        ContentItem(
            category_id=3,
            title="Прогрессивная мышечная релаксация",
            description="Последовательное напряжение и расслабление мышц.",
            stress_type="stress",
            content_text="1. Напрягите мышцы ног на 5 секунд\n2. Расслабьте\n3. Перейдите к мышцам бёдер\n4. Продолжайте вверх по телу до лица"
        ),
        # Упражнения
        ContentItem(
            category_id=4,
            title="Дневник эмоций",
            description="Запись и анализ своих эмоций в течение дня.",
            stress_type="sadness",
            content_text="Каждый вечер записывайте:\n1. Какое событие вызвало эмоцию\n2. Какую эмоцию вы почувствовали\n3. Как вы отреагировали\n4. Что можно было сделать иначе"
        ),
        ContentItem(
            category_id=4,
            title="Список благодарностей",
            description="Практика для повышения настроения.",
            stress_type="sadness",
            content_text="Каждый день записывайте 3-5 вещей, за которые вы благодарны. Это могут быть мелочи: вкусный кофе, улыбка прохожего, хорошая погода."
        ),
    ]
    
    session.add_all(categories)
    session.commit()
    print(f"✅ Added {len(categories)} categories")
    
    session.add_all(content_items)
    session.commit()
    print(f"✅ Added {len(content_items)} content items")
    
    session.close()
    print("✅ Sample data inserted.")

if __name__ == "__main__":
    init_db()
    populate_sample_data()