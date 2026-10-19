"""Stem separation with Demucs (CPU).

Writes ``stems/<song_id>/{guitar,vocals,bass,drums,other}.wav``. Stem quality
is the single biggest determinant of everything downstream, so this is the
place to spend effort on model choice (``config.separation_model``) and on
getting a usable guitar stem out of the 4/6-stem models.
"""

from __future__ import annotations

from pathlib import Path

from rig_match.project import Project

STEM_NAMES = ("guitar", "vocals", "bass", "drums", "other")


def separate_song(project: Project, song_id: str) -> dict[str, Path]:
    """Separate one song; return a mapping stem name -> written file."""
    raise NotImplementedError("stem separation (docs/development-plan.md, milestone 3)")
