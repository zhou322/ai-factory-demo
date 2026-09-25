# ai-factory-demo

一个用 FastAPI 写的最小 Todo API，作为验证 **AI Factory + Spec-Driven Development**
全自动开发流水线的载体：从提 issue 到需求澄清、写 spec、实现、测试、部署，
全部由 GitHub Actions + Claude Code Action 自动完成，人只负责提想法和在关键节点 review。

- 完整流水线说明、状态机、配置步骤见 [`docs/ai-factory.md`](docs/ai-factory.md)
- AI 在各阶段必须遵守的规则见 [`CLAUDE.md`](CLAUDE.md)
- 规格文档模板见 [`specs/TEMPLATE.md`](specs/TEMPLATE.md)

## 本地运行

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## 本地测试

```bash
pytest -q
```
