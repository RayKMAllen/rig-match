from pathlib import Path

import pytest

from rig_match.config import CONFIG_FILENAME, Config, load_config, save_config
from rig_match.project import SUBDIRS, ProjectError, init_project, load_project


def test_init_creates_tree_and_config(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    project = init_project(root)
    assert project.root == root
    for name in SUBDIRS:
        assert (root / name).is_dir()
    assert (root / CONFIG_FILENAME).is_file()
    assert project.config == Config()


def test_init_refuses_existing_project(tmp_path: Path) -> None:
    init_project(tmp_path / "proj")
    with pytest.raises(ProjectError):
        init_project(tmp_path / "proj")


def test_load_round_trips_config(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    init_project(root, Config(sample_rate=48000, separation_model="htdemucs_ft"))
    loaded = load_project(root)
    assert loaded.config.sample_rate == 48000
    assert loaded.config.separation_model == "htdemucs_ft"
    assert loaded.config.device == "cpu"


def test_load_missing_project(tmp_path: Path) -> None:
    with pytest.raises(ProjectError):
        load_project(tmp_path)


def test_config_ignores_unknown_keys(tmp_path: Path) -> None:
    path = tmp_path / CONFIG_FILENAME
    save_config(Config(), path)
    path.write_text(path.read_text() + "not_a_setting: 1\n")
    assert load_config(path) == Config()


def test_song_ids_lists_song_dirs(tmp_path: Path) -> None:
    project = init_project(tmp_path / "proj")
    assert project.song_ids() == []
    (project.songs_dir / "b_song").mkdir()
    (project.songs_dir / "a_song").mkdir()
    (project.songs_dir / "stray.txt").write_text("")
    assert project.song_ids() == ["a_song", "b_song"]
