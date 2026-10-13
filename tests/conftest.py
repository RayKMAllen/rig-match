from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
LOCAL_LIBRARY_DB = DATA_DIR / "rigmanager" / "Local Library" / "repositoryR2.db"

requires_local_data = pytest.mark.skipif(
    not LOCAL_LIBRARY_DB.exists(),
    reason="no Rig Manager snapshot in data/ (run scripts/sync_rigmanager_data.py)",
)
