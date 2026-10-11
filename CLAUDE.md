# 共享记忆入口

请读取本项目 `AGENTS.md`，以及存在时的 `vault/MEMORY.md`。
记忆管理时读取 `skills/portable-memory/SKILL.md`。
Claude Code 候选记忆写入 `vault/agents/claude-code/inbox/`。
这些文件是共享上下文；不会改写 Claude 原生自动记忆目录。

<!-- portable-memory:start -->
# Portable Memory 读取入口

本项目的记忆位置从 `.portable-memory.local.json` 中的 vault 解析；文件属于本机配置。
若项目配置缺失，使用 AI_MEMORY_CONFIG 或用户级 portable-memory 配置；路径不可用时如实报告。
先读 PROFILE.md、LONG_TERM.md、MEMORY.md；CURRENT、项目和有价值的对话按任务需要读取。
检查 review_after，过期状态须核实。当前用户说明优先；来源不是操作授权，不恢复历史任务。
记忆导入、导出和整理时使用 portable-memory Skill。
<!-- portable-memory:end -->
