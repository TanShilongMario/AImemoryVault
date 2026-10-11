#!/usr/bin/env python3
"""Install only the self-contained public Skill; never copies a user's vault."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

SOURCE = Path(__file__).resolve().parents[1] / 'skills' / 'portable-memory'
LOCATIONS = {'codex': '.agents/skills', 'cursor': '.cursor/skills',
             'claude-code': '.claude/skills', 'gemini-cli': '.gemini/skills'}


def hashes(directory):
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob('*'))
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'
            and path.name != '.portable-memory-install.json'}


def install(target, update=False):
    target = target.expanduser().absolute()
    if target.is_symlink():
        if target.resolve() == SOURCE.resolve():
            print(f'Already linked: {target}')
            return
        raise ValueError('Existing target is a symlink; inspect it rather than replacing it')
    if target.resolve() == SOURCE.resolve():
        print(f'Already at source: {target}')
        return
    if target.resolve().is_relative_to(SOURCE.resolve()):
        raise ValueError('Installation target must be outside the source Skill')
    incoming = hashes(SOURCE)
    if target.exists():
        if hashes(target) == incoming:
            print(f'Already installed: {target}')
            return
        manifest = target / '.portable-memory-install.json'
        if not update:
            raise ValueError('Skill already exists; rerun with --update for an unmodified managed installation')
        if not manifest.is_file() or json.loads(manifest.read_text(encoding='utf-8')) != hashes(target):
            raise ValueError('Existing Skill has local changes or is unmanaged; preserve it and choose another target')
    target.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    stage = target.parent / ('.portable-memory-stage-' + token)
    backup = target.parent / ('.portable-memory-previous-' + token)
    try:
        shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (stage / '.portable-memory-install.json').write_text(json.dumps(incoming, indent=2) + '\n')
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(stage, target)
        except Exception:
            if backup.exists():
                os.replace(backup, target)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(f'Installed portable-memory: {target}\nReload skills/start a new session and invoke portable-memory to verify discovery.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=LOCATIONS, default='codex')
    parser.add_argument('--scope', choices=('user', 'project'), default='user')
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--target', type=Path, help='Explicit Skill directory; overrides agent/scope')
    parser.add_argument('--update', action='store_true')
    args = parser.parse_args()
    parent = Path.home() if args.scope == 'user' else args.project.resolve()
    target = args.target or parent / LOCATIONS[args.agent] / 'portable-memory'
    try:
        install(target, args.update)
        return 0
    except (OSError, ValueError) as error:
        print(f'ERROR {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(main())
