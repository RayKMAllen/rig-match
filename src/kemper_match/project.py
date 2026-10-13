"""A kemper-match project: the directory layout every command works inside.

Nothing lives only in memory. Each pipeline stage reads its inputs from the
project tree and writes its outputs back as files, so every intermediate
artifact can be inspected and any stage re-run on its own.

    <project>/
      config.yaml
      songs/<song_id>/original.wav, metadata.json
      stems/<song_id>/guitar.wav, vocals.wav, bass.wav, drums.wav, other.wav
      analysis/<song_id>/sections.json, tone_segments.json, features.json,
                         tones.json, recommendations.json
      rigs/            rig database and anything copied in by `import-rigs`
      renders/         Kemper output captures (phase 2)
      exports/         performance plans
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kemper_match.config import CONFIG_FILENAME, Config, load_config, save_config

SUBDIRS = ("songs", "stems", "analysis", "rigs", "renders", "exports")

# File names shared by the stages. Change them here, nowhere else.
ORIGINAL_AUDIO = "original.wav"
METADATA_FILE = "metadata.json"
GUITAR_STEM = "guitar.wav"
SECTIONS_FILE = "sections.json"
TONE_SEGMENTS_FILE = "tone_segments.json"
FEATURES_FILE = "features.json"
TONES_FILE = "tones.json"
RECOMMENDATIONS_FILE = "recommendations.json"
RIG_DB_FILE = "rigs.db"


class ProjectError(Exception):
    """Raised for a missing, malformed or already-existing project."""


@dataclass
class Project:
    root: Path
    config: Config

    # -- top-level paths --------------------------------------------------
    @property
    def config_path(self) -> Path:
        return self.root / CONFIG_FILENAME

    @property
    def songs_dir(self) -> Path:
        return self.root / "songs"

    @property
    def stems_dir(self) -> Path:
        return self.root / "stems"

    @property
    def analysis_dir(self) -> Path:
        return self.root / "analysis"

    @property
    def rigs_dir(self) -> Path:
        return self.root / "rigs"

    @property
    def renders_dir(self) -> Path:
        return self.root / "renders"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def rig_db_path(self) -> Path:
        return self.rigs_dir / RIG_DB_FILE

    # -- per-song paths ---------------------------------------------------
    def song_dir(self, song_id: str) -> Path:
        return self.songs_dir / song_id

    def stems_dir_for(self, song_id: str) -> Path:
        return self.stems_dir / song_id

    def analysis_dir_for(self, song_id: str) -> Path:
        return self.analysis_dir / song_id

    def song_ids(self) -> list[str]:
        """Ids of all imported songs (one sub-directory of songs/ each)."""
        if not self.songs_dir.exists():
            return []
        return sorted(p.name for p in self.songs_dir.iterdir() if p.is_dir())

    def save_config(self) -> None:
        save_config(self.config, self.config_path)


def init_project(root: Path, config: Config | None = None) -> Project:
    """Create the project tree and a default ``config.yaml``.

    Refuses to touch a directory that already holds a project.
    """
    root = Path(root)
    if (root / CONFIG_FILENAME).exists():
        raise ProjectError(f"{root} is already a kemper-match project")
    root.mkdir(parents=True, exist_ok=True)
    for name in SUBDIRS:
        (root / name).mkdir(exist_ok=True)
    project = Project(root=root, config=config or Config())
    project.save_config()
    return project


def load_project(root: Path) -> Project:
    root = Path(root)
    config_path = root / CONFIG_FILENAME
    if not config_path.exists():
        raise ProjectError(f"no {CONFIG_FILENAME} in {root} (run `kemper-match init {root}` first)")
    return Project(root=root, config=load_config(config_path))
