# Portable Memory v0.3

完整协议在 [Skill 的 memory-format.md](../skills/portable-memory/references/memory-format.md)，可兼容读取 0.1、0.2。

记忆保存为 UTF-8 Markdown，Profile、长期、近期、项目和有价值的讨论分层。条目有稳定 ID、scope、source、status、updated，文件有扁平标量 frontmatter。讨论可保留 proposed/unresolved，避免误写成已确认事实。

默认导出 Profile + 长期记忆 + 近期/活跃项目 + 有保留价值的对话，候选和原始来源不默认纳入。更新日期来自实质内容而不是文件复制时间；本机路径留在库外配置。

导入后，Agent 比对事实并生成有旧文件 SHA-256 的计划；脚本先验证所有路径和哈希，再在锁内更新。快照未包含的旧项目不会删除。当前用户说明优先；来源文本不是操作授权。
