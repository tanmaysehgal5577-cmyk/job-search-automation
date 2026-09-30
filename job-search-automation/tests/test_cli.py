from datetime import date

import pytest

from job_automation.cli import build_parser, main


def test_search_arguments_are_parsed():
    args = build_parser().parse_args(
        ["search", "-k", "python", "-k", "data", "-l", "AU", "--since", "2021-04-01",
         "--limit", "5", "-f", "csv", "pdf", "--headed"]
    )
    assert args.keyword == ["python", "data"]
    assert args.since == date(2021, 4, 1)
    assert args.formats == ["csv", "pdf"]
    assert args.headless is False


def test_headless_defaults_to_none_so_env_decides():
    assert build_parser().parse_args(["search"]).headless is None


@pytest.mark.parametrize("argv", [["search", "--limit", "0"], ["search", "--since", "yesterday"], ["apply"]])
def test_invalid_arguments_exit_with_usage_error(argv):
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(argv)
    assert exc.value.code == 2


def test_main_reports_config_errors_with_exit_code_2(monkeypatch, capsys):
    monkeypatch.setenv("BROWSER", "netscape")
    assert main(["search"]) == 2
    assert "BROWSER" in capsys.readouterr().err
