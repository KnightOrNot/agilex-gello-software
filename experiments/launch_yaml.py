"""Compatibility wrapper for ``agilex-gello-software launch-yaml``."""

import tyro

from agilex_gello_software.commands.launch_yaml import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
