import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src import models
from src.main import app, get_db_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_cookbook.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)


def setup_module():
    """Создает таблицы в тестовой базе данных перед началом всех тестов."""

    async def create_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.drop_all)
            await conn.run_sync(models.Base.metadata.create_all)

    asyncio.run(create_tables())


async def override_get_db_session():
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_db_session] = override_get_db_session

client = TestClient(app)


def test_create_recipe():
    """Тест создания рецепта — строго по структуре POST."""
    response = client.post(
        "/recipes",
        json={
            "title": "Паста Карбонара",
            "cooking_time": 15,
            "ingredients": "Спагетти, бекон, сыр, яйца",
            "description": "Обжарить бекон, сварить пасту, смешать всё с сыром и яйцом.",
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Паста Карбонара"
    assert response.json()["id"] is not None


def test_get_recipe_by_id():
    """Тест деталки и проверки просмотров — через обычный client.get."""
    response = client.post(
        "/recipes",
        json={
            "title": "Стейк Рибай",
            "cooking_time": 20,
            "ingredients": "Говядина, розмарин, чеснок",
            "description": "Обжарить на сильном огне по 3 минуты со всех сторон.",
        },
    )
    recipe_id = response.json()["id"]

    response_first = client.get(f"/recipes/{recipe_id}")
    assert response_first.status_code == 200
    assert response_first.json()["views_count"] == 1

    response_second = client.get(f"/recipes/{recipe_id}")
    assert response_second.json()["views_count"] == 2


def test_get_all_recipes_sorting():
    """Тест общего списка — проверяем, что эндпоинт отдает успешный статус."""
    response = client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
