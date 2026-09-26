from __future__ import annotations

import pytest

from spanlint.cli import main


def test_help_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "spanlint" in capsys.readouterr().out


def test_version_prints_package_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out.strip()
    assert out  # some version string was printed


def test_no_args_returns_zero() -> None:
    assert main([]) == 0


def test_format_text_accepted() -> None:
    assert main(["--format", "text"]) == 0


def test_format_json_accepted() -> None:
    assert main(["--format", "json"]) == 0


def test_format_invalid_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--format", "yaml"])
    assert exc.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
