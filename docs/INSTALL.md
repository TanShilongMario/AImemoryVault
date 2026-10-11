# 安装与新设备恢复

[完整配置流程](../skills/portable-memory/references/workflows.md)是 Skill 的执行规范；[平台入口](../skills/portable-memory/references/agent-adapters.md)列出安装位置。

## 只安装 Skill

从公开仓库 clone 后运行 `python3 scripts/install.py --agent codex`；可选 cursor、claude-code、gemini-cli。该命令只复制完整 Skill，不创建私人库。项目级安装用 `--scope project --project PATH`。

对 Agent 说“使用 portable-memory 建立我的记忆库”。它会检查依赖、保留已有文件、选择库位置并运行 init、doctor、建立读取入口。默认本地 Git；远程模式使用用户自己的私有库。

## 首次创建

Python 3.9+ 和 Git；无 Python 第三方依赖、无模型 API Key。

```bash
python3 scripts/memory.py --vault /chosen/private-vault init
python3 scripts/memory.py --vault /chosen/private-vault doctor
```

本机配置默认在 `~/.config/portable-memory/config.json`；`--config` 可指定库外位置。已有项目本机配置由 connect 建立，脚本也会从当前项目及祖先目录找到它。配置只记录路径和工具参数，不进入记忆远程。

init 不覆盖已有正式内容，补齐缺少模板、合并忽略规则，仅设置私人库本地 Git 策略。缺少提交身份时使用用户提供的真实作者标签；不改全局 Git 配置。

## 新设备

先安装 Skill，再 clone 自己的私人库到选择的位置，运行 init 重建本机配置、doctor 和读取入口。不要复制另一台设备的绝对路径。无需 Git 历史时，也可建立空库并导入交接文件。

## 无文件/终端能力

生成或消费独立 Markdown，保持同样的筛选、来源与冲突规则。只在当前会话生效时如实报告，不宣称永久记忆或自动同步。
