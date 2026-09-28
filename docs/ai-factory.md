# AI Factory: fully automated development pipeline

This repository demonstrates an "AI Factory + Spec-Driven Development"
pattern: **humans only propose ideas (open an issue) and gate the key
checkpoints (review / merge); everything in between -- clarifying
requirements, writing specs, implementing code, opening PRs, running
tests, and deploying -- is done automatically by AI through GitHub
Actions.**

The FastAPI Todo API is just a minimal vehicle to validate this; you can
keep evolving it purely through issues.

## 1. Overall state machine

```
        (human) opens issue
              |
              v
        stage:init  ──────────────▶ needs-human-input (not enough info; AI asks and stops)
              | AI drafts problem statement / acceptance criteria
              v
        stage:plan  ── AI writes a spec per specs/TEMPLATE.md, opens a spec PR
              |
              v
     stage:plan-review ──/revise feedback──▶ stage:improve (AI updates the spec, loops back to plan-review)
              | human approves -> merges the spec PR
              v
        stage:implement ── AI implements code + tests against the merged spec, opens an implementation PR
              |
              v
        stage:verify ── standard CI (pytest/lint) + AI self-check against acceptance criteria, posts a checklist
              |
              v
        (human) reviews and merges the implementation PR into main
              |
              v
        stage:deploy ── automatic build + smoke test (demo-grade), closes the issue on success
              |
              v
        stage:done
```

Labels are the "current state" of this state machine. Each stage's workflow
only fires on the event/label it owns, and advances the label itself once
its work is done -- that is what makes the whole thing fully automated
without a human touching labels by hand.

## 2. One-time setup (must be done manually)

### 2.1 Install the Claude GitHub App

Go to https://github.com/apps/claude and install it on
`zhou322/ai-factory-demo`.

### 2.2 Add two repository secrets

GitHub repo -> Settings -> Secrets and variables -> Actions -> New
repository secret:

1. `ANTHROPIC_API_KEY`: an API key generated from the Console at
   https://platform.claude.com.
   (If you use a Claude subscription instead of pay-as-you-go API billing,
   use `CLAUDE_CODE_OAUTH_TOKEN` instead -- generate it locally with
   `claude setup-token`, then replace the `anthropic_api_key` line in every
   workflow with `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`.)

2. `GH_AUTOMATION_PAT`: **this step matters, do not skip it.**
   GitHub Actions' default `GITHUB_TOKEN` has an anti-recursion mechanism:
   a git push / PR / label change made with it will not trigger other
   workflows (this exists to prevent infinite loops). But this pipeline
   relies exactly on that kind of chain reaction ("AI adds a label ->
   triggers the next workflow"), so it needs a real Personal Access Token
   instead of the default token.

   How to create one: GitHub avatar (top right) -> Settings -> Developer
   settings -> Personal access tokens -> Fine-grained tokens -> Generate
   new token:
   - Repository access: "Only select repositories" -> select
     `ai-factory-demo`
   - Permissions: Contents (Read and write), Issues (Read and write),
     Pull requests (Read and write)
   - Paste the generated token into the repository secret `GH_AUTOMATION_PAT`

### 2.3 Bootstrap the labels

From the repo's Actions tab, manually run the `00-bootstrap-labels`
workflow once (Actions -> Bootstrap AI Factory Labels -> Run workflow). It
uses `GH_AUTOMATION_PAT` to create every `stage:*` label the pipeline
needs.

## 3. Day-to-day usage

1. Open a new issue using the "Feature Request" template describing the
   feature you want the FastAPI app to have.
2. From there, do nothing and just watch the issue's labels and comments.
   The AI will automatically:
   - clarify your request into a clean problem statement during
     `stage:init` (and ask you questions if it is not clear enough);
   - open a spec PR for you to review during `stage:plan`;
   - if the spec needs changes, comment `/revise your feedback` directly on
     the PR and the AI will update it;
   - once you are happy with the spec, merge that spec PR;
   - the AI then implements the real code, opens the implementation PR, CI
     runs the tests, and the AI self-checks it against the acceptance
     criteria;
   - you review the code PR and merge it once you are satisfied;
   - after the merge it "deploys" automatically (a demo-grade build +
     health check), reports back on the issue, and closes it.
3. If a stage ever gets stuck or the AI misunderstood something, just
   comment in natural language on the issue or the relevant PR, or talk to
   it directly with `@claude ...` (the Claude GitHub App is installed, so
   `@claude` works anywhere).

## 4. Workflow file overview

| File | Trigger | Responsibility |
| --- | --- | --- |
| `00-bootstrap-labels.yml` | Manual (`workflow_dispatch`) | Create/update all `stage:*` labels |
| `01-ai-init.yml` | Issue opened | Clarify requirements, draft acceptance criteria, advance to `stage:plan` |
| `02-ai-plan.yml` | Issue labeled `stage:plan` | Write the spec, open the spec PR, advance to `stage:plan-review` |
| `03-ai-improve.yml` | Comment `/revise ...` on the spec PR / issue | Update the spec based on feedback |
| `04-ai-implement.yml` | Spec PR merged, or comment `/implement` | Implement code + tests against the spec, open the implementation PR, advance to `stage:verify` |
| `05-ci.yml` | Any PR | Standard CI: install deps, `pytest`, `ruff` |
| `06-ai-verify.yml` | PR from a `feature/*` branch | AI self-checks the diff against the spec's acceptance criteria, posts a checklist |
| `07-deploy.yml` | Push to `main` | Demo-grade "deploy": build + health-check smoke test, report back and close the issue |

## 5. Known trade-offs (demo stage)

- "Deploy" is demo-grade (build a Docker image locally + run the container
  + smoke-test `/health`), with no real cloud environment behind it. Wire
  up a real deployment by replacing the last step of `07-deploy.yml`.
- One issue maps to one spec / one feature branch; concurrent issues
  editing the same files and merge conflicts between them are not handled.
  This is a deliberate simplification to get the "fully automated
  pipeline" itself working first.
- Advancing from `stage:plan-review` to `stage:implement` relies on the
  signal "the spec PR was merged". If you would rather advance on a human
  comment like `/approve-plan` instead of requiring the PR to be merged,
  adjust the trigger condition in `04-ai-implement.yml`.
