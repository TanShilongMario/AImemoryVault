# Agent 安装与背景读取

核对日期：2026-10-11。完整安装位置和验证方法见 [agent-adapters.md](../skills/portable-memory/references/agent-adapters.md)。

```bash
python3 scripts/install.py --agent codex
python3 scripts/install.py --agent cursor
python3 scripts/install.py --agent claude-code
python3 scripts/install.py --agent gemini-cli
```

只安装正在使用的客户端即可。Skill 文件夹自包含，更新与私人记忆分开。

建立指定项目读取入口：

```bash
python3 skills/portable-memory/scripts/connect.py --vault /path/to/private-vault --agent codex --project /path/to/project
```

connect 幂等合并标记片段，保留现有规则；真实绝对路径放被 Git 忽略的 `.portable-memory.local.json`，规则内只有通用相对指针。Agent 在新会话读取项目配置后找到记忆库。

安装、规则创建、成功读取、跨会话复用是不同验证阶段。其他聊天 Agent 可上传快照，不推测其隐藏记忆目录。

官方资料：[Codex](https://learn.chatgpt.com/docs/build-skills)、[Cursor](https://cursor.com/docs/skills)、[Claude Code](https://code.claude.com/docs/en/skills)、[Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/)。
