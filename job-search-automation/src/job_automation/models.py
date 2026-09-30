"""Domain model: a scraped job posting and the parsing rules around it."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)


def _clean(value: Any) -> str:
    """Collapse whitespace and turn ``None`` into an empty string."""
    return " ".join(str(value or "").split())


@dataclass(frozen=True)
class Job:
    """A single job posting."""

    title: str
    company: str
    location: str
    posted_date: str = ""
    url: str = ""
    apply_url: str = ""
    description: str = ""

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any]) -> Job:
        """Build a validated ``Job`` from the dict returned by the page script."""
        title = _clean(raw.get("title"))
        company = _clean(raw.get("company"))
        if not title or not company:
            raise ValueError("A job needs at least a title and a company.")
        return cls(
            title=title,
            company=company,
            location=_clean(raw.get("location")) or "Not specified",
            posted_date=_clean(raw.get("posted")),
            url=_clean(raw.get("learn_url")),
            apply_url=_clean(raw.get("apply_url")),
        )

    @property
    def posted_on(self) -> date | None:
        """Posting date as a ``date`` or ``None`` if missing/unparseable."""
        try:
            return date.fromisoformat(self.posted_date)
        except ValueError:
            return None

    def to_row(self) -> dict[str, str]:
        return asdict(self)


def parse_jobs(raw_items: Iterable[Mapping[str, Any]]) -> tuple[list[Job], int]:
    """Convert raw dicts to jobs. Returns ``(jobs, skipped_count)``.

    Malformed entries are logged and skipped so one bad card never kills a run.
    """
    jobs: list[Job] = []
    skipped = 0
    for index, raw in enumerate(raw_items):
        try:
            jobs.append(Job.from_raw(raw))
        except ValueError as exc:
            skipped += 1
            logger.warning("Skipping malformed job card #%d: %s", index, exc)
    return jobs, skipped
