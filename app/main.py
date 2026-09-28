"""FastAPI application entrypoint.

This application is intentionally simple. It exists to serve as the
verification vehicle for the "AI Factory" fully automated development
pipeline: every new feature should be proposed as a GitHub issue and flow
through six stages -- init -> plan -> improve -> implement -> verify ->
deploy -- driven automatically by GitHub Actions and Claude Code Action,
rather than being hand-edited here. See CLAUDE.md and docs/ai-factory.md
at the repository root.
"""
from fastapi import FastAPI

from app.routers import todos

app = FastAPI(
    title="AI Factory Demo",
    description="Minimal FastAPI app used to validate the AI Factory + Spec-Driven Development fully automated pipeline",
    version="0.1.0",
)

app.include_router(todos.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
