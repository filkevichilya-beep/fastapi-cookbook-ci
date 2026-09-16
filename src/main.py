"""
Главный модуль приложения.
Запускает сервер FastAPI, управляет его жизненным циклом и обрабатывает HTTP-запросы.
"""
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import engine, async_session_factory
from src import models, schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет стартами и остановками сервера."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Кулинарная книга!", lifespan=lifespan)


async def get_db_session():
    """Генератор изолированных сессий-черновиков на каждый HTTP-запрос."""
    async with async_session_factory() as session:
        yield session


@app.post("/recipes", response_model=schemas.RecipeDetailOut)
async def create_recipe(
        recipe: schemas.RecipeCreate,
        db: AsyncSession = Depends(get_db_session)
) -> models.Recipe:
    """Создает новый рецепт в кулинарной книге."""
    new_recipe = models.Recipe(**recipe.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe


@app.get("/recipes", response_model=List[schemas.RecipeListOut])
async def get_all_recipes(
        db: AsyncSession = Depends(get_db_session)
) -> List[models.Recipe]:
    """Возвращает список всех рецептов с двухуровневой сортировкой."""
    statement = select(models.Recipe).order_by(
        models.Recipe.views_count.desc(),
        models.Recipe.cooking_time
    )
    result = await db.execute(statement)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetailOut)
async def get_recipe_by_id(
        recipe_id: int,
        db: AsyncSession = Depends(get_db_session)
) -> models.Recipe:
    """Возвращает детальную инфу рецепта по ID и увеличивает счетчик просмотров на +1."""
    recipe = (await db.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )).scalar_one_or_none()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views_count += 1
    await db.commit()

    return recipe
