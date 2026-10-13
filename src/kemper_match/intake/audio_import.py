"""Local audio import.

Takes a file or a folder, validates the format, converts each file to
``songs/<song_id>/original.wav`` with ffmpeg and writes ``metadata.json``
next to it (tags via :mod:`kemper_match.intake.metadata`). The song id must be
stable across re-imports of the same file.
"""

from __future__ import annotations

from pathlib import Path

from kemper_match.project import Project

SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".aac", ".m4a", ".aiff", ".aif"}


def import_audio(project: Project, source: Path) -> list[str]:
    """Import ``source`` (file or folder) and return the song ids created."""
    raise NotImplementedError("audio import (plans/development-plan.md, milestone 2)")
