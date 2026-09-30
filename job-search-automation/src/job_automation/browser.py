"""Browser lifecycle management and failure screenshots."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from playwright.async_api import Page, async_playwright

from job_automation.config import Settings
from job_automation.utils import slugify, timestamp

logger = logging.getLogger(__name__)


@asynccontextmanager
async def browser_session(settings: Settings) -> AsyncIterator[Page]:
    """Launch a browser and yield a ready-to-use page.

    Everything (page, context, browser, Playwright driver) is closed in
    ``finally`` blocks, even when the automation raises.
    """
    async with async_playwright() as playwright:
        launcher = getattr(playwright, settings.browser)
        logger.info("Launching %s (headless=%s)", settings.browser, settings.headless)
        browser = await launcher.launch(headless=settings.headless, slow_mo=settings.slow_mo_ms)
        try:
            context = await browser.new_context(viewport={"width": 1366, "height": 900})
            try:
                context.set_default_timeout(settings.timeout_ms)
                context.set_default_navigation_timeout(settings.timeout_ms)
                yield await context.new_page()
            finally:
                await context.close()
        finally:
            await browser.close()
            logger.info("Browser closed")


async def capture_screenshot(
    page: Page, directory: Path, label: str, *, full_page: bool = True
) -> Path | None:
    """Save a screenshot. Never raises - a failed screenshot must not hide the real error."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{timestamp()}_{slugify(label)}.png"
    try:
        await page.screenshot(path=str(path), full_page=full_page)
    except Exception:  # noqa: BLE001 - deliberately broad, see docstring
        logger.exception("Could not capture screenshot %s", path)
        return None
    logger.info("Screenshot saved: %s", path)
    return path


@asynccontextmanager
async def screenshot_on_failure(page: Page, directory: Path, label: str) -> AsyncIterator[None]:
    """Capture a screenshot if the wrapped block raises, then re-raise."""
    try:
        yield
    except Exception:
        logger.error("Step %r failed - capturing screenshot", label)
        await capture_screenshot(page, directory, f"failure_{label}")
        raise
