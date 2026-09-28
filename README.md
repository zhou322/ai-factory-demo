# ai-factory-demo

A minimal FastAPI Todo API used as the vehicle for validating an
**AI Factory + Spec-Driven Development** fully automated pipeline: from
opening an issue, to clarifying requirements, writing a spec, implementing,
testing, and deploying -- all driven by GitHub Actions + Claude Code
Action. Humans only propose ideas and review at the key checkpoints.

- Full pipeline description, state machine, and setup steps:
  [`docs/ai-factory.md`](docs/ai-factory.md)
- Rules the AI must follow at every stage: [`CLAUDE.md`](CLAUDE.md)
- Spec template: [`specs/TEMPLATE.md`](specs/TEMPLATE.md)

## Run locally

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Run tests locally

```bash
pytest -q
```
