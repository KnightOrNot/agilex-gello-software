"""Compatibility wrapper for ``agilex-gello-software run-env``."""

import tyro

from agilex_gello_software.commands.run_env import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
