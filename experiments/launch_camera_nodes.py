"""Compatibility wrapper for ``agilex-gello-software camera-server``."""

import tyro

from agilex_gello_software.commands.camera_server import Args, main

if __name__ == "__main__":
    raise SystemExit(main(tyro.cli(Args)))
