"""Read Kemper Rig Manager's own library databases.

Rig Manager stores its data under ``%LOCALAPPDATA%\\Kemper Amps\\RigManager``.
Every library folder is one SQLite file called ``repositoryR2.db``::

    Local Library/repositoryR2.db              rigs in the top-level local library
    Local Library/<pack>/.../repositoryR2.db   one DB per sub-folder (profile packs)
    Prf/..., Prst/...                          performances and presets (not used here)

A rig DB has a ``Rigs`` table (one row per rig; ~36 text columns holding the
metadata Rig Manager shows in its list view: Name, Author, Gain, "Amp Name",
"Cabinet Name", "Mic Type", ...) and a ``Rigs_blobs`` table keyed by the same
id whose ``data`` column is the raw rig, byte-for-byte a ``.krig`` file.

Only reading is supported, and only metadata plus raw blobs. Decoding a blob
is :mod:`kemper_match.rigs.parser`'s job. Only rigs are read; performances and
presets are out of scope.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

REPOSITORY_FILENAME = "repositoryR2.db"
RIG_MAGIC = b"KThd"

# Values Rig Manager uses for "unset".
_EMPTY = (None, "", -1)


@dataclass
class RigRecord:
    rig_id: int
    name: str
    filename: str
    author: str
    date: str
    gain: float | None
    amp_name: str
    cabinet_name: str
    # Every non-empty column of the row, keyed by Rig Manager's column name.
    fields: dict[str, str] = field(default_factory=dict, repr=False)


def find_repositories(root: Path) -> list[Path]:
    """All ``repositoryR2.db`` files under ``root`` (rigs, performances and presets alike)."""
    return sorted(Path(root).rglob(REPOSITORY_FILENAME))


def _connect(db_path: Path) -> sqlite3.Connection:
    if not Path(db_path).is_file():
        raise FileNotFoundError(db_path)
    uri = "file:" + quote(Path(db_path).as_posix(), safe="/:") + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _rows(conn: sqlite3.Connection, table: str) -> Iterator[dict[str, Any]]:
    cur = conn.execute(f'SELECT * FROM "{table}" ORDER BY id')
    cols = [d[0] for d in cur.description]
    for row in cur:
        yield {k: v for k, v in zip(cols, row, strict=True) if v not in _EMPTY}


def _to_float(value: str | None) -> float | None:
    try:
        return float(value) if value not in _EMPTY else None
    except ValueError:
        return None


def _record(row: dict[str, Any]) -> RigRecord:
    fields = {k: str(v) for k, v in row.items() if k != "id"}
    return RigRecord(
        rig_id=int(row["id"]),
        name=fields.get("Name", ""),
        filename=fields.get("Filename", ""),
        author=fields.get("Author", ""),
        date=fields.get("Date", ""),
        gain=_to_float(fields.get("Gain")),
        amp_name=fields.get("Amp Name", ""),
        cabinet_name=fields.get("Cabinet Name", ""),
        fields=fields,
    )


def read_rigs(db_path: Path) -> list[RigRecord]:
    """Metadata of every rig in one ``repositoryR2.db``."""
    conn = _connect(db_path)
    try:
        return [_record(row) for row in _rows(conn, "Rigs")]
    finally:
        conn.close()


def read_rig_blob(db_path: Path, rig_id: int) -> bytes:
    conn = _connect(db_path)
    try:
        row = conn.execute('SELECT data FROM "Rigs_blobs" WHERE id = ?', (rig_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise KeyError(f"no blob for rig id {rig_id} in {db_path}")
    return bytes(row[0])


def iter_rig_blobs(db_path: Path) -> Iterator[tuple[RigRecord, bytes]]:
    """(record, raw rig bytes) for every rig, in id order."""
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            'SELECT r.*, b.data FROM "Rigs" r JOIN "Rigs_blobs" b ON r.id = b.id ORDER BY r.id'
        )
        cols = [d[0] for d in cur.description]
        for row in cur:
            meta = {k: v for k, v in zip(cols[:-1], row[:-1], strict=True) if v not in _EMPTY}
            yield _record(meta), bytes(row[-1])
    finally:
        conn.close()


def _safe_filename(name: str) -> str:
    keep = "".join(c if c.isalnum() or c in " -_.()'" else "_" for c in name)
    return keep.strip() or "rig"


def export_rig_files(db_path: Path, dest_dir: Path) -> list[Path]:
    """Write every rig blob as ``<id> - <name>.krig`` under ``dest_dir``; return the paths.

    Rig Manager's own ``Filename`` column is truncated to 40 characters, so the
    file name is rebuilt from the id and the rig name instead.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for rec, blob in iter_rig_blobs(db_path):
        if not blob.startswith(RIG_MAGIC):
            raise ValueError(f"rig {rec.rig_id} ({rec.name!r}) in {db_path} does not start with {RIG_MAGIC!r}")
        out = dest_dir / f"{rec.rig_id:03d} - {_safe_filename(rec.name)}.krig"
        out.write_bytes(blob)
        written.append(out)
    return written

