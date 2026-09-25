# AI Factory 全自动开发流水线

这个仓库演示一种"AI Factory + Spec-Driven Development"的全自动开发模式：
**人只负责提出想法（开 issue）和把关关键节点（review / merge），
中间从需求澄清到写代码、开 PR、跑测试、部署的全过程都由 AI 通过 GitHub Actions 自动完成。**

FastAPI 的 Todo API 只是一个最小的验证载体，你可以在此基础上不断通过 issue 演进它。

## 1. 整体状态机

```
        (人) 开 issue
              |
              v
        stage:init  ──────────────▶ needs-human-input（信息不够，AI 提问后停住）
              | AI 整理问题/验收标准
              v
        stage:plan  ── AI 依据 specs/TEMPLATE.md 写 spec，开 spec PR
              |
              v
     stage:plan-review ──/revise反馈──▶ stage:improve（AI 改 spec，循环回 plan-review）
              | 人 review 通过 -> 合并 spec PR
              v
        stage:implement ── AI 依据已合并的 spec 实现代码+测试，开实现 PR
              |
              v
        stage:verify ── 标准 CI（pytest/lint）+ AI 自查验收标准，贴 checklist
              |
              v
        （人）review 通过 -> 合并实现 PR 进 main
              |
              v
        stage:deploy ── 自动构建 + 冒烟测试（演示性质），成功后关闭 issue
              |
              v
        stage:done
```

标签（label）就是这个状态机的"当前状态"，每个阶段对应的 workflow 只在自己负责的标签/事件上被触发，
完成后自己把标签推进到下一个状态——这是全自动化的关键，人不需要手工改标签。

## 2. 前置准备（必须手动做一次）

### 2.1 安装 Claude GitHub App

打开 https://github.com/apps/claude ，安装到 `zhou322/ai-factory-demo` 这个仓库。

### 2.2 添加两个 repository secret

进入 GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret，添加：

1. `ANTHROPIC_API_KEY`：从 https://platform.claude.com 的 Console 里生成的 API Key。
   （如果你用的是 Claude 订阅而不是按量计费的 API，改用 `CLAUDE_CODE_OAUTH_TOKEN`，
   本地跑 `claude setup-token` 生成，然后把所有 workflow 里的 `anthropic_api_key` 那一行
   换成 `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`。）

2. `GH_AUTOMATION_PAT`：**这一步很重要，不能跳过。**
   GitHub Actions 默认的 `GITHUB_TOKEN` 有一个"防递归"机制：用它做的
   git push / 开 PR / 加标签，不会触发其它 workflow（否则容易死循环）。
   但我们这条流水线恰恰需要"AI 加了个标签 -> 触发下一个 workflow"这种链式反应，
   所以必须用一个真正的 Personal Access Token 来代替默认 token。

   创建步骤：GitHub 右上角头像 → Settings → Developer settings → Personal access tokens
   → Fine-grained tokens → Generate new token：
   - Repository access 选 "Only select repositories" → 选 `ai-factory-demo`
   - Permissions 里勾选：Contents（Read and write）、Issues（Read and write）、
     Pull requests（Read and write）
   - 生成后把 token 粘贴进仓库 secret `GH_AUTOMATION_PAT`

### 2.3 初始化 labels

仓库的 Actions 页面手动运行一次 `00-bootstrap-labels` workflow
（Actions → Bootstrap AI Factory Labels → Run workflow），
它会用 `GH_AUTOMATION_PAT` 创建流水线需要的所有 `stage:*` 标签。

## 3. 日常使用方式

1. 用 "Feature Request" issue 模板开一个新 issue，描述你想要 FastAPI 应用具备的新功能。
2. 之后什么都不用做，观察 issue 的标签和评论，AI 会自动：
   - 在 `stage:init` 阶段把你的需求整理成清晰的问题陈述（信息不够会反问你）；
   - 在 `stage:plan` 阶段开一个 spec PR，你去 review 这份规格文档；
   - 如果规格有问题，直接在 PR 上评论 `/revise 你的意见`，AI 会修改；
   - 你觉得 spec OK 了，合并这个 spec PR；
   - AI 自动开始实现，开出真正的代码 PR，CI 跑测试，AI 自己对照验收标准做一次自查；
   - 你 review 代码 PR，没问题就合并；
   - 合并后自动"部署"（这里是演示性质的构建 + 健康检查），并回到 issue 里报告完成，关闭 issue。
3. 如果某个阶段卡住了 / AI 理解错了，直接在 issue 或对应 PR 下用自然语言评论，
   或者用 `@claude ...` 直接对话调整（因为装了 Claude GitHub App，`@claude` 随时可用）。

## 4. Workflow 文件一览

| 文件 | 触发条件 | 职责 |
| --- | --- | --- |
| `00-bootstrap-labels.yml` | 手动 (`workflow_dispatch`) | 创建/更新所有 `stage:*` 标签 |
| `01-ai-init.yml` | issue 被打开 | 需求澄清，产出验收标准草稿，推进到 `stage:plan` |
| `02-ai-plan.yml` | issue 被打上 `stage:plan` 标签 | 写 spec，开 spec PR，推进到 `stage:plan-review` |
| `03-ai-improve.yml` | 在 spec PR / issue 下评论 `/revise ...` | 按反馈修改 spec |
| `04-ai-implement.yml` | spec PR 合并，或评论 `/implement` | 依据 spec 写代码+测试，开实现 PR，推进到 `stage:verify` |
| `05-ci.yml` | 任意 PR | 标准 CI：安装依赖、`pytest`、`ruff` |
| `06-ai-verify.yml` | `feature/*` 分支的 PR | AI 对照 spec 验收标准自查，贴 checklist |
| `07-deploy.yml` | push 到 `main` | 演示性"部署"：构建 + 健康检查冒烟测试，回写 issue 并关闭 |

## 5. 已知的取舍（demo 阶段）

- "部署"是演示性质的（本地构建 Docker 镜像 + 起容器做 `/health` 冒烟测试），
  没有接真实的云环境；如果要接真实部署，替换 `07-deploy.yml` 最后一步即可。
- 一个 issue 对应一个 spec / 一条功能分支，没有处理多个 issue 并发修改同一批文件的合并冲突场景，
  这是刻意简化，方便先把"全自动流水线"跑通。
- `stage:plan-review` 到 `stage:implement` 的推进依赖"spec PR 被合并"这个信号，
  如果你更喜欢"人工评论 /approve-plan 就推进"而不是必须合并 PR，
  可以调整 `04-ai-implement.yml` 的触发条件。
