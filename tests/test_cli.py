from pathlib import Path

from typer.testing import CliRunner

from rig_match import __version__
from rig_match.cli.main import app
from rig_match.config import CONFIG_FILENAME

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_init_then_status(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    result = runner.invoke(app, ["init", str(root)])
    assert result.exit_code == 0, result.output
    assert (root / CONFIG_FILENAME).is_file()

    result = runner.invoke(app, ["status", "--project", str(root)])
    assert result.exit_code == 0, result.output
    assert "No songs" in result.output


def test_init_twice_fails(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    assert runner.invoke(app, ["init", str(root)]).exit_code == 0
    assert runner.invoke(app, ["init", str(root)]).exit_code == 1


def test_commands_need_a_project(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", "--project", str(tmp_path), "--song", "x"])
    assert result.exit_code == 1


def test_unbuilt_stage_exits_2(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    runner.invoke(app, ["init", str(root)])
    result = runner.invoke(app, ["analyze", "--project", str(root), "--song", "x"])
    assert result.exit_code == 2
    assert "not implemented" in result.output
