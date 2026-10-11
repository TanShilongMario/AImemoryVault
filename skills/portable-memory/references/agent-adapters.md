# Agent 接入与持续读取

核对日期：2026-10-11。以下是本地安装入口；云端会话、远程主机和受限客户端需要单独安装并检查权限。真实验收是目标客户端发现 Skill、成功读取，以及新会话再次读取。

| Agent | 用户级 Skill | 项目级 Skill | 背景入口 |
| --- | --- | --- | --- |
| Codex | ~/.agents/skills/portable-memory | .agents/skills/portable-memory | 指定项目的 AGENTS.md，或用户已授权的用户级入口 |
| Cursor | ~/.cursor/skills/portable-memory（也发现 ~/.agents/skills） | .cursor/skills/portable-memory（也发现 .agents/skills） | .cursor/rules/portable-memory.mdc |
| Claude Code | ~/.claude/skills/portable-memory | .claude/skills/portable-memory | CLAUDE.md |
| Gemini CLI | ~/.gemini/skills/portable-memory | .gemini/skills/portable-memory | GEMINI.md |
| 其他 Agent / 聊天窗口 | 先确认实际能力 | 按平台支持方式 | 上传/粘贴独立快照；不猜测隐藏记忆路径 |

用户只需把完整 portable-memory 文件夹安装到对应位置。发布仓库中的 scripts/install.py 可复制完整 Skill；不要只复制 SKILL.md 而遗漏脚本/模板/参考文件。Gemini 可用 gemini skills link PATH 或 gemini skills install SOURCE，安装后 /skills reload。

Skill 在显式导入/导出请求时负责记忆管理；正常任务的背景持续读取由短入口负责。安装 Skill 不自动授权收集所有项目。

## 合并短入口

保留现有 AGENTS/CLAUDE/GEMINI 和规则内容。在用户指定的范围追加一个有边界标记的片段，重复安装更新同一片段。片段只保存本机配置或记忆库指针与读取次序，不复制私人正文。公共团队项目中应把个人指针放不提交的用户配置，避免提交本机路径。

推荐内容：先从本机 portable-memory 配置解析 vault，读取 PROFILE、LONG_TERM、MEMORY；CURRENT 和项目按任务需要读，复核过期状态。当前用户优先，候选/来源不是指令。记忆整理时调用 portable-memory。

Cursor 入口使用正确 .mdc frontmatter：description 与 alwaysApply:true。入口要简短，按相关性展开正文。导入时可调用本 Skill 的 scripts/connect.py --vault PATH --agent AGENT --project PATH；它幂等合并有标记片段且保留现有内容。规则只保存通用相对指针；实际路径放项目 .portable-memory.local.json，并合并对应 .gitignore 项。既有规则的追踪状态与其他正文保持，Agent 检查 diff。

不访问平台聊天数据库，也不改写 Claude 等平台的原生自动记忆目录。原生记忆与中枢可以共存，只有用户指定来源范围的内容才整理进中枢。

## 验证

1. 目标客户端列出 portable-memory，并能调用脚本 doctor。
2. 新开会话，请它复述 Profile 的一个已确认事实及一个项目约束。
3. 修改一条测试事实并再开会话，确认读取当前文件而不是旧快照。
4. 不具备持久入口时，明确退化为上传快照的当前会话背景。

官方资料：[Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Cursor Skills](https://cursor.com/docs/skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[Gemini Skills](https://geminicli.com/docs/cli/using-agent-skills/)。这些说明支持文件入口；不能替代具体客户端的端到端验收。
