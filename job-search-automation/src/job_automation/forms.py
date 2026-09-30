"""Form-interaction automation: fill, submit and verify a form.

The default target is httpbin's public sandbox form, which echoes the submitted
data back as JSON - ideal for proving that the automation really worked. Point
``FORM_URL`` at another form and adjust ``FIELD_SELECTORS`` to reuse this code.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from playwright.async_api import Page

from job_automation.browser import capture_screenshot, screenshot_on_failure
from job_automation.config import Settings
from job_automation.exceptions import ConfigError, FormSubmissionError

logger = logging.getLogger(__name__)

FIELD_SELECTORS = {
    "custname": "input[name='custname']",
    "custtel": "input[name='custtel']",
    "custemail": "input[name='custemail']",
    "comments": "textarea[name='comments']",
}


@dataclass(frozen=True)
class Applicant:
    """Person on whose behalf the form is filled (loaded from ``.env``)."""

    name: str
    email: str
    phone: str

    @classmethod
    def from_settings(cls, settings: Settings) -> Applicant:
        missing = [
            env
            for env, value in (
                ("APPLICANT_NAME", settings.applicant_name),
                ("APPLICANT_EMAIL", settings.applicant_email),
                ("APPLICANT_PHONE", settings.applicant_phone),
            )
            if not value
        ]
        if missing:
            raise ConfigError(f"Set {', '.join(missing)} in your .env file to use the apply command.")
        return cls(settings.applicant_name, settings.applicant_email, settings.applicant_phone)


def parse_form_response(body_text: str, expected: dict[str, str]) -> dict[str, Any]:
    """Parse the JSON echo and verify every expected field came back unchanged."""
    try:
        payload = json.loads(body_text)
    except json.JSONDecodeError as exc:
        raise FormSubmissionError("Server response was not valid JSON.") from exc

    echoed = payload.get("form", {}) if isinstance(payload, dict) else {}
    mismatches = [k for k, v in expected.items() if echoed.get(k) != v]
    if mismatches:
        raise FormSubmissionError(f"Server echoed different values for: {', '.join(mismatches)}")
    return echoed


async def submit_application(
    page: Page, settings: Settings, applicant: Applicant, job_title: str, company: str
) -> dict[str, Any]:
    """Fill the form for one job, submit it and verify the server's echo."""
    async with screenshot_on_failure(page, settings.screenshot_dir, "apply"):
        logger.info("Opening form %s", settings.form_url)
        await page.goto(settings.form_url, wait_until="domcontentloaded")
        form = page.locator("form")
        await form.wait_for(state="visible")

        values = {
            "custname": applicant.name,
            "custtel": applicant.phone,
            "custemail": applicant.email,
            "comments": f"Application for '{job_title}' at {company}.",
        }
        for field, value in values.items():
            await page.fill(FIELD_SELECTORS[field], value)
        await capture_screenshot(page, settings.screenshot_dir, "form_filled")

        async with page.expect_navigation(wait_until="domcontentloaded"):
            await form.locator("button").first.click()

        echoed = parse_form_response(await page.inner_text("body"), values)
        await capture_screenshot(page, settings.screenshot_dir, "form_submitted")
        logger.info("Form submitted and verified for %s / %s", job_title, company)
        return echoed
