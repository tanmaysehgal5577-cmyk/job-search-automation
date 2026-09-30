"""Command-line interface."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from collections.abc import Sequence
from dataclasses import replace
from datetime import date
from pathlib import Path

from playwright.async_api import Error as PlaywrightError

from job_automation import __version__
from job_automation.config import SUPPORTED_BROWSERS, Settings
from job_automation.exceptions import AutomationError, ConfigError
from job_automation.exporters import EXPORTERS
from job_automation.filters import SORT_OPTIONS, SearchCriteria
from job_automation.logger import setup_logging
from job_automation.pipeline import run_apply, run_search

logger = logging.getLogger(__name__)


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a valid YYYY-MM-DD date") from exc


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return number


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    mode = common.add_mutually_exclusive_group()
    mode.add_argument("--headless", dest="headless", action="store_true", default=None,
                      help="run without a visible browser window")
    mode.add_argument("--headed", dest="headless", action="store_false",
                      help="show the browser window (useful for debugging)")
    common.add_argument("--browser", choices=SUPPORTED_BROWSERS, help="override BROWSER from .env")
    common.add_argument("--output-dir", type=Path, help="override OUTPUT_DIR from .env")

    parser = argparse.ArgumentParser(
        prog="job-automation", description="Playwright job-search automation."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--env-file", type=Path, help="path to a .env file (default: ./.env)")
    commands = parser.add_subparsers(dest="command", required=True)

    search = commands.add_parser("search", parents=[common], help="scrape, filter and export jobs")
    search.add_argument("-k", "--keyword", action="append", default=[], metavar="TEXT",
                        help="match title/company/description (repeatable, OR logic)")
    search.add_argument("-x", "--exclude", action="append", default=[], metavar="TEXT",
                        help="drop jobs containing this text (repeatable)")
    search.add_argument("-l", "--location", action="append", default=[], metavar="TEXT",
                        help="match location (repeatable, OR logic)")
    search.add_argument("--since", type=_iso_date, metavar="YYYY-MM-DD", help="only newer postings")
    search.add_argument("--sort", choices=SORT_OPTIONS, default="title")
    search.add_argument("--limit", type=_positive_int, help="keep only the first N results")
    search.add_argument("--details", action="store_true", help="also visit detail pages for descriptions")
    search.add_argument("-f", "--format", nargs="+", choices=sorted(EXPORTERS), default=["csv"],
                        dest="formats", help="export formats (default: csv)")

    apply_cmd = commands.add_parser("apply", parents=[common], help="fill & submit the application form")
    apply_cmd.add_argument("--title", required=True, help="job title you are applying for")
    apply_cmd.add_argument("--company", required=True, help="company name")
    return parser


def _override_settings(settings: Settings, args: argparse.Namespace) -> Settings:
    changes = {}
    if args.headless is not None:
        changes["headless"] = args.headless
    if args.browser:
        changes["browser"] = args.browser
    if args.output_dir:
        changes["output_dir"] = args.output_dir
    return replace(settings, **changes)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        settings = _override_settings(Settings.from_env(args.env_file), args)
        setup_logging(settings.log_dir, settings.log_level)

        if args.command == "search":
            criteria = SearchCriteria(
                keywords=tuple(args.keyword), exclude=tuple(args.exclude),
                locations=tuple(args.location), since=args.since,
                sort_by=args.sort, limit=args.limit,
            )
            files = asyncio.run(
                run_search(settings, criteria, formats=args.formats, fetch_details=args.details)
            )
            for path in files:
                print(f"Created: {path}")
        else:
            echoed = asyncio.run(run_apply(settings, args.title, args.company))
            print(f"Application submitted for {echoed.get('custname')} <{echoed.get('custemail')}>")
        return 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except AutomationError as exc:
        logger.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except PlaywrightError as exc:
        # Playwright messages include a long call log; the first line is the useful part.
        message = str(exc).strip().splitlines()[0]
        logger.error("Browser automation failed: %s", message)
        if "Executable doesn't exist" in str(exc):
            print("Browser binaries missing. Run: playwright install chromium", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 - last-resort handler for the CLI
        logger.exception("Unexpected error")
        return 1
