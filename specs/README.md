# specs/ 目录说明

这里存放 Spec-Driven Development 的规格文档，一个功能一份文件，命名为：

```
specs/<issue编号>-<slug>.md
```

例如 issue #12「支持给 Todo 打标签」对应 `specs/12-todo-tags.md`。

规格文档由 AI 在 `stage:plan` 阶段依据 [`TEMPLATE.md`](./TEMPLATE.md) 生成，
以 PR 的形式提交，必须经人工 review 通过（合并该 PR）之后，才允许进入 `stage:implement` 阶段。

这是整条 AI Factory 流水线里 **唯一的真相来源**：实现阶段的 AI 只被允许依据已合并的 spec 写代码，
不允许自己重新解读 issue 原始描述。
