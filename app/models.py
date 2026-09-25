"""Pydantic models for the Todo demo API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    done: bool = Field(default=False, description="Whether the todo is done")


class TodoCreate(TodoBase):
    """Payload for creating a Todo."""


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class Todo(TodoBase):
    id: int
