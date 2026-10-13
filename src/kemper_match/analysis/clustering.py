"""Group equivalent tone segments into reusable tones (tone_A, tone_B, ...).

HDBSCAN first, agglomerative as fallback; auto-label by gain and brightness.
Output: ``tones.json``.
"""

from __future__ import annotations

from pathlib import Path

from kemper_match.project import Project


def cluster_tones(project: Project, song_id: str) -> Path:
    raise NotImplementedError("tone clustering (plans/development-plan.md, milestone 7)")
