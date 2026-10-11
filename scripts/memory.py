#!/usr/bin/env python3
"""Compatibility entrypoint; the distributable Skill owns the implementation."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
if not any(arg == flag or arg.startswith(flag + '=') for arg in sys.argv for flag in ('--root', '--vault')):
    sys.argv[1:1] = ['--root', str(ROOT)]
runpy.run_path(str(ROOT / 'skills/portable-memory/scripts/memory.py'), run_name='__main__')
