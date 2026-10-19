"""Guitar tone segmentation: where the *tone* changes, independent of song structure.

Frame-level spectral features, change points from feature discontinuities,
merged with the structural boundaries. Output: ``tone_segments.json``.
"""

from __future__ import annotations

from pathlib import Path

from rig_match.project import Project


def segment_tones(project: Project, song_id: str) -> Path:
    raise NotImplementedError("tone segmentation (docs/development-plan.md, milestone 5)")
