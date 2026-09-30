"""Scraping logic: navigate, wait, extract and validate job listings."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import replace

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

from job_automation.config import Settings
from job_automation.exceptions import NavigationError, ValidationError
from job_automation.models import Job, parse_jobs
from job_automation.utils import retry_async

logger = logging.getLogger(__name__)

RESULTS_SELECTOR = "#ResultsContainer"
CARD_SELECTOR = f"{RESULTS_SELECTOR} .card-content"
MAX_DESCRIPTION_CHARS = 600

# Runs inside the browser once for ALL cards (one round-trip instead of hundreds).
_EXTRACT_CARDS_JS = """
cards => cards.map(card => {
    const text = selector => {
        const el = card.querySelector(selector);
        return el ? el.textContent.trim() : "";
    };
    const links = Array.from(card.querySelectorAll("footer a"));
    const hrefFor = label => {
        const link = links.find(a => a.textContent.trim().toLowerCase() === label);
        return link ? link.href : "";
    };
    const time = card.querySelector("time");
    return {
        title: text("h2.title"),
        company: text("h3.company"),
        location: text("p.location"),
        posted: time ? (time.getAttribute("datetime") || time.textContent.trim()) : "",
        learn_url: hrefFor("learn"),
        apply_url: hrefFor("apply"),
    };
})
"""

# Best-effort: the longest paragraph on a detail page is the job description.
_EXTRACT_DESCRIPTION_JS = """
() => {
    const paragraphs = Array.from(document.querySelectorAll(".content p"))
        .map(p => p.textContent.trim())
        .filter(Boolean);
    return paragraphs.sort((a, b) => b.length - a.length)[0] || "";
}
"""


class JobScraper:
    """Drives one Playwright page to collect job listings."""

    def __init__(self, page: Page, settings: Settings) -> None:
        self._page = page
        self._settings = settings

    async def open(self) -> None:
        """Navigate to the job board (with retries) and wait for the results."""
        await retry_async(
            self._navigate,
            attempts=self._settings.max_retries,
            delay_s=self._settings.retry_delay_s,
            exceptions=(PlaywrightError, NavigationError),
            label="Navigation",
        )

    async def _navigate(self) -> None:
        url = self._settings.base_url
        logger.info("Opening %s", url)
        response = await self._page.goto(url, wait_until="domcontentloaded")
        if response is not None and not response.ok:
            raise NavigationError(f"{url} returned HTTP {response.status}")
        # Explicit wait on the element we need - no sleeps.
        await self._page.wait_for_selector(CARD_SELECTOR, state="visible")

    async def collect(self) -> list[Job]:
        """Extract every job card on the page and validate the outcome."""
        raw_items = await self._page.eval_on_selector_all(CARD_SELECTOR, _EXTRACT_CARDS_JS)
        jobs, skipped = parse_jobs(raw_items)
        self._validate(jobs, found=len(raw_items), skipped=skipped)
        logger.info("Collected %d jobs (%d skipped)", len(jobs), skipped)
        return jobs

    @staticmethod
    def _validate(jobs: list[Job], *, found: int, skipped: int) -> None:
        """Fail loudly if the page structure changed instead of exporting junk."""
        if found == 0 or not jobs:
            raise ValidationError(
                "No job cards were extracted - the site layout may have changed "
                f"(selector: {CARD_SELECTOR!r})."
            )
        if skipped / found > 0.5:
            raise ValidationError(f"{skipped} of {found} cards were malformed; refusing to continue.")
        missing_url = sum(1 for job in jobs if not job.url)
        if missing_url:
            logger.warning("%d jobs have no detail URL", missing_url)

    async def enrich_with_details(self, jobs: list[Job]) -> list[Job]:
        """Visit each job's detail page (concurrently) to add a description."""
        semaphore = asyncio.Semaphore(self._settings.detail_concurrency)
        logger.info(
            "Fetching %d detail pages (concurrency=%d)", len(jobs), self._settings.detail_concurrency
        )
        return list(await asyncio.gather(*(self._fetch_description(j, semaphore) for j in jobs)))

    async def _fetch_description(self, job: Job, semaphore: asyncio.Semaphore) -> Job:
        if not job.url:
            return job
        async with semaphore:
            detail_page = await self._page.context.new_page()
            try:
                await detail_page.goto(job.url, wait_until="domcontentloaded")
                text = await detail_page.evaluate(_EXTRACT_DESCRIPTION_JS)
                return replace(job, description=text[:MAX_DESCRIPTION_CHARS])
            except PlaywrightError as exc:
                logger.warning("Could not read details for %r: %s", job.title, exc)
                return job
            finally:
                await detail_page.close()
