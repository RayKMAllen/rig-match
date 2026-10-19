"""The project's own rig index (SQLite at ``rigs/rigs.db``).

Sources, in order of usefulness:

1. Rig Manager library databases (``repositoryR2.db``), read with
   :mod:`rig_match.rigs.rigmanager`. These already carry rich metadata
   (amp name, cab, gain, author ...), so this is the primary path.
2. Loose ``.krig`` / ``.kipr`` files, parsed with :mod:`rig_match.rigs.parser`.
3. Manual tags.
"""

from __future__ import annotations

from pathlib import Path

from rig_match.project import Project


def import_rigs(project: Project, source: Path) -> int:
    """Index every rig found under ``source``; return how many rows were written."""
    raise NotImplementedError("rig library indexing (docs/development-plan.md, milestone 8)")
