"""Candidate rig search and ranking for each detected tone.

amp-family classification -> gain classification -> feature similarity, combined
with the weights below. Output: ``recommendations.json`` (top N per tone).
"""

from __future__ import annotations

from pathlib import Path

from rig_match.project import Project

RANKING_WEIGHTS = {
    "amp_family_match": 0.30,
    "gain_match": 0.25,
    "spectral_match": 0.25,
    "transient_match": 0.10,
    "user_history": 0.10,
}

GAIN_CATEGORIES = ("clean", "edge", "crunch", "hard_rock", "high_gain", "extreme")


def recommend_rigs(project: Project, song_id: str) -> Path:
    raise NotImplementedError("rig search and ranking (docs/development-plan.md, milestone 9)")
