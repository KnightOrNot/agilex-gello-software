"""Local read command plus direct launchers for unchanged upstream scripts."""

from __future__ import annotations

import contextlib
import importlib
import runpy
import sys
from collections.abc import Sequence
from dataclasses import dataclass

from agilex_gello_software.paths import project_root


@dataclass(frozen=True)
class Command:
    description: str
    script: str | None = None
    extra: str | None = None


COMMANDS = {
    "read": Command("read GELLO joints and gripper"),
    "launch-yaml": Command("launch upstream YAML configuration", "launch_yaml.py"),
    "launch-nodes": Command(
        "launch upstream robot server", "launch_nodes.py", "robots"
    ),
    "camera-server": Command("serve cameras", "launch_camera_nodes.py", "camera"),
    "camera-client": Command(
        "display camera streams", "launch_camera_clients.py", "camera"
    ),
    "quick-run": Command("run upstream quick workflow", "quick_run.py", "full"),
    "run-env": Command("run upstream GELLO environment", "run_env.py", "full"),
}


def _print_help() -> None:
    print("usage: agilex-gello-software COMMAND [OPTIONS]\n")
    for name, command in COMMANDS.items():
        suffix = f" [extra: {command.extra}]" if command.extra else ""
        print(f"  {name:<14} {command.description}{suffix}")
    print("\nRun `agilex-gello-software COMMAND --help` for options.")


def _run_upstream(script: str, args: list[str]) -> int:
    root = project_root()
    path = root / "experiments" / script
    if not path.is_file():
        raise RuntimeError(f"Upstream script not found: {path}")
    original_argv = sys.argv
    try:
        sys.argv = [str(path), *args]
        # Upstream scripts intentionally keep their original relative resources.
        with contextlib.chdir(root):
            runpy.run_path(str(path), run_name="__main__")
    finally:
        sys.argv = original_argv
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        _print_help()
        return 0
    name = args.pop(0)
    command = COMMANDS.get(name)
    if command is None:
        print(f"agilex-gello-software: unknown command: {name!r}", file=sys.stderr)
        _print_help()
        return 2
    try:
        if command.script is None:
            return importlib.import_module("agilex_gello_software.commands.read").main(
                args
            )
        return _run_upstream(command.script, args)
    except ModuleNotFoundError as exc:
        hint = f"; install `uv sync --extra {command.extra}`" if command.extra else ""
        print(
            f"agilex-gello-software {name}: missing {exc.name!r}{hint}", file=sys.stderr
        )
        return 1
    except (OSError, RuntimeError) as exc:
        print(f"agilex-gello-software {name}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
