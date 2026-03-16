from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100))
    description = Column(Text)
    stress_type = Column(String(50), nullable=False, index=True)

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    platform = Column(String(100))
    description = Column(Text)
    stress_type = Column(String(50), nullable=False, index=True)