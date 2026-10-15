# Repository Guidelines

## Project Structure & Responsibilities

`gello/`, `experiments/`, `scripts/`, `configs/`, `ros2/`, and hardware assets preserve the pinned upstream tree. `third_party/DynamixelSDK` and Menagerie retain upstream revisions. Do not rename upstream imports or patch these files for an installation. README, local docs, uv configuration, Python version, and uv CI describe this fork; declared upstream overrides are recorded in `src/agilex_gello_software/upstream.json`.

Put application-facing extensions in `src/agilex_gello_software/`: agent/config adapters, driver lifecycle policy, local read command, and script dispatch. Reuse upstream methods without global monkey patches. `tests/` verifies adapters with fake hardware. Preserve historical generated configurations under the local package's `configs/legacy/`.

Client composition, follower mapping, JS positioning, recording, and process management belong to agilex-controller; alignment/conversion belongs to lerobot-converter. Neither application is a library dependency.

## Build, Test, and Development Commands

Use Python 3.11 and uv from this repository root. Initialize the upstream DynamixelSDK before syncing.

- `uv sync --frozen`: install local packages and the pinned SDK source.
- `uv run --frozen agilex-gello-software --help`: inspect the CLI.
- `uv run --frozen pytest`: run hardware-free adapter regressions.
- `uv run --frozen ruff check src tests`: lint local code.
- `uv run --frozen ruff format --check src tests`: check local formatting.
- `uv run --frozen ruff check gello experiments scripts --select E9,F63,F7,F82`: check upstream syntax/name errors.
- `uv run --frozen python -m agilex_gello_software.upstream`: audit pinned files and initialized submodules offline.
- `uv build`: build both Python namespaces through Hatchling.

## Coding & Testing Guidelines

Use four spaces, annotated public interfaces, snake_case functions/modules, and PascalCase classes. Never reformat upstream files. Tests use `test_*.py`; no coverage threshold is configured. Default pytest excludes real-device diagnostics under `gello/`.

Real adapters must reject fake fallback, busy ports, stale feedback, and initialization failure. Bound reads and cleanup; never kill port owners or change permissions automatically. Keep calibration, gripper, multi-turn, and filtering parity with upstream. Hardware verification requires operator confirmation. Native `gello.*` retains its original behavior; local policies apply only to the adapter.

## Commits & Pull Requests

Honor requests to validate before committing. Prefer conventional imperative subjects and report upstream changes, checks, hardware status, and compatibility. Publish tested submodule commits before updating parent gitlinks. Independent checkouts do not synchronize automatically. Keep licenses and notices; exclude environments, caches, datasets, and build outputs.
