# Builds the release file:
#   dist/bl2speed.sdkmod  - for the new SDK (willow2-mod-manager)
#
# Pass --legacy to also build dist/bl2speed.zip for the old SDK. That build
# isn't shipped yet because the old-SDK code path hasn't been tested on a real
# install, so it isn't advertised as supported.
#
# Both hold the same thing: a zip whose root contains exactly one folder,
# named the same as the file, with __init__.py inside it. Getting that
# structure wrong is the usual reason a mod won't load, so it's done here
# rather than by hand.
#
# Run with:  python package.py [--legacy]

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
MOD_FOLDER = ROOT / "bl2speed"
DIST = ROOT / "dist"

# Build leftovers that should never end up in a release.
EXCLUDED_DIRS = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(relative_path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in relative_path.parts):
        return False
    return relative_path.suffix not in EXCLUDED_SUFFIXES


def check_versions_match() -> str:
    """Make sure _config.py and pyproject.toml agree before shipping."""
    config_text = (MOD_FOLDER / "_config.py").read_text(encoding="utf-8")
    config_match = re.search(r'^VERSION\s*=\s*"([^"]+)"', config_text, re.MULTILINE)

    pyproject_text = (MOD_FOLDER / "pyproject.toml").read_text(encoding="utf-8")
    pyproject_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.MULTILINE)

    if config_match is None or pyproject_match is None:
        raise SystemExit("Could not read the version out of _config.py or pyproject.toml")

    if config_match.group(1) != pyproject_match.group(1):
        raise SystemExit(
            f"Version mismatch: _config.py says {config_match.group(1)},"
            f" pyproject.toml says {pyproject_match.group(1)}",
        )
    return config_match.group(1)


def build(output: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            # Stored path keeps the "bl2speed/..." prefix the SDKs expect.
            archive.write(path, path.relative_to(MOD_FOLDER.parent).as_posix())
    print(f"Built {output}")


def main() -> None:
    if not (MOD_FOLDER / "__init__.py").is_file():
        raise SystemExit(f"No __init__.py found in {MOD_FOLDER}")

    version = check_versions_match()

    files = [
        path
        for path in sorted(MOD_FOLDER.rglob("*"))
        if path.is_file() and should_include(path.relative_to(MOD_FOLDER.parent))
    ]

    DIST.mkdir(parents=True, exist_ok=True)
    build(DIST / "bl2speed.sdkmod", files)

    if "--legacy" in sys.argv:
        build(DIST / "bl2speed.zip", files)

    print(f"Version {version}")


if __name__ == "__main__":
    main()
