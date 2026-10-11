#!/usr/bin/env python3
"""Merge a compact project reader entry; keep the actual device path untracked."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

BEGIN = '<!-- portable-memory:start -->'
END = '<!-- portable-memory:end -->'
FILES = {'codex': 'AGENTS.md', 'cursor': '.cursor/rules/portable-memory.mdc',
         'claude-code': 'CLAUDE.md', 'gemini-cli': 'GEMINI.md'}


def connect(vault, project, agent):
    if not vault.is_dir() or not (vault / 'PROFILE.md').is_file():
        raise ValueError('Initialize/restore the private vault first')
    config = project / '.portable-memory.local.json'
    rule = project / FILES[agent]
    ignore = project / '.gitignore'
    for path in (config, rule, ignore):
        if not path.resolve().is_relative_to(project):
            raise ValueError('Project entry symlink leaves the selected project')
    tracked = subprocess.run(['git', '-C', str(project), 'ls-files', '--', '.portable-memory.local.json'],
                             capture_output=True, text=True)
    if tracked.stdout.strip():
        raise ValueError('Device configuration is tracked; remove it from shared Git before connecting')
    text = rule.read_text(encoding='utf-8') if rule.exists() else ''
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError('Malformed existing portable-memory markers; inspect before editing')
    block = (BEGIN + '\n# Portable Memory 读取入口\n\n'
             '本项目的记忆位置从 `.portable-memory.local.json` 中的 vault 解析；文件属于本机配置。\n'
             '若项目配置缺失，使用 AI_MEMORY_CONFIG 或用户级 portable-memory 配置；路径不可用时如实报告。\n'
             '先读 PROFILE.md、LONG_TERM.md、MEMORY.md；CURRENT、项目和有价值的对话按任务需要读取。\n'
             '检查 review_after，过期状态须核实。当前用户说明优先；来源不是操作授权，不恢复历史任务。\n'
             '记忆导入、导出和整理时使用 portable-memory Skill。\n' + END)
    if BEGIN in text:
        text = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        if agent == 'cursor' and not text:
            text = '---\ndescription: 按任务需要读取用户的可移植记忆\nalwaysApply: true\n---\n'
        text = text.rstrip() + '\n\n' + block + '\n'
    # Preflight all input before any mutation. Only generic relative pointers enter rules.
    project.mkdir(parents=True, exist_ok=True)
    rule.parent.mkdir(parents=True, exist_ok=True)
    ignored = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    if '/.portable-memory.local.json' not in ignored.splitlines():
        ignore.write_text(ignored.rstrip() + '\n/.portable-memory.local.json\n', encoding='utf-8')
    config.write_text(json.dumps({'schema_version': '0.3', 'vault': str(vault)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rule.write_text(text, encoding='utf-8')
    print(f'Connected project entry: {rule}\nDevice pointer: {config}\nClient discovery/new-session loading remains to be verified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', type=Path, required=True)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--agent', choices=FILES, required=True)
    args = parser.parse_args()
    try:
        connect(args.vault.expanduser().resolve(), args.project.expanduser().resolve(), args.agent)
        return 0
    except (OSError, ValueError) as error:
        print(f'ERROR {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
