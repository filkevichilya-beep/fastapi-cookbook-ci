"""
Модуль описания ORM-моделей.
Задает физическую структуру таблиц внутри базы данных на жестком диске.
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text

from src.database import Base

class Recipe(Base):
    """Таблица рецептов кулинарной книги."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    views_count: Mapped[int] = mapped_column(default=0)
    cooking_time: Mapped[int] = mapped_column()
    ingredients: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)