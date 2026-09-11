# Builds the release file: dist/bl2speed.sdkmod
#
# A .sdkmod is just a zip whose root holds exactly one folder, named the same
# as the file, with __init__.py inside it. Getting that structure wrong is the
# usual reason a mod won't load, so it's done here rather than by hand.
#
# Run with:  python package.py

from __future__ import annotations

import zipfile
from pathlib import Path

MOD_FOLDER = Path(__file__).parent / "bl2speed"
OUTPUT = Path(__file__).parent / "dist" / "bl2speed.sdkmod"

# Files and folders that should never end up in a release.
EXCLUDED_DIRS = {"__pycache__", ".git", ".idea", ".vscode"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    return path.suffix not in EXCLUDED_SUFFIXES


def main() -> None:
    if not (MOD_FOLDER / "__init__.py").is_file():
        raise SystemExit(f"No __init__.py found in {MOD_FOLDER}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(MOD_FOLDER.rglob("*")):
            if path.is_file() and should_include(path.relative_to(MOD_FOLDER.parent)):
                # Stored path keeps the "bl2speed/..." prefix the SDK expects.
                archive.write(path, path.relative_to(MOD_FOLDER.parent).as_posix())

    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    main()
