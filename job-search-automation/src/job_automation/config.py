"""Typed, validated configuration loaded from environment variables / ``.env``."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from job_automation.exceptions import ConfigError

SUPPORTED_BROWSERS = ("chromium", "firefox", "webkit")
_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


def _parse_bool(name: str, value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ConfigError(f"{name} must be a boolean (true/false), got {value!r}.")


def _parse_number(name: str, value: str, cast: type, minimum: float):
    try:
        number = cast(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a {cast.__name__}, got {value!r}.") from exc
    if number < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {number}.")
    return number


@dataclass(frozen=True)
class Settings:
    """Immutable application settings. Build with :meth:`Settings.from_env`."""

    base_url: str = "https://realpython.github.io/fake-jobs/"
    form_url: str = "https://httpbin.org/forms/post"
    browser: str = "chromium"
    headless: bool = True
    slow_mo_ms: int = 0
    timeout_ms: int = 30_000
    max_retries: int = 3
    retry_delay_s: float = 1.0
    detail_concurrency: int = 5
    output_dir: Path = Path("output")
    screenshot_dir: Path = Path("screenshots")
    log_dir: Path = Path("logs")
    log_level: str = "INFO"
    applicant_name: str = ""
    applicant_email: str = ""
    applicant_phone: str = ""

    @classmethod
    def from_env(
        cls, env_file: str | Path | None = None, environ: Mapping[str, str] | None = None
    ) -> Settings:
        """Load settings from ``.env`` (if present) and the process environment.

        ``environ`` can be injected for tests so no real environment is touched.
        """
        if environ is None:
            # usecwd=True: look for .env in the directory the user runs from, not next to this module.
            load_dotenv(env_file or find_dotenv(usecwd=True), override=False)
            environ = os.environ

        def get(name: str, default: str) -> str:
            value = environ.get(name)
            return default if value is None or value.strip() == "" else value.strip()

        d = cls()
        browser = get("BROWSER", d.browser).lower()
        if browser not in SUPPORTED_BROWSERS:
            raise ConfigError(f"BROWSER must be one of {SUPPORTED_BROWSERS}, got {browser!r}.")

        log_level = get("LOG_LEVEL", d.log_level).upper()
        if log_level not in _LOG_LEVELS:
            raise ConfigError(f"LOG_LEVEL is not a valid level: {log_level!r}.")

        return cls(
            base_url=get("BASE_URL", d.base_url),
            form_url=get("FORM_URL", d.form_url),
            browser=browser,
            headless=_parse_bool("HEADLESS", get("HEADLESS", str(d.headless))),
            slow_mo_ms=_parse_number("SLOW_MO_MS", get("SLOW_MO_MS", "0"), int, 0),
            timeout_ms=_parse_number("TIMEOUT_MS", get("TIMEOUT_MS", "30000"), int, 1),
            max_retries=_parse_number("MAX_RETRIES", get("MAX_RETRIES", "3"), int, 1),
            retry_delay_s=_parse_number("RETRY_DELAY_S", get("RETRY_DELAY_S", "1"), float, 0),
            detail_concurrency=_parse_number(
                "DETAIL_CONCURRENCY", get("DETAIL_CONCURRENCY", "5"), int, 1
            ),
            output_dir=Path(get("OUTPUT_DIR", str(d.output_dir))),
            screenshot_dir=Path(get("SCREENSHOT_DIR", str(d.screenshot_dir))),
            log_dir=Path(get("LOG_DIR", str(d.log_dir))),
            log_level=log_level,
            applicant_name=get("APPLICANT_NAME", ""),
            applicant_email=get("APPLICANT_EMAIL", ""),
            applicant_phone=get("APPLICANT_PHONE", ""),
        )
