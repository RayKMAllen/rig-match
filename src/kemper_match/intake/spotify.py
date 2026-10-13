"""Spotify playlist import. Metadata only: title, artist, album, track order.

Audio is never fetched from Spotify; the user supplies audio files separately
and metadata is matched to them.
"""

from __future__ import annotations

from kemper_match.project import Project


def import_playlist(project: Project, url: str) -> list[dict[str, str]]:
    raise NotImplementedError("Spotify playlist metadata import (plans/development-plan.md, milestone 2)")
