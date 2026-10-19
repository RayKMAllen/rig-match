"""Song structure detection (intro / verse / chorus / bridge / solo / outro).

Self-similarity matrix + novelty curve on the guitar stem, boundaries by
peak-picking, labels by heuristics. Output: ``sections.json``.
"""

from __future__ import annotations

from pathlib import Path

from rig_match.project import Project


def detect_sections(project: Project, song_id: str) -> Path:
    raise NotImplementedError("structure detection (docs/development-plan.md, milestone 4)")
