"""Software-only checks for the unified command-line dispatcher."""

import json
import sys
from pathlib import Path

import pytest

from agilex_gello_software import cli
from agilex_gello_software.cli import COMMANDS, main


def test_top_level_help(capsys):
    assert main(["--help"]) == 0
    output = capsys.readouterr().out
    for command in COMMANDS:
        assert command in output


def test_unknown_command(capsys):
    assert main(["does-not-exist"]) == 2
    assert "unknown command" in capsys.readouterr().err


def test_upstream_launcher_forwards_options_and_resource_directory(
    tmp_path, monkeypatch
):
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments/launch_nodes.py").write_text(
        "import json, sys\nfrom pathlib import Path\n"
        "Path('result.json').write_text(json.dumps(sys.argv[1:]))\n"
    )
    monkeypatch.setattr(cli, "project_root", lambda: tmp_path)
    previous_cwd, previous_argv = Path.cwd(), sys.argv
    assert main(["launch-nodes", "--robot", "sim_ur"]) == 0
    assert json.loads((tmp_path / "result.json").read_text()) == ["--robot", "sim_ur"]
    assert Path.cwd() == previous_cwd
    assert sys.argv is previous_argv


def test_upstream_launcher_restores_process_state_on_error(tmp_path, monkeypatch):
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments/run_env.py").write_text("raise SystemExit(2)\n")
    monkeypatch.setattr(cli, "project_root", lambda: tmp_path)
    previous_cwd, previous_argv = Path.cwd(), sys.argv
    with pytest.raises(SystemExit) as error:
        main(["run-env", "--bad-option"])
    assert error.value.code == 2
    assert Path.cwd() == previous_cwd
    assert sys.argv is previous_argv
