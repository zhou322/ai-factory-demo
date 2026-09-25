from fastapi.testclient import TestClient

from app.main import app
from app.routers.todos import reset_store

client = TestClient(app)


def setup_function() -> None:
    reset_store()


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_and_list_todo() -> None:
    resp = client.post("/todos", json={"title": "写 spec"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "写 spec"
    assert body["done"] is False

    resp = client.get("/todos")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_missing_todo_returns_404() -> None:
    resp = client.get("/todos/999")
    assert resp.status_code == 404


def test_update_and_delete_todo() -> None:
    created = client.post("/todos", json={"title": "实现功能"}).json()
    todo_id = created["id"]

    resp = client.patch(f"/todos/{todo_id}", json={"done": True})
    assert resp.status_code == 200
    assert resp.json()["done"] is True

    resp = client.delete(f"/todos/{todo_id}")
    assert resp.status_code == 204

    resp = client.get(f"/todos/{todo_id}")
    assert resp.status_code == 404
