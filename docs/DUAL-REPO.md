# 公开工具与私人记忆

| 仓库 | 内容 | 远程用途 |
| --- | --- | --- |
| 工具库 | Skill、协议、模板、脚本与适配说明 | 公开分发工具 |
| 私人库 | 已整理事实、项目、讨论、合并记录 | 可选，仅受限访问 |

工具库中的 vault/ 和 local/ 被整体忽略；私人库有自己的 `.git`，不是公开库的分支或子模块。用户也可把私人库放工具目录之外。clone 工具不会带走个人记忆。

模板随完整 Skill 安装在 `assets/templates/`；实际路径放本机配置，不写进通用模板。公开 Skill 仓库 AImemoryVault 与用户的私人记忆远程必须分别管理。

## 快照

`checkpoint` 只提交正式路径；遇到已有暂存内容时保留现场并停止，避免混入来源原文。`export` 生成 Markdown 交接快照及本地范围 manifest；二者默认不进入私人 Git。

Git 用于差异、版本和恢复，不提供加密。sources 原文、导出文件、本机配置与事务临时文件被忽略，需额外备份时由用户选择方式。

## 可选私有同步

用户明确选择私人远程后使用 remote、checkpoint、sync。GitHub 在绑定和推送前查验 private 状态；其他服务需要实际访问检查与用户明确确认。公开仓库被拒绝作为记忆远程。

同步检查工作区 → fetch → 比较历史 → 可快进时 merge --ff-only → push。分叉先核实事实并在本地合并，不使用 force push、reset --hard 或按时间覆盖。无后台同步器。

## 并发与恢复

apply、checkpoint、export、sync 使用库内独占锁。apply 在写入前验证旧文件哈希，失败回滚本次修改。多个 Agent 的未验证内容可分目录暂存；正式记忆统一按计划合并。

进程中断后的锁或事务备份先检查和恢复，不直接抢锁。用户要求遗忘时，当前文件删除不代表 Git 历史已消除；历史清理需要明确范围。

操作细节见 [workflows.md](../skills/portable-memory/references/workflows.md)。
