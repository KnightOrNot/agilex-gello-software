# Repository Guidelines

## Project Structure & Responsibilities

`src/agilex_gello_software/` provides GELLO agents, Dynamixel access, device calibration, robot abstractions, and generic upstream commands. `configs/`, `experiments/`, and `scripts/` contain configuration examples and upstream tools. `tests/` contains hardware-free regressions; `ros2/` has a separate ROS2 workflow. Preserve reference images in `imgs/` and the Menagerie submodule in `third_party/`.

PiPER-X client composition, follower mapping, JS positioning, following, and raw recording belong to agilex-controller. Alignment and dataset conversion belong to lerobot-converter. Keep those applications out of this library's dependencies. Pass installation calibration through `DynamixelRobotConfig`; do not repurpose an upstream port-map entry for one installation.

## Build, Test, and Development Commands

Use Python 3.11 and uv from this repository root.

- `uv sync --frozen`: install the base package and development tools.
- `uv run --frozen agilex-gello-software --help`: list commands without hardware access.
- `uv run --frozen pytest`: run the configured `tests/` suite with fake hardware.
- `uv run --frozen ruff check src tests experiments scripts --select E9,F63,F7,F82`: match Python CI lint.
- `uv build`: build distributions.

Optional tools require the corresponding `camera`, `simulation`, `robots`, or `full` extra. Simulation assets require submodule initialization. See `docs/installation.md` before running hardware commands.

## Coding & Testing Guidelines

Use four spaces, snake_case functions/modules, PascalCase classes, and annotations for new public interfaces. Preserve upstream formatting and avoid unrelated changes. Legacy pre-commit hooks exist; they are separate from CI's limited Ruff checks.

Name tests `test_*.py`. No coverage threshold is configured. Mock serial access and exercise failure and cleanup paths. Default pytest excludes hardware diagnostics under `src/`. Real-device verification requires operator confirmation. Real robot initialization must report errors rather than silently use fake state, and acquired drivers must close after initialization failure or normal exit.

## Commits & Pull Requests

Use concise imperative subjects, preferably conventional prefixes. Describe behavior, upstream compatibility, checks, hardware-validation status, and related issues. Update reference docs and CHANGELOG with behavior changes. Retain MIT notices and third-party attribution.

Standalone and controller submodule checkouts are independent. Publish tested library commits before updating the parent gitlink. Never commit environments, build artifacts, egg metadata, or collected data.
