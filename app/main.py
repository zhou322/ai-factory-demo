"""FastAPI application entrypoint.

这个应用本身很简单，它存在的目的是作为 "AI Factory" 全自动开发流水线的验证载体：
所有新功能都应该先在一个 GitHub Issue 里被提出，经过
init -> plan -> improve -> implement -> verify -> deploy
六个阶段，由 GitHub Actions + Claude Code Action 自动流转完成，
而不是靠人手工在这里改代码。见仓库根目录的 CLAUDE.md 和 docs/ai-factory.md。
"""
from fastapi import FastAPI

from app.routers import todos

app = FastAPI(
    title="AI Factory Demo",
    description="用于验证 AI Factory + Spec-Driven Development 全自动开发流水线的最小 FastAPI 应用",
    version="0.1.0",
)

app.include_router(todos.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
