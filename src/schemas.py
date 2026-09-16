"""
Модуль Pydantic-схем.
Служит шлюзом безопасности для валидации данных от фронтенда (In) и для фронтенда (Out).
"""
from pydantic import BaseModel, ConfigDict


class RecipeBase(BaseModel):
    """Общие базовые поля рецепта для всех экранов."""
    title: str
    cooking_time: int

    model_config = ConfigDict(from_attributes=True)


class RecipeCreate(RecipeBase):
    """Схема данных, присылаемых клиентом для создания нового рецепта."""
    ingredients: str
    description: str


class RecipeListOut(RecipeBase):
    """Схема легкого ответа для таблицы первого экрана (без лишнего текста)."""
    id: int
    views_count: int


class RecipeDetailOut(RecipeListOut):
    """Схема полного детального ответа для второго экрана (весь фарш)."""
    ingredients: str
    description: str






