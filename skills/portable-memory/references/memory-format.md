# Portable Memory v0.3

UTF-8 Markdown 是交换格式。脚本兼容 0.1、0.2、0.3；不依赖某平台聊天格式。协议头使用扁平 YAML 标量；日期是 ISO YYYY-MM-DD，不支持数组或嵌套 YAML。

## 分层

| 层 | 文件 | 使用方式 |
| --- | --- | --- |
| Profile | PROFILE.md | 简短、稳定、首先读取；身份与已确认协作偏好 |
| 长期 | LONG_TERM.md | 持续目标与长期约定 |
| 当前 | CURRENT.md | observed 与 review_after 标明时效；任务相关时读取 |
| 项目 | projects/*.md、PROJECTS.md | 目标、约束、决定、进度与下一步，限项目范围 |
| 有价值的对话 | conversations/*.md、CONVERSATIONS.md | 纠正、理由、结论、未定论问题；摘要而非原始聊天 |
| 候选/来源/历史 | inbox/、agents/*/inbox/、sources/、archive/ | 非正式背景，不默认导出 |
| 正式入口 | MEMORY.md | 少量可靠摘要与上述主题索引 |

## 条目

```markdown
- [project-001] 为文档保留可编辑源文件。
  - scope: project/example
  - source: 用户明确说明，2026-01-01
  - status: confirmed
  - updated: 2026-01-01
```

事实修改沿用原 ID，明确替代关系。有来源的多次观察可写 observed 或 pending-confirmation；不要冒充 confirmed。用户此刻更正优先；临时要求只适用于对应任务。用户要求遗忘时说明 Git 旧版本仍可能保留，历史清理按另行明确范围处理。

## 默认导出

默认包含 Profile、长期记忆、有效近期摘要、近期/活跃项目与有保留价值的对话。项目与讨论建议使用：

```yaml
---
schema_version: 0.3
kind: canonical
updated: 2026-01-01
status: active
review_after: 2026-01-15
retain: false
share: true
---
```

- schema_version：0.1 / 0.2 / 0.3；kind：canonical / candidate / snapshot。
- updated：有实质内容更新的日期，不能用文件复制时间代替。
- status：项目 active / paused / completed / archived；讨论 confirmed / proposed / unresolved。
- retain:true：有持续保留价值，超出近期窗口仍可导出。未定论的重要讨论可同时 unresolved。
- share:true（缺省）：可在同一用户选择的设备/Agent 中携带；不是授权向任何人发布。
- share:false 或 share:local：留在本地库，导出时排除。需要分享其中部分时创建独立可分享摘要。
- review_after：读取时必须判断是否过期，过期状态不得当作当前事实。CURRENT 缺少有效复核日期时默认省略；项目/讨论仍可能作为历史上下文携带。

初始 recent_days 为 30，属于可调整工具默认值，不是用户永久偏好。默认纳入窗口内未归档主题，以及 active 项目、retain:true、unresolved 讨论；明确 --include 可带上指定旧主题；--all 包含全部可分享正式主题，但仍排除 share:local、候选与来源。Profile 或长期记忆被标为 local 时，先整理可分享摘要再导出。

旧项目缺少元数据时由 Agent 判断内容，补充有证据的日期/状态或显式选择；不能为过关而假造“最近更新”。重要旧决策可提炼到长期记忆或 retain 讨论。新但无价值的对话不必存入正式库。

## 交接文件

生成文件内展开所选正文，按 Profile → 长期 → 当前 → 项目 → 对话排列，不要求访问来源机器。来源平台与线程标识可以保留用于追溯；本机路径移除，未包含文件的链接省略。索引由所选内容生成，不复制全库项目目录。

完整包含/排除 manifest 留在本地，避免暴露被排除的项目名。manifest 不是额外需要发送的附件。脚本检查明显凭据，但不能判定商业秘密、个人隐私或所有密钥格式；Agent 在指定分享范围内做最终语义检查。

## 目录与 Git

私人库是独立 Git，Skill 更新不覆盖它。本机配置放库外。sources 原文、import 暂存、exports、交接生成文件、锁与事务目录忽略；正式记忆、项目、讨论和合并理由可由 checkpoint 提交。

Git 提供版本和差异；不是加密。记忆内容的当前授权优先于历史记录。并发写入用独占锁和旧文件哈希检查；不在导入时删除快照未包含的内容。
