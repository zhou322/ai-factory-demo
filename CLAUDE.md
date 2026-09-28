# CLAUDE.md -- AI Factory Operating Rules

This repository is a validation project for an "AI Factory + Spec-Driven
Development" pipeline. The FastAPI app is just a vehicle; what actually
matters is that **every feature change is driven by a GitHub issue and
flows automatically through six stages: init -> plan -> improve ->
implement -> verify -> deploy**. You (Claude) will be woken up in different
workflows acting as a different stage each time. Always follow the rules
below.

## General rules

1. **Spec first**: never implement code before a `specs/<issue-number>-<slug>.md`
   spec exists and has been approved by a human (the issue carries the
   `stage:implement` label only after that). Do not skip the plan stage and
   jump straight to code.
2. **Never push directly to main**: every change goes through a PR. Never
   run `git push origin main`.
3. **Always run the test suite after any change**: run `pytest -q` and make
   sure everything passes before committing or opening a PR. If tests fail,
   fix them; if you cannot fix them, say so honestly in the PR/issue instead
   of pretending they passed.
4. **Labels are the state machine**: an issue's `stage:*` label represents
   its current position in the pipeline. When you finish your stage's work,
   advance it yourself with
   `gh issue edit <number> --remove-label "stage:xxx" --add-label "stage:yyy"`
   rather than leaving that for a human to do.
5. **Use the `gh` CLI for all GitHub operations** (`gh issue comment`,
   `gh pr create`, `gh issue edit --add-label`, etc.). A token with the
   right permissions is already exposed as `GH_TOKEN` in the environment --
   just use it.
6. **Be honest about uncertainty**: if an issue's description is not
   enough to act on, do not guess. Ask specific questions in a comment,
   set the label to `needs-human-input`, and stop -- do not advance to the
   next stage.
7. **Small, clear commits.** PR descriptions should link back to the issue
   (`Closes #<number>` only on the final implementation PR; use
   `Refs #<number>` on the spec PR so the issue is not closed prematurely).

## Stage responsibilities

- **init** (`01-ai-init.yml`): understand the issue, turn a possibly vague
  request into a clear problem statement plus a draft of acceptance
  criteria, comment it on the issue, then advance to `stage:plan`. If the
  request is too vague, stop at `needs-human-input` instead.
- **plan** (`02-ai-plan.yml`): write a full spec following
  `specs/TEMPLATE.md` (background, non-goals, API design, data model, task
  breakdown, acceptance criteria), commit it on a new branch, open a PR
  titled `spec: <title>`, comment the PR link on the issue, advance to
  `stage:plan-review`.
- **improve** (`03-ai-improve.yml`): triggered when someone comments
  `/revise <feedback>` on the spec PR or the issue. Update the spec file on
  the same branch based on the feedback and push; do not open a new PR.
- **implement** (`04-ai-implement.yml`): only wakes up once the spec PR has
  been merged, or a human comments `/implement` on the issue. Read the
  matching `specs/*.md`, implement the code and tests, run `pytest` locally
  until it passes, open the implementation PR (`Closes #<number>`), advance
  to `stage:verify`.
- **verify** (`06-ai-verify.yml`, alongside the standard `05-ci.yml` CI):
  for the implementation PR, check off each acceptance criterion from the
  spec and post a checklist comment. Never merge the PR yourself -- merging
  stays a human decision.
- **deploy** (`07-deploy.yml`): runs automatically after a merge to main.
  "Deploy" here is a demo-grade build + health-check smoke test. On
  success, comment on the original issue and close it, with the
  `stage:done` label.

## Code style

- Python 3.11+, type-annotated, FastAPI + Pydantic v2 style.
- Keep the `app/` layout: data models in `models.py`, routes split by
  resource under `routers/`.
- Every new feature needs matching tests under `tests/test_*.py`, covering
  both the happy path and at least one error path.
