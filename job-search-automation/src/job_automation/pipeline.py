"""High-level workflows that combine browser, scraper, filters and exporters."""

from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from job_automation.browser import browser_session, capture_screenshot, screenshot_on_failure
from job_automation.config import Settings
from job_automation.exporters import export_all
from job_automation.filters import SearchCriteria, apply_criteria
from job_automation.forms import Applicant, submit_application
from job_automation.scraper import JobScraper
from job_automation.utils import timestamp

logger = logging.getLogger(__name__)


async def run_search(
    settings: Settings,
    criteria: SearchCriteria,
    *,
    formats: Sequence[str],
    fetch_details: bool = False,
) -> list[Path]:
    """Scrape -> filter -> (optionally enrich) -> export. Returns created files."""
    started = time.perf_counter()
    async with browser_session(settings) as page:
        async with screenshot_on_failure(page, settings.screenshot_dir, "search"):
            scraper = JobScraper(page, settings)
            await scraper.open()
            all_jobs = await scraper.collect()
            selected = apply_criteria(all_jobs, criteria)
            logger.info("%d of %d jobs match your criteria", len(selected), len(all_jobs))
            if fetch_details and selected:
                selected = await scraper.enrich_with_details(selected)
            await capture_screenshot(page, settings.screenshot_dir, "results", full_page=False)

    if not selected:
        logger.warning("No jobs matched - nothing to export. Try broader filters.")
        return []

    files = export_all(selected, formats, settings.output_dir, f"jobs_{timestamp()}")
    logger.info("Finished in %.1fs", time.perf_counter() - started)
    return files


async def run_apply(settings: Settings, job_title: str, company: str) -> dict[str, Any]:
    """Fill and submit the application form for one job."""
    applicant = Applicant.from_settings(settings)
    async with browser_session(settings) as page:
        return await submit_application(page, settings, applicant, job_title, company)
