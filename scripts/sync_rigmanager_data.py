#!/usr/bin/env python
"""Snapshot a slice of Kemper Rig Manager's library plus a couple of songs into data/.

Copies (see PACKS and SONGS below):

    data/rigmanager/<same relative path>/repositoryR2.db   selected library DBs
    data/rigs/local_library/*.krig                          every top-level local-library rig as a file
    data/rigs/rigbackups/*.krig                             .krig files Rig Manager wrote to disk itself
    data/songs/*.mp3                                        reference songs
    data/manifest.json                                      what was copied, from where, when

Rig Manager keeps its data in %LOCALAPPDATA%\\Kemper Amps\\RigManager (from WSL:
/mnt/c/Users/<user>/AppData/Local/Kemper Amps/RigManager). Quit Rig Manager
before running this so no SQLite file is mid-write.

    python scripts/sync_rigmanager_data.py
    python scripts/sync_rigmanager_data.py --rigmanager-root "D:/RigManager" --music-dir "D:/Music"
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from rig_match.rigs.rigmanager import export_rig_files, read_rigs  # noqa: E402

# Library DBs to copy, relative to the Rig Manager root. The 80k Profile Pack
# (500 MB) and the big commercial packs are deliberately left out.
PACKS = [
    "Local Library/repositoryR2.db",
    "Local Library/Muse/repositoryR2.db",
    "Local Library/Pink Floyd/repositoryR2.db",
    "Local Library/Kemper Stage GL/repositoryR2.db",
    "Local Library/Michael Britt/'69 Marsh Pack/repositoryR2.db",
]
LOCAL_LIBRARY_DB = PACKS[0]

SONGS = [
    "Scar Tissue.mp3",
    "Basket Case.mp3",
]


def _windows_user_dirs() -> list[Path]:
    if os.name == "nt":
        return [Path(os.environ.get("USERPROFILE", Path.home()))]
    return sorted(p for p in Path("/mnt/c/Users").glob("*") if p.is_dir())


def _rigmanager_under(user: Path) -> Path:
    return user / "AppData" / "Local" / "Kemper Amps" / "RigManager"


def default_user_dir() -> Path | None:
    """The Windows user profile that has a Rig Manager install (Music and Documents are read from the same one)."""
    if os.name == "nt" and "LOCALAPPDATA" in os.environ:
        cand = Path(os.environ["LOCALAPPDATA"]) / "Kemper Amps" / "RigManager"
        return Path(os.environ["USERPROFILE"]) if cand.is_dir() else None
    for user in _windows_user_dirs():
        if _rigmanager_under(user).is_dir():
            return user
    return None


def default_rigmanager_root() -> Path | None:
    user = default_user_dir()
    return _rigmanager_under(user) if user else None


def default_rigbackups_dir() -> Path | None:
    user = default_user_dir()
    if user is None:
        return None
    for docs in ("OneDrive/Documents", "Documents"):
        cand = user / docs / "Kemper Amps" / "RigManager" / "rigbackups"
        if cand.is_dir():
            return cand
    return None


def default_music_dir() -> Path | None:
    user = default_user_dir()
    if user is None:
        return None
    cand = user / "Music"
    return cand if cand.is_dir() else None


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rigmanager-root", type=Path, default=default_rigmanager_root())
    ap.add_argument("--rigbackups-dir", type=Path, default=default_rigbackups_dir())
    ap.add_argument("--music-dir", type=Path, default=default_music_dir())
    ap.add_argument("--dest", type=Path, default=REPO_ROOT / "data")
    args = ap.parse_args()

    if args.rigmanager_root is None or not args.rigmanager_root.is_dir():
        ap.error("Rig Manager data folder not found; pass --rigmanager-root")

    dest: Path = args.dest
    manifest: dict = {
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rigmanager_root": str(args.rigmanager_root),
        "music_dir": str(args.music_dir),
        "rig_dbs": [],
        "exported_rigs": [],
        "rigbackups": [],
        "songs": [],
    }

    for rel in PACKS:
        src = args.rigmanager_root / rel
        if not src.is_file():
            print(f"skip (missing): {src}")
            continue
        dst = dest / "rigmanager" / rel
        copy(src, dst)
        entry = {"path": str(dst.relative_to(dest)), "bytes": dst.stat().st_size, "rigs": len(read_rigs(dst))}
        manifest["rig_dbs"].append(entry)
        print(f"copied {rel}  ({entry})")

    local_db = dest / "rigmanager" / LOCAL_LIBRARY_DB
    if local_db.is_file():
        written = export_rig_files(local_db, dest / "rigs" / "local_library")
        manifest["exported_rigs"] = [str(p.relative_to(dest)) for p in written]
        print(f"exported {len(written)} rigs to {dest / 'rigs' / 'local_library'}")

    if args.rigbackups_dir and args.rigbackups_dir.is_dir():
        for src in sorted(args.rigbackups_dir.glob("*.krig")):
            dst = dest / "rigs" / "rigbackups" / src.name
            copy(src, dst)
            manifest["rigbackups"].append(str(dst.relative_to(dest)))
        print(f"copied {len(manifest['rigbackups'])} rig backup file(s)")

    if args.music_dir and args.music_dir.is_dir():
        for name in SONGS:
            src = args.music_dir / name
            if not src.is_file():
                print(f"skip (missing): {src}")
                continue
            dst = dest / "songs" / name
            copy(src, dst)
            manifest["songs"].append({"path": str(dst.relative_to(dest)), "bytes": dst.stat().st_size})
            print(f"copied {name}")

    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {dest / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
