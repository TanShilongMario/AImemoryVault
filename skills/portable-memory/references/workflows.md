# 配置与事务流程

下面的 M 指本 Skill 内 scripts/memory.py 的实际路径。Python 3.9+、Git 为本地模式所需；GitHub 私有同步还需已认证 gh 或等效连接器。

## 首次配置 / 新设备

1. 检查 Python、Git、文件权限、已有本机配置和用户提供的库位置。缺少依赖时说明具体缺项并使用可用安装方式；不擅自修改系统全局设置。
2. 已有库先读取并保留；不把本机旧登记路径当成新设备实际路径。未指定位置时建议 ~/.local/share/portable-memory/vault，或当前用户明确选择的目录。默认本地 Git，可在之后加私有远程。
3. 初始化：

```bash
python3 M --vault /chosen/private-vault init
python3 M doctor
```

init 创建缺少的模板与独立 Git，保留已有正式文件，合并必需忽略项，仅设置当前库的 Git 策略。本机配置默认 ~/.config/portable-memory/config.json，--config 可指定库外位置。身份从现有 Git 配置读取；缺失时请用户提供实际作者标签，仅设仓库级配置，不臆造姓名或邮箱。

4. 读取现有 Profile。有足够背景就直接工作；首次空库只针对影响工作的未知项询问。初次快照可为空白背景，不编造个人资料。
5. 按 agent-adapters.md 创建用户指定范围的读取入口并验证；配置文件存在不等于客户端已经发现或读到。

## 私有远程 / 恢复

Skill 发布仓库和用户记忆远程用途不同。用户给出私人库地址后验证访问范围：GitHub 使用 gh api repos/OWNER/REPO --jq .private；连接器需返回同等证据。URL/名称不能证明私有。不得把默认公开 Skill 仓库设置成私人 origin。

GitHub 路径：

```bash
python3 M remote https://github.com/OWNER/PRIVATE-REPO.git
python3 M checkpoint
python3 M sync
```

remote 在绑定前查询私有状态；缺少认证先引导登录。sync 再次验证可见性并检查工作区、fetch、比较历史、只快进、push。分叉时停止同步并保留两边，在本地核实事实与合并，禁止 force push、reset --hard 或按时间全覆盖。

其他 Git 服务：验证其受限访问机制并取得用户明确确认后才使用 remote URL --private-confirmed。该参数是用户确认的记录，不是跳过隐私检查的默认选项。脚本从不创建云端账号或代替用户决定仓库可见性。创建私有库可用平台原生工具/连接器完成；不要打印凭据。

新设备先安装 Skill，再 clone 用户指定私人库到选择的位置；若目标已有内容则比较或选择另一目录，不覆盖。然后对该路径运行 init 重建库外本机配置、doctor 与读取入口。只需交接且不需要历史时可创建空库并导入快照。

如果环境只能使用 GitHub 连接器同步：核对远程私有状态、准确父提交、内容 diff，只提交私人库的正式文件；保留本地提交与远程对象的一致性证据。不要把“API 上传成功”当成本机 Git 认证成功。

## 导入和合并计划

import 只暂存。完整 Skill 任务还包括比对、合并、checkpoint、目标 Agent 接入。使用 inventory 得到现有内容 SHA-256；新文件的 base_sha256 为 null。

```bash
python3 M inventory
python3 M apply /local/merge-plan.json --preview
python3 M apply /local/merge-plan.json
```

计划在库外或被忽略的本机目录创建，内容是完整新文件正文，不是需要执行的代码：

```json
{
  "schema_version": "0.3",
  "changes": [
    {
      "path": "conversations/example.md",
      "base_sha256": null,
      "content": "---\nschema_version: 0.3\nkind: canonical\nupdated: 2026-01-01\nretain: true\nstatus: unresolved\n---\n# 一个待讨论问题\n\n- [discussion-001] 已提出的选择及下一步核实事项。\n  - scope: project/example\n  - source: 用户本次讨论，2026-01-01\n  - status: unresolved\n  - updated: 2026-01-01\n",
      "reason": "保留尚未定论但需要继续讨论的问题；不写成用户决定"
    }
  ]
}
```

写计划前重读现有正文，保持未修改条目。apply 校验所有路径、哈希、格式、明显凭据和理由，在锁内写入；失败回滚本次文件修改。合并记录保存在 decisions/，事务临时备份不进入 Git。冲突内容留候选，不按更新日期自动判断真伪。未定论的讨论可以正式保存为“讨论”，而不是已确认事实。

锁冲突时检查所属进程；不直接抢锁。进程崩溃后若 .transactions 留有内容，先查看备份并恢复/核对文件，再重试；不盲删锁与备份。手工编辑同样遵守独占写入和写前重读。

## 导出和版本

```bash
python3 M export --preview
python3 M export
python3 M export --include projects/example.md
python3 M export --handoff
python3 M checkpoint --message 'Update portable memory'
```

export 只打包已有正式文件，Agent 先完成语义整理，尤其核对 MEMORY.md 是否有尚未归入其他层的独有事实；将可分享部分保留到对应层后再导出。默认窗口可在配置 recent_days 或参数 --recent-days 调整。Profile/长期之外的缺省筛选见 memory-format.md。

生成文件会移除常见本机路径并拒绝明显凭据，但必须按用户的分享对象/范围检查正文。--all 仍不包含 raw sources 或候选。checkpoint 只暂存正式路径；已有 staged 变更时停下来保留其状态，不混入用户先前暂存内容。

命令成功后简短报告：实际读取覆盖、纳入主题、保留的不确定项、文件路径、Git commit 与同步是否完成。目标平台的永久记忆能力不由本脚本保证。

## 无文件/终端环境

使用同样的分层和筛选规则，生成独立 Markdown 或消费上传文件。先复述必要背景，保留当前用户优先与不恢复历史任务的约束。只能当前会话生效就明确说明，不声称自动写入永久记忆。
