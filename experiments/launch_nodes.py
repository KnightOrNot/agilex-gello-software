"""Compatibility wrapper for ``agilex-gello-software launch-nodes``."""

import tyro

from agilex_gello_software.commands.launch_nodes import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
