from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_create_recipe():
    """Тест создания рецепта — строго по структуре POST из статьи."""
    response = client.post(
        "/recipes",
        json={
            "title": "Паста Карбонара",
            "cooking_time": 15,
            "ingredients": "Спагетти, бекон, сыр, яйца",
            "description": "Обжарить бекон, сварить пасту, смешать всё с сыром и яйцом."
        }
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
            "description": "Обжарить на сильном огне по 3 минуты со всех сторон."
        }
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

