"""Todo CRUD endpoints backed by an in-memory store.

这是一个演示用的最小实现：数据只保存在进程内存里，重启即丢失。
它的作用只是给 AI Factory 流水线一个"可以被 issue 驱动着不断演进"的载体。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models import Todo, TodoCreate, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])

_todos: dict[int, Todo] = {}
_next_id = 1


def reset_store() -> None:
    """Test-only helper to reset in-memory state between test cases."""
    global _next_id
    _todos.clear()
    _next_id = 1


@router.get("", response_model=list[Todo])
def list_todos() -> list[Todo]:
    return list(_todos.values())


@router.post("", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate) -> Todo:
    global _next_id
    todo = Todo(id=_next_id, **payload.model_dump())
    _todos[todo.id] = todo
    _next_id += 1
    return todo


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: int) -> Todo:
    todo = _todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
    todo = _todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated = todo.model_copy(update=payload.model_dump(exclude_unset=True))
    _todos[todo_id] = updated
    return updated


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> None:
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del _todos[todo_id]
