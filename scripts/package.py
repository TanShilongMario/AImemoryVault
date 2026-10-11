#!/usr/bin/env python3
"""Build a portable Skill ZIP from an explicit public-source allowlist."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills' / 'portable-memory'


def package(destination):
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / 'portable-memory-v0.3.0.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for path in sorted(SOURCE.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                output.write(path, 'portable-memory/' + path.relative_to(SOURCE).as_posix())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / 'SHA256SUMS').write_text(checksum + '  ' + archive.name + '\n')
    print(archive)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    package(parser.parse_args().output)
