import random
from typing import List, Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from bot.models.db_models import User, Category, ContentItem, Feedback, StressType, Base
from bot.config import DATABASE_URL

# Создаём движок с поддержкой JSON
engine = create_engine(
    DATABASE_URL,
    json_serializer=lambda obj: obj,  # Для SQLite совместимости
    echo=False  # Логирование SQL-запросов (включить для отладки)
)

SessionLocal = sessionmaker(bind=engine)


# ============================================
# Пользователи
# ============================================

def get_or_create_user(telegram_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None) -> User:
    """Получить или создать пользователя"""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            session.commit()
        return user
    finally:
        session.close()


def update_user_interaction(user_id: int):
    """Обновить статистику взаимодействий пользователя"""
    session = SessionLocal()
    try:
        from datetime import datetime
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.total_interactions += 1
            user.last_interaction = datetime.utcnow()
            session.commit()
    finally:
        session.close()


def update_user_mood(user_id: int, mood: str, stress_type: str = None):
    """Обновить историю настроений пользователя"""
    session = SessionLocal()
    try:
        from datetime import datetime
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            if user.mood_history is None:
                user.mood_history = []
            
            # Добавляем запись о настроении
            user.mood_history.append({
                "mood": mood,
                "stress_type": stress_type,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Храним только последние 100 записей
            user.mood_history = user.mood_history[-100:]
            session.commit()
    finally:
        session.close()


# ============================================
# Категории
# ============================================

def get_all_categories() -> List[Category]:
    """Получить все активные категории"""
    session = SessionLocal()
    try:
        categories = session.query(Category).filter(
            Category.is_active == 1
        ).order_by(Category.sort_order).all()
        return categories
    finally:
        session.close()


def get_category_by_id(category_id: int) -> Optional[Category]:
    """Получить категорию по ID"""
    session = SessionLocal()
    try:
        return session.query(Category).filter(
            Category.id == category_id,
            Category.is_active == 1
        ).first()
    finally:
        session.close()


# ============================================
# Контент
# ============================================

def get_content_items(category_id: int = None, 
                      stress_type: str = None,
                      limit: int = 10) -> List[ContentItem]:
    """Получить контент с фильтрацией"""
    session = SessionLocal()
    try:
        query = session.query(ContentItem).filter(ContentItem.is_active == 1)
        
        if category_id:
            query = query.filter(ContentItem.category_id == category_id)
        if stress_type:
            query = query.filter(ContentItem.stress_type == stress_type)
        
        return query.order_by(ContentItem.created_at.desc()).limit(limit).all()
    finally:
        session.close()


def get_random_content(stress_type: str = None, 
                       content_type: str = None) -> Optional[ContentItem]:
    """Получить случайный контент"""
    session = SessionLocal()
    try:
        query = session.query(ContentItem).filter(ContentItem.is_active == 1)
        
        if stress_type:
            query = query.filter(ContentItem.stress_type == stress_type)
        if content_type:
            query = query.filter(
                ContentItem.meta_data['content_type'].astext == content_type
            )
        
        count = query.count()
        if count == 0:
            return None
        
        random_index = random.randint(0, count - 1)
        return query.offset(random_index).first()
    finally:
        session.close()


def get_content_by_id(content_id: int) -> Optional[ContentItem]:
    """Получить контент по ID"""
    session = SessionLocal()
    try:
        return session.query(ContentItem).filter(
            ContentItem.id == content_id,
            ContentItem.is_active == 1
        ).first()
    finally:
        session.close()


def increment_usage_count(content_id: int):
    """Увеличить счётчик использования контента"""
    session = SessionLocal()
    try:
        content = session.query(ContentItem).filter(ContentItem.id == content_id).first()
        if content:
            content.usage_count += 1
            session.commit()
    finally:
        session.close()


# ============================================
# Обратная связь
# ============================================

def add_feedback(user_id: int, content_item_id: int, 
                 is_positive: bool, comment: str = None):
    """Добавить отзыв о контенте"""
    session = SessionLocal()
    try:
        feedback = Feedback(
            user_id=user_id,
            content_item_id=content_item_id,
            is_positive=1 if is_positive else 0,
            comment=comment
        )
        session.add(feedback)
        
        # Обновляем статистику контента
        content = session.query(ContentItem).filter(
            ContentItem.id == content_item_id
        ).first()
        if content:
            if is_positive:
                content.positive_feedback += 1
            else:
                content.negative_feedback += 1
            session.commit()
    finally:
        session.close()


# ============================================
# Утилиты
# ============================================

def get_all_stress_types() -> List[str]:
    """Получить все типы стресса"""
    return [item.value for item in StressType]


def drop_all_tables():
    """Удалить все таблицы (для тестов!)"""
    Base.metadata.drop_all(engine)