"""Offline integrity check for the pinned upstream source and SDK checkout."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from agilex_gello_software.paths import project_root


def verify_checkout(root: Path) -> list[str]:
    manifest = json.loads(Path(__file__).with_suffix(".json").read_text())
    errors = []
    for relative, expected in manifest["files"].items():
        if relative in manifest["overrides"]:
            continue
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing upstream file: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
            errors.append(f"Modified upstream file: {relative}")
        elif bool(path.stat().st_mode & 0o111) != (expected["mode"] == "100755"):
            errors.append(f"Changed upstream executable mode: {relative}")
    for relative, revision in manifest["submodules"].items():
        path = root / relative
        if not (path / ".git").exists():
            if relative.endswith("DynamixelSDK"):
                errors.append(f"Missing required submodule checkout: {relative}")
            continue  # Simulation assets are optional.
        head = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()
        if head != revision:
            errors.append(f"Wrong upstream submodule revision: {relative}: {head}")
        changed = subprocess.run(
            ["git", "-C", str(path), "diff", "--quiet", "HEAD", "--"], check=False
        )
        if changed.returncode:
            errors.append(f"Modified upstream submodule: {relative}")
    return errors


def main() -> int:
    errors = verify_checkout(project_root())
    if errors:
        print("\n".join(errors))
        return 1
    print("Pinned upstream files and submodules match; declared overrides excluded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
