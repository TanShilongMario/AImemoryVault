# Portable Memory · AImemoryVault

[中文](#中文) · [English](#english)

## 中文

在不同设备、不同 Agent 之间带走自己的记忆。安装一次 Skill，日常只需说 **“导出记忆”** 或 **“导入记忆”**。

通过 Markdown 交换记忆，使用本地 Git 保存快照，也可连接自己的私有远程库。无需模型 API Key 或第三方 Python 依赖。

默认导出 **Profile + 长期记忆 + 近期项目 + 有保留价值的对话摘要**。它会保留已确认事实、项目约束、重要纠正、决策理由与未解决问题，并标明来源和确认状态。无需搬运全部聊天记录。

### 让 Agent 安装

把下面这段交给有文件与终端能力的 Agent：

> 从 https://github.com/TanShilongMario/AImemoryVault 安装 portable-memory Skill。先阅读 README 和 skills/portable-memory/SKILL.md，把完整 Skill 安装到你支持的用户级目录，保留已有安装。首次使用时引导我创建或接入私人记忆库，默认本地 Git，可选私有远程；公开 Skill 仓库不是我的私人记忆远程。已有记忆、配置与项目规则不要覆盖。完成 doctor 检查，并在我指定的范围建立记忆读取入口，报告实际验证结果。然后按我的请求导入或导出记忆。

只有普通聊天窗口时，也可以按协议生成/读取 Markdown 附件；生效范围取决于平台能力。

### 手动安装

需要 Python 3.9+ 与 Git：

```bash
git clone https://github.com/TanShilongMario/AImemoryVault.git
cd AImemoryVault
python3 scripts/install.py --agent codex
```

将 codex 换成 cursor、claude-code 或 gemini-cli 即可。项目安装用 `--scope project --project /path/to/project`。安装脚本只复制 `skills/portable-memory/`，不会复制任何用户记忆。已有安装相同则不变；`--update` 只更新未被本地修改的受管安装。

安装后重新加载 Skill 或新开会话，提出：

> 使用 portable-memory 帮我建立记忆库。

> 导出我的记忆，包含 Profile、长期记忆、最近的项目和有保留价值的讨论。

> 导入这份记忆，核实冲突并让后续会话能继续读取。

### 开发者用法

以下显式选择一个私人库路径；安装后的脚本也可从本机配置找到它：

```bash
python3 scripts/memory.py --vault /path/to/private-vault init
python3 scripts/memory.py --vault /path/to/private-vault doctor
python3 scripts/memory.py --vault /path/to/private-vault export --preview
python3 scripts/memory.py --vault /path/to/private-vault export
python3 scripts/memory.py --vault /path/to/private-vault import /path/to/MEMORY.md
```

脚本负责确定性文件操作；**提炼记忆、判断价值、去敏、冲突核实由 Skill 驱动 Agent 完成**。import 暂存后，Agent 用带旧内容哈希的合并计划 apply，再 checkpoint；不是把来源文本自动当成事实。

默认近期窗口 30 天，可调整；另纳入活跃项目、明确保留的内容和未解决讨论。旧文件无元数据时由 Agent 判断，不用复制时间冒充更新日期。候选、原文、本机配置与 local-only 内容不默认导出。

### 存储与跨设备

```text
公开工具仓库                          用户自己的私人库（独立 Git）
skills/portable-memory/                PROFILE.md / LONG_TERM.md
  SKILL.md                             CURRENT.md / MEMORY.md
  scripts/                             projects/ / conversations/
  references/                          inbox/ / decisions/
  assets/templates/                    sources/ / exports/（忽略）
```

私人库可以在任何获准目录，不依赖 Skill 安装路径。这个工作区保留的 `vault/` 与 `local/` 被工具 Git 忽略，clone 公开工具不会携带它们。

本地 Git 提供版本、差异和恢复；跨设备可用导出文件，或用户自己的私有远程。GitHub 私有同步使用已认证 gh 验证可见性；同步只快进，分叉须核实合并。没有后台任务或自动扫描聊天数据库。

Git 是版本管理，不是加密；文件附件也需要按分享对象选择范围。目标 Agent 持久读取需要接入入口与新会话验证，安装成功不等于所有客户端已验收。

### 文档与验证

[新设备安装](docs/INSTALL.md) · [记忆协议](docs/MEMORY-FORMAT.md) · [分层与选择](docs/MEMORY-LAYERS.md) · [Agent 接入](docs/AGENT-PATHS.md) · [Git 与双库](docs/DUAL-REPO.md)

```bash
python3 -m unittest discover -s tests -v
```

v0.3：自包含 Skill、保留已有数据的环境配置、可选择的导出、哈希检查与锁保护合并、私人 Git checkpoint、私有远程检查与快进同步。脚本功能通过自动测试；实际客户端发现与跨会话加载须在对应产品中验证。

MIT License。公开仓库只发布通用工具、协议和空白模板。

---

## English

Take your memory with you across devices and agents. Install the Skill once, then ask your agent to **“export my memory”** or **“import this memory.”**

Exchange memory as Markdown, keep local Git snapshots, and optionally sync with your own private remote repository. No model API key or third-party Python dependencies required.

The default export includes **Profile + long-term memory + recent projects + conversation summaries worth keeping**. It preserves confirmed facts, project constraints, important corrections, decision rationale, and unresolved questions, with sources and confirmation status. You do not need to transfer your entire chat history.

### Ask your agent to install it

Give this prompt to an agent with filesystem and terminal access:

> Install the portable-memory Skill from https://github.com/TanShilongMario/AImemoryVault. Read README and skills/portable-memory/SKILL.md first. Install the complete Skill in your supported user-level directory, preserving any existing installation. On first use, guide me through creating or connecting a private memory vault, using local Git by default and an optional private remote. The public Skill repository is not my private memory remote. Preserve existing memory, configuration, and project rules. Run doctor, configure a memory-reading entry point within the scope I specify, and report what you actually verified. Then import or export memory as I request.

In a regular chat interface, you can also generate or read Markdown attachments using the same protocol. How long that context remains available depends on the platform.

### Manual installation

Requires Python 3.9+ and Git:

```bash
git clone https://github.com/TanShilongMario/AImemoryVault.git
cd AImemoryVault
python3 scripts/install.py --agent codex
```

Replace `codex` with `cursor`, `claude-code`, or `gemini-cli` as needed. For a project-level installation, add `--scope project --project /path/to/project`. The installer copies only `skills/portable-memory/`, without any user memory. Identical existing installations are left unchanged; `--update` updates only managed installations that have no local modifications.

After installation, reload skills or start a new session and ask:

> Use portable-memory to help me set up my memory vault.

> Export my memory, including my Profile, long-term memory, recent projects, and discussions worth keeping.

> Import this memory, check conflicts, and make it available for future sessions.

### Developer usage

These commands explicitly select a private vault path. Installed scripts can also resolve it from local configuration:

```bash
python3 scripts/memory.py --vault /path/to/private-vault init
python3 scripts/memory.py --vault /path/to/private-vault doctor
python3 scripts/memory.py --vault /path/to/private-vault export --preview
python3 scripts/memory.py --vault /path/to/private-vault export
python3 scripts/memory.py --vault /path/to/private-vault import /path/to/MEMORY.md
```

Scripts handle deterministic file operations. **The Skill guides the agent in extracting useful memory, assessing its value, removing sensitive details, and checking conflicts.** Import stages incoming material for review. The agent then uses `apply` with a merge plan containing hashes of the previous contents, followed by `checkpoint`. Imported text is treated as source material until reviewed.

The default recent-history window is 30 days and can be adjusted. Active projects, explicitly retained content, and unresolved discussions are also included. The agent assesses older files without metadata; file-copy timestamps are not treated as meaningful update dates. Candidates, raw source material, local configuration, and `local-only` content are excluded from default exports.

### Storage and moving between devices

```text
Public tool repository                Your private vault (independent Git)
skills/portable-memory/                PROFILE.md / LONG_TERM.md
  SKILL.md                            CURRENT.md / MEMORY.md
  scripts/                            projects/ / conversations/
  references/                         inbox/ / decisions/
  assets/templates/                   sources/ / exports/ (ignored)
```

Your private vault can live in any authorized directory, independently of the Skill installation. The tool repository ignores the workspace's `vault/` and `local/` directories, so cloning the public repository does not include their contents.

Local Git provides version history, diffs, and recovery. Move between devices using exported files or your own private remote. Private GitHub sync uses authenticated `gh` to verify repository visibility. Sync allows fast-forward updates only; divergent histories require a reviewed merge. There are no background jobs or automatic scans of native chat databases.

Git provides version control, not encryption. Choose attachment contents according to whom you intend to share them with. Persistent reading by a target agent requires a configured entry point and verification in a new session. Successful installation alone does not verify every client integration.

### Documentation and validation

Detailed guides are currently in Chinese:

[New-device setup](docs/INSTALL.md) · [Memory protocol](docs/MEMORY-FORMAT.md) · [Memory layers and selection](docs/MEMORY-LAYERS.md) · [Agent integration](docs/AGENT-PATHS.md) · [Git and repository isolation](docs/DUAL-REPO.md)

```bash
python3 -m unittest discover -s tests -v
```

v0.3 includes a self-contained Skill, setup that preserves existing data, selective exports, merges protected by hash checks and locks, private Git checkpoints, private-remote verification, and fast-forward sync. Script functionality is covered by automated tests; skill discovery and loading across sessions must be verified in each client.

MIT License. The public repository contains only general-purpose tools, protocols, and blank templates.
