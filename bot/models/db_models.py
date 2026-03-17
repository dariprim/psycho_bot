from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Enum, Index, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class StressType(enum.Enum):
    """Типы стрессовых состояний"""
    anxiety = "anxiety"      # Тревога
    sadness = "sadness"      # Грусть/депрессия
    stress = "stress"        # Стресс
    anger = "anger"          # Гнев
    fatigue = "fatigue"      # Усталость


class User(Base):
    """Пользователи бота"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Профиль пользователя (настройки, предпочтения)
    preferences = Column(JSON, nullable=True, default=dict)
    
    # История настроений (mood_history)
    mood_history = Column(JSON, nullable=True, default=list)
    
    # Статистика
    total_interactions = Column(Integer, default=0)
    last_interaction = Column(DateTime, nullable=True)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    feedback_items = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_users_telegram_id', 'telegram_id'),
    )


class Category(Base):
    """Категории контента (техники, книги, игры, упражнения)"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)  # book, game, technique, exercise
    
    # Для каких состояний рекомендуется
    stress_types = Column(JSON, nullable=True, default=list)
    
    # Метаданные
    is_active = Column(Integer, default=1)  # 1 = активна, 0 = скрыта
    sort_order = Column(Integer, default=0)
    
    # Связи
    content_items = relationship("ContentItem", back_populates="category", cascade="all, delete-orphan")


class ContentItem(Base):
    """Контент (книги, игры, техники, упражнения)"""
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Дополнительные данные (автор, платформа, ссылка и т.д.)
    meta_data = Column(JSON, nullable=True, default=dict)
    
    # Для какого состояния рекомендуется
    stress_type = Column(String(50), nullable=False, index=True)
    
    # Контент
    content_text = Column(Text, nullable=True)  # Текст техники/упражнения
    external_url = Column(String(500), nullable=True)  # Ссылка на внешний ресурс
    
    # Статистика использования
    usage_count = Column(Integer, default=0)
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)
    
    # Статус
    is_active = Column(Integer, default=1)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    category = relationship("Category", back_populates="content_items")
    feedback_items = relationship("Feedback", back_populates="content_item", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_content_stress_type', 'stress_type'),
    )


class Feedback(Base):
    """Обратная связь от пользователей (понравилось/не понравилось)"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_item_id = Column(Integer, ForeignKey("content_items.id", ondelete="CASCADE"), nullable=True)
    
    # Оценка
    is_positive = Column(Integer, nullable=False)  # 1 = понравилось, 0 = не понравилось
    comment = Column(Text, nullable=True)
    
    # Дата
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="feedback_items")
    content_item = relationship("ContentItem", back_populates="feedback_items")