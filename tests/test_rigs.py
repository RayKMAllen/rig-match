"""Tests against the local Rig Manager snapshot in data/ (skipped when absent)."""

from pathlib import Path

import pytest

from rig_match.rigs import parser, rigmanager
from tests.conftest import DATA_DIR, LOCAL_LIBRARY_DB, requires_local_data


@requires_local_data
def test_read_rigs_has_metadata() -> None:
    rigs = rigmanager.read_rigs(LOCAL_LIBRARY_DB)
    assert rigs
    for rig in rigs:
        assert rig.name
        assert rig.amp_name
        assert rig.gain is None or 0.0 <= rig.gain <= 10.0


@requires_local_data
def test_blob_is_a_rig_file_matching_its_record() -> None:
    for rec, blob in rigmanager.iter_rig_blobs(LOCAL_LIBRARY_DB):
        rig = parser.parse_rig_bytes(blob)
        assert rig.format == 0 and len(rig.tracks) == 1 and rig.division == 480
        assert rig.name == rec.name
        strings = rig.strings()
        assert strings[parser.RIG_AUTHOR] == rec.author
        if rec.cabinet_name:
            assert strings[parser.CABINET_NAME] == rec.cabinet_name


@requires_local_data
def test_export_round_trip(tmp_path: Path) -> None:
    written = rigmanager.export_rig_files(LOCAL_LIBRARY_DB, tmp_path)
    assert len(written) == len(rigmanager.read_rigs(LOCAL_LIBRARY_DB))
    for path in written:
        assert path.suffix == ".krig"
        assert parser.parse_rig_file(path).name


@requires_local_data
def test_find_repositories() -> None:
    found = rigmanager.find_repositories(DATA_DIR / "rigmanager")
    assert LOCAL_LIBRARY_DB in found


def test_parse_rejects_garbage() -> None:
    with pytest.raises(parser.RigParseError):
        parser.parse_rig_bytes(b"not a rig")
