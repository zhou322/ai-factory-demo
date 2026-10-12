from fastapi.testclient import TestClient

from app.main import app
from app.routers.todos import reset_store

client = TestClient(app)


def setup_function() -> None:
    reset_store()


def test_count_empty() -> None:
    resp = client.get("/todos/count")
    assert resp.status_code == 200
    assert resp.json() == {"count": 0}


def test_count_after_create_and_delete() -> None:
    for i in range(3):
        client.post("/todos", json={"title": f"t{i}"})
    assert client.get("/todos/count").json() == {"count": 3}
    assert client.get("/todos/count").json() == {"count": 3}
    assert client.delete("/todos/1").status_code == 204
    assert client.get("/todos/count").json() == {"count": 2}


def test_count_unchanged_by_failed_delete() -> None:
    client.post("/todos", json={"title": "a"})
    assert client.delete("/todos/99").status_code == 404
    assert client.get("/todos/count").json() == {"count": 1}


def test_count_includes_done_and_not_done() -> None:
    client.post("/todos", json={"title": "a", "done": True})
    client.post("/todos", json={"title": "b"})
    client.post("/todos", json={"title": "c", "done": False})
    assert client.get("/todos/count").json() == {"count": 3}


def test_count_route_not_shadowed_by_todo_id() -> None:
    client.post("/todos", json={"title": "a"})
    resp = client.get("/todos/count")
    assert resp.status_code == 200
    assert list(resp.json()) == ["count"]
    assert isinstance(resp.json()["count"], int)


def test_todo_id_routes_unchanged() -> None:
    client.post("/todos", json={"title": "a"})
    assert client.get("/todos/1").status_code == 200
    assert client.get("/todos/2").status_code == 404
    assert client.get("/todos/abc").status_code == 422
