"""rig-match command-line interface.

One command per pipeline stage. A stage that is not built yet exits with
status 2 and says so; the order of work is in docs/development-plan.md.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from rig_match import __version__
from rig_match import project as prj
from rig_match.project import Project, ProjectError, init_project, load_project

app = typer.Typer(
    name="rig-match",
    help="Match songs to Kemper rigs: import, separate, analyze, recommend, export.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err = Console(stderr=True)

PROJECT_OPTION = typer.Option(
    ..., "--project", "-p", help="rig-match project directory (created by `init`)."
)
SONG_OPTION = typer.Option(..., "--song", "-s", help="Song id (a directory name under songs/).")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"rig-match {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """Song-to-Kemper rig matcher."""


def _open_project(path: Path) -> Project:
    try:
        return load_project(path)
    except ProjectError as exc:
        err.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(1) from exc


def _run(stage: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call a pipeline stage; an unbuilt stage becomes a clean exit instead of a traceback."""
    try:
        return stage(*args, **kwargs)
    except NotImplementedError as exc:
        err.print(f"[yellow]not implemented yet:[/yellow] {exc}")
        raise typer.Exit(2) from exc


# --------------------------------------------------------------------------- init


@app.command()
def init(path: Path = typer.Argument(..., help="Directory to create.")) -> None:
    """Create a new project: config.yaml plus the standard sub-folders."""
    try:
        project = init_project(path)
    except ProjectError as exc:
        err.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"Initialised project at [bold]{project.root}[/bold]")
    for name in prj.SUBDIRS:
        console.print(f"  {name}/")
    console.print(f"  {project.config_path.name}")


# --------------------------------------------------------------------------- intake


@app.command("import-audio")
def import_audio_cmd(
    source: Path = typer.Argument(..., exists=True, help="Audio file or folder of audio files."),
    project: Path = PROJECT_OPTION,
) -> None:
    """Import local audio into the project (converted to WAV, tags read into metadata.json)."""
    from rig_match.intake.audio_import import import_audio

    song_ids = _run(import_audio, _open_project(project), source)
    console.print(f"Imported {len(song_ids)} song(s).")


@app.command("import-playlist")
def import_playlist_cmd(
    url: str = typer.Argument(..., help="Spotify playlist URL."),
    project: Path = PROJECT_OPTION,
    metadata_only: bool = typer.Option(
        True, "--metadata-only", help="Fetch track metadata only. This is the only mode; audio is never downloaded."
    ),
) -> None:
    """Import track metadata (title, artist, album, order) from a Spotify playlist."""
    from rig_match.intake.spotify import import_playlist

    _run(import_playlist, _open_project(project), url)


# --------------------------------------------------------------------------- separation


@app.command()
def separate(
    project: Path = PROJECT_OPTION,
    song: Optional[str] = typer.Option(None, "--song", "-s", help="Song id to separate."),
    all_songs: bool = typer.Option(False, "--all", help="Separate every imported song."),
) -> None:
    """Run stem separation and write stems/<song_id>/{guitar,vocals,bass,drums,other}.wav."""
    from rig_match.separation.demucs_runner import separate_song

    if bool(song) == all_songs:
        err.print("[red]error:[/red] give exactly one of --song or --all")
        raise typer.Exit(1)
    p = _open_project(project)
    for song_id in p.song_ids() if all_songs else [song]:
        _run(separate_song, p, song_id)


# --------------------------------------------------------------------------- analysis


@app.command()
def analyze(project: Path = PROJECT_OPTION, song: str = SONG_OPTION) -> None:
    """Detect song structure, segment guitar tones, extract features, cluster into tones."""
    from rig_match.analysis import clustering, features, segmentation, structure

    p = _open_project(project)
    _run(structure.detect_sections, p, song)
    _run(segmentation.segment_tones, p, song)
    _run(features.extract_features, p, song)
    _run(clustering.cluster_tones, p, song)


# --------------------------------------------------------------------------- rigs


@app.command("import-rigs")
def import_rigs_cmd(
    source: Path = typer.Argument(..., exists=True, help="Rig Manager folder, a repositoryR2.db, or a folder of .krig files."),
    project: Path = PROJECT_OPTION,
) -> None:
    """Index Kemper rigs into the project's rig database."""
    from rig_match.rigs.library import import_rigs

    count = _run(import_rigs, _open_project(project), source)
    console.print(f"Indexed {count} rig(s).")


@app.command()
def recommend(project: Path = PROJECT_OPTION, song: str = SONG_OPTION) -> None:
    """Rank rig candidates for every detected tone of a song."""
    from rig_match.rigs.search import recommend_rigs

    _run(recommend_rigs, _open_project(project), song)


# --------------------------------------------------------------------------- export


@app.command()
def export(
    project: Path = PROJECT_OPTION,
    song: str = SONG_OPTION,
    fmt: str = typer.Option("json", "--format", "-f", help="json, yaml or markdown."),
) -> None:
    """Build the Performance slot layout for a song and write it to exports/."""
    from rig_match.performance.builder import build_performance, export_performance

    p = _open_project(project)
    plan = _run(build_performance, p, song)
    out = _run(export_performance, p, song, plan, fmt)
    console.print(f"Wrote {out}")


# --------------------------------------------------------------------------- status


_STAGES: list[tuple[str, Callable[[Project, str], Path]]] = [
    ("audio", lambda p, s: p.song_dir(s) / prj.ORIGINAL_AUDIO),
    ("meta", lambda p, s: p.song_dir(s) / prj.METADATA_FILE),
    ("stems", lambda p, s: p.stems_dir_for(s) / prj.GUITAR_STEM),
    ("sections", lambda p, s: p.analysis_dir_for(s) / prj.SECTIONS_FILE),
    ("segments", lambda p, s: p.analysis_dir_for(s) / prj.TONE_SEGMENTS_FILE),
    ("features", lambda p, s: p.analysis_dir_for(s) / prj.FEATURES_FILE),
    ("tones", lambda p, s: p.analysis_dir_for(s) / prj.TONES_FILE),
    ("recs", lambda p, s: p.analysis_dir_for(s) / prj.RECOMMENDATIONS_FILE),
]


@app.command()
def status(project: Path = PROJECT_OPTION) -> None:
    """Show which pipeline stages have produced output for each song."""
    p = _open_project(project)
    songs = p.song_ids()
    if not songs:
        console.print("No songs imported yet.")
        return
    table = Table(title=str(p.root))
    table.add_column("song")
    for name, _ in _STAGES:
        table.add_column(name, justify="center")
    for song_id in songs:
        cells = ["[green]x[/green]" if path(p, song_id).exists() else "-" for _, path in _STAGES]
        table.add_row(song_id, *cells)
    console.print(table)
    console.print(f"rig db: {'present' if p.rig_db_path.exists() else 'none'}")


if __name__ == "__main__":
    app()
