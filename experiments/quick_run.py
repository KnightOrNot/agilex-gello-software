"""Compatibility wrapper for ``agilex-gello-software quick-run``."""

import tyro

from agilex_gello_software.commands.quick_run import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
