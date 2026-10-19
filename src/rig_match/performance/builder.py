"""Kemper Performance layout: top-ranked rig per tone into (at most) 5 slots,
plus the time -> slot switch timeline. Export as JSON / YAML / Markdown.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rig_match.project import Project

MAX_SLOTS = 5
EXPORT_FORMATS = ("json", "yaml", "markdown")


def build_performance(project: Project, song_id: str) -> dict[str, Any]:
    raise NotImplementedError("performance builder (docs/development-plan.md, milestone 10)")


def export_performance(project: Project, song_id: str, plan: dict[str, Any], fmt: str) -> Path:
    raise NotImplementedError("performance export (docs/development-plan.md, milestone 10)")
