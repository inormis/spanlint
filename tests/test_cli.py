from __future__ import annotations

import json
from pathlib import Path

import pytest

from spanlint.cli import main


def _clean_export(tmp_path: Path) -> Path:
    path = tmp_path / "trace.json"
    path.write_text(
        json.dumps(
            {
                "resourceSpans": [
                    {
                        "scopeSpans": [
                            {
                                "spans": [
                                    {
                                        "name": "chat gpt-4o-mini",
                                        "kind": 3,
                                        "startTimeUnixNano": "0",
                                        "endTimeUnixNano": "1",
                                        "attributes": [
                                            {
                                                "key": "gen_ai.operation.name",
                                                "value": {"stringValue": "chat"},
                                            },
                                            {
                                                "key": "gen_ai.provider.name",
                                                "value": {"stringValue": "openai"},
                                            },
                                            {
                                                "key": "gen_ai.request.model",
                                                "value": {"stringValue": "gpt-4o-mini"},
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
    return path


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


def test_check_on_clean_export_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["check", str(_clean_export(tmp_path))])
    out = capsys.readouterr().out
    assert code == 0
    assert "no findings" in out


def test_check_json_format_emits_valid_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["check", str(_clean_export(tmp_path)), "--format", "json"])
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
                                                "key": "gen_ai.provider.name",
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


def test_check_dispatches_on_jsonl_extension(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    line = json.dumps(
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
                                            "key": "gen_ai.provider.name",
                                            "value": {"stringValue": "openai"},
                                        }
                                    ],
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    )
    p = tmp_path / "trace.jsonl"
    p.write_text(line + "\n" + line + "\n")
    code = main(["check", str(p)])
    out = capsys.readouterr().out
    assert code == 0
    assert "no findings" in out


def test_matrix_prints_a_markdown_table_over_a_fixture_tree(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main(["matrix", str(Path(__file__).parent / "fixtures")])
    lines = capsys.readouterr().out.splitlines()
    assert code == 0
    assert lines[0].startswith("| framework |")
    assert lines[1].startswith("| --- |")
    assert any(line.startswith("| vercel_ai |") for line in lines)


def test_matrix_on_a_tree_without_fixtures_prints_the_header_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["matrix", str(tmp_path)])
    assert code == 0
    assert capsys.readouterr().out == "| framework |\n| --- |\n"
