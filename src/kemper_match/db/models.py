"""SQLite schema and queries for the project rig database (``rigs/rigs.db``).

Planned table (milestone 8): rigs(rig_id, rig_name, file_path, amp_family,
gain_category, cab_type, brightness, tightness, tags JSON, feature_vector JSON).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: Path) -> sqlite3.Connection:
    raise NotImplementedError("rig database schema (plans/development-plan.md, milestone 8)")
