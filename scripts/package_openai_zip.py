#!/usr/bin/env python3
"""Build a plugin ZIP with plugin.json at the archive root."""

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "dist", "__pycache__"}
SKIP_NAMES = {".DS_Store", "photo-gps", "account.json", "preview.json"}


def include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in relative.parts):
        return False
    if path.name in SKIP_NAMES or path.suffix == ".pyc":
        return False
    return path.is_file()


def main() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text())
    version = manifest["version"]
    out_dir = ROOT / "dist"
    out_dir.mkdir(exist_ok=True)
    dest = out_dir / f"file-311-{version}.zip"
    if dest.exists():
        dest.unlink()
    with ZipFile(dest, "w", ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if include(path):
                archive.write(path, path.relative_to(ROOT).as_posix())
    print(dest)


if __name__ == "__main__":
    main()
