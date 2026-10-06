"""Compatibility wrapper for ``agilex-gello-software follow-record``."""

from agilex_gello_software.commands.follow_record import _sample_from_cycle, main

__all__ = ["_sample_from_cycle", "main"]
if __name__ == "__main__":
    raise SystemExit(main())
