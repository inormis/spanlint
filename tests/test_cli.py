from __future__ import annotations

import json
from pathlib import Path

import pytest

from spanlint.cli import main

OPENAI_FIXTURE = Path(__file__).parent / "fixtures" / "openai" / "chat_completion.json"


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


def test_no_args_prints_help_and_returns_zero() -> None:
    assert main([]) == 0


def test_check_on_clean_fixture_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["check", str(OPENAI_FIXTURE)])
    out = capsys.readouterr().out
    assert code == 0
    assert "no findings" in out


def test_check_json_format_emits_valid_json(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["check", str(OPENAI_FIXTURE), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out) == {"findings": []}


def test_check_with_findings_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text(
        json.dumps(
            {
                "resourceSpans": [
                    {
                        "scopeSpans": [
                            {
                                "spans": [
                                    {
                                        "name": "chat",
                                        "kind": 3,
                                        "startTimeUnixNano": "0",
                                        "endTimeUnixNano": "1",
                                        "attributes": [
                                            {
                                                "key": "gen_ai.system",
                                                "value": {"stringValue": "openai"},
                                            },
                                            {
                                                "key": "gen_ai.request.model",
                                                "value": {"intValue": "42"},
                                            },
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        )
    )
    code = main(["check", str(broken)])
    out = capsys.readouterr().out
    assert code == 1
    assert "gen_ai.request.model" in out
