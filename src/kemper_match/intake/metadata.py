"""Song metadata: audio tags, CSV manifests, and the ``metadata.json`` written per song."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_tags(path: Path) -> dict[str, Any]:
    """Title / artist / album / duration from the file's tags (mutagen)."""
    raise NotImplementedError("tag reading (plans/development-plan.md, milestone 2)")


def read_csv_manifest(path: Path) -> list[dict[str, Any]]:
    """Rows of a CSV manifest (one song per row) as dicts."""
    raise NotImplementedError("CSV manifest import (plans/development-plan.md, milestone 2)")
