"""Project configuration: defaults plus load/save of ``config.yaml``."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILENAME = "config.yaml"


@dataclass
class Config:
    """Settings stored in a project's ``config.yaml``.

    Keep this flat and serialisable; every value here must round-trip through YAML.
    """

    sample_rate: int = 44100
    separation_model: str = "htdemucs"  # or "htdemucs_ft" (slower, better)
    device: str = "cpu"
    top_n_rigs: int = 5
    # Rig Manager data folder (or a snapshot of one) that `import-rigs` reads by default.
    rig_manager_root: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        # TODO: report unknown keys instead of silently dropping them.
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


def load_config(path: Path) -> Config:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at top level")
    return Config.from_dict(data)


def save_config(config: Config, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(config.to_dict(), fh, sort_keys=False)
