# rig-match

Song-to-rig matcher for the Kemper Profiler. Give it songs; it isolates the
guitar, finds the distinct guitar tones, picks a rig from your library for each
one and lays them out as a Performance. Command line only; Python 3.11, CPU
(librosa, scikit-learn, Demucs, SQLite).

- Design: [docs/design.md](docs/design.md)
- Plan and progress: [docs/development-plan.md](docs/development-plan.md)

## Status

Early scaffold. What works:

- `rig-match init` and `rig-match status`; the project layout and `config.yaml`
- reading Kemper Rig Manager libraries (`src/rig_match/rigs/rigmanager.py`) and a
  script that snapshots them plus two songs into `data/`
- container-level parsing of `.krig` rig files (rig name and the other string fields)

Every other command exits with "not implemented yet". The milestones in the plan
say what each one should do and in what order.

## Install

Python 3.11+ and ffmpeg on PATH.

    python -m venv .venv
    .venv\Scripts\activate        # Windows
    source .venv/bin/activate     # Linux / WSL
    pip install -e ".[dev]"
    pytest

Optional extras: `separation` (torch, demucs), `clustering` (hdbscan), `spotify`,
`data` (pandas). Example: `pip install -e ".[dev,separation]"`.

## Commands

| Command | Does |
|---|---|
| `rig-match init PATH` | create a project |
| `rig-match import-audio SRC -p PROJ` | import audio files, read tags |
| `rig-match import-playlist URL -p PROJ` | Spotify playlist metadata (never audio) |
| `rig-match separate -p PROJ --song ID` or `--all` | stem separation |
| `rig-match analyze -p PROJ --song ID` | structure, tone segments, features, tone clusters |
| `rig-match import-rigs SRC -p PROJ` | index rigs from a Rig Manager folder or loose rig files |
| `rig-match recommend -p PROJ --song ID` | rank rigs per tone |
| `rig-match export -p PROJ --song ID --format json` | Performance plan |
| `rig-match status -p PROJ` | which stages have output per song |

## Local data

`data/` is git-ignored. `python scripts/sync_rigmanager_data.py` fills it from the
Rig Manager install on the Windows side of this machine; see
[data/README.md](data/README.md).

## Layout

    src/rig_match/
      cli/main.py        commands
      config.py          config.yaml
      project.py         project tree and the file names stages share
      intake/            audio import, tags, Spotify metadata
      separation/        Demucs wrapper
      analysis/          structure, segmentation, features, clustering
      rigs/              rigmanager (Rig Manager DBs), parser (.krig), library (index), search (ranking)
      performance/       slot layout and export
      db/                SQLite schema for the rig index
    scripts/             data sync
    tests/

## Next

[docs/development-plan.md](docs/development-plan.md), milestones 2 to 11: intake,
stems, structure, tone segments, features, clustering, rig index, search, export.

## Licence

MIT, see `LICENSE`.
