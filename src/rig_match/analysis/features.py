"""Per-segment tone descriptors (spectral, dynamic, distortion, musical), normalised 0-1.

Output: ``features.json``, one vector per tone segment. The same descriptors
must be computable for a rendered rig so that search can compare like with like.
"""

from __future__ import annotations

from pathlib import Path

from rig_match.project import Project


def extract_features(project: Project, song_id: str) -> Path:
    raise NotImplementedError("feature extraction (docs/development-plan.md, milestone 6)")
