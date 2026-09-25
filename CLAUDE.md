# CLAUDE.md — AI Factory 工作规则

本仓库是一个 "AI Factory + Spec-Driven Development" 流水线的验证项目。
FastAPI 应用本身只是载体，重点是：**每一个功能变更都必须由 GitHub Issue 驱动，
经过 init -> plan -> improve -> implement -> verify -> deploy 六个阶段自动流转**。
你（Claude）在不同 workflow 里会被以不同阶段的身份唤醒，请始终遵守下面的规则。

## 通用规则

1. **Spec 先行**：任何代码实现之前，必须存在一份 `specs/<issue编号>-<slug>.md` 规格文档，
   并且它是被人工批准过的（对应 issue 上有 `stage:implement` 标签）。不要跳过 plan 阶段直接写代码。
2. **不要直接推 main**：所有变更都通过 PR 完成，绝不 `git push origin main`。
3. **每次改动都要跑测试**：改完代码后必须本地执行 `pytest -q`，全部通过才可以提交 / 打开 PR。
   如果测试失败，先修复，修复不了就在 PR / issue 里如实说明，不要假装通过。
4. **标签即状态机**：issue 的 `stage:*` 标签代表它在流水线里的位置。当你完成本阶段的工作后，
   使用 `gh issue edit <编号> --remove-label "stage:xxx" --add-label "stage:yyy"` 把它推进到下一阶段，
   而不是留给人去手动改标签。
5. **所有 GitHub 操作用 `gh` CLI**（`gh issue comment`、`gh pr create`、`gh issue edit --add-label` 等），
   环境里已经通过 `GH_TOKEN` 提供了有权限的 token，直接用即可。
6. **诚实汇报不确定性**：如果 issue 描述信息不够，不要凭空猜测需求，而是在评论里提出具体问题，
   并把标签改成 `needs-human-input`，停下来等人回答，不要继续往下一阶段推进。
7. **小步提交，清晰的 commit message**，PR 描述里要链接对应的 issue（`Closes #<编号>` 仅在真正是最终实现 PR 时使用；
   spec PR 用 `Refs #<编号>`，避免过早自动关闭 issue）。

## 各阶段职责

- **init**（`01-ai-init.yml`）：读懂 issue，把模糊需求整理成清晰的问题陈述 + 验收标准草稿，
  评论在 issue 下，然后推进到 `stage:plan`。信息不足则停在 `needs-human-input`。
- **plan**（`02-ai-plan.yml`）：依据 `specs/TEMPLATE.md` 写出完整规格（背景、非目标、API 设计、
  数据模型、任务拆分、验收标准），提交到新分支，开一个标题为 `spec: <标题>` 的 PR，
  在 issue 里评论 PR 链接，标签推进到 `stage:plan-review`。
- **improve**（`03-ai-improve.yml`）：当有人在 spec PR 或 issue 下评论 `/revise <反馈>` 时被唤醒，
  根据反馈修改同一个分支上的 spec 文件，push 更新，不要开新 PR。
- **implement**（`04-ai-implement.yml`）：只有当 spec PR 已合并、或人工在 issue 下评论 `/implement` 时才会被唤醒。
  读取对应 `specs/*.md`，实现代码 + 测试，本地跑通 `pytest`，开实现 PR（`Closes #<编号>`），
  标签推进到 `stage:verify`。
- **verify**（`06-ai-verify.yml`，配合标准 CI `05-ci.yml`）：针对实现 PR，对照 spec 里的验收标准
  逐条自查，在 PR 下贴一份 checklist 评论（每条 AC 是否满足），不要自己合并 PR —— 合并权在人类手里。
- **deploy**（`07-deploy.yml`）：合并进 main 后自动运行，这里的"部署"是演示性质的
  （构建 + 健康检查冒烟测试），成功后在原始 issue 下评论并关闭它，标签设为 `stage:done`。

## 代码风格

- Python 3.11+，使用类型标注；FastAPI + Pydantic v2 风格。
- 保持 `app/` 目录结构：`models.py` 放数据模型，`routers/` 按资源拆分路由。
- 新功能一律要有对应的 `tests/test_*.py`，覆盖正常路径和至少一个错误路径。
