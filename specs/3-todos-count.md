# Spec: GET /todos/count endpoint

- Issue: #3
- Status: Draft
- Created: 2026-10-12

## 1. Background / Problem statement

Clients currently have to call `GET /todos` and measure the returned list to learn how many todos exist. A dedicated read-only endpoint returns the total directly without transferring every todo.

## 2. Goals

- Add `GET /todos/count` returning the total number of stored todos as `{"count": <int>}`.
- Ensure the route is not shadowed by `GET /todos/{todo_id}`.

## 3. Non-goals (Out of Scope)

- Filtering (e.g. `?done=true`) or per-status counts.
- Persistence or any change to the in-memory store.
- Changes to existing endpoints.

## 4. Design

### 4.1 API changes

| Method | Path | Description |
| --- | --- | --- |
| GET | `/todos/count` | Returns HTTP 200 with `{"count": N}`, N being the number of todos in the store (all statuses). |

The handler must be declared in `app/routers/todos.py` **before** `GET /{todo_id}`; otherwise FastAPI matches `count` as `todo_id` and returns 422.

### 4.2 Data model changes

Add to `app/models.py`:

```python
class TodoCount(BaseModel):
    count: int = Field(..., ge=0, description="Total number of todos")
```

No changes to existing models.

### 4.3 Key implementation notes / edge cases

- Implementation: `return TodoCount(count=len(_todos))` with `response_model=TodoCount`.
- Completed and incomplete todos are both counted.
- Empty store returns `{"count": 0}`.
- Deleting a todo decreases the count by 1; deleting a nonexistent id (404) leaves it unchanged.
- `GET /todos/{todo_id}` behavior for numeric ids and non-numeric ids (422) is unchanged.

## 5. Task breakdown

- [ ] Add `TodoCount` model to `app/models.py`.
- [ ] Add `count_todos` route in `app/routers/todos.py`, placed before `/{todo_id}` routes.
- [ ] Add tests in `tests/test_todos.py` (or a new `tests/test_todos_count.py`).
- [ ] Run `pytest -q` and confirm everything passes.

## 6. Acceptance Criteria

- [ ] AC1: `GET /todos/count` returns HTTP 200 with JSON body `{"count": <int>}`.
- [ ] AC2: With an empty store the response is `{"count": 0}`.
- [ ] AC3: After creating N todos (e.g. 3) the response is `{"count": N}`; after deleting one it is `{"count": N-1}`.
- [ ] AC4: Todos with `done=true` and `done=false` are both counted (e.g. 1 done + 2 not done -> 3).
- [ ] AC5: `/todos/count` is routed to the count handler, not `/todos/{todo_id}` (status is 200, not 422/404).
- [ ] AC6: `GET /todos/1` still returns the todo (200) or 404 when missing, and existing tests still pass.
- [ ] AC7: Tests cover the empty case, non-empty case, decrease after delete, mixed done status, and route ordering; `pytest -q` passes.

## 7. Risks and rollback

Low risk: additive, read-only endpoint. The only hazard is route ordering, covered by AC5. Rollback by reverting the implementation PR.
