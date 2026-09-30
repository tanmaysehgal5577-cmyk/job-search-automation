"""Pure functions to de-duplicate, filter, sort and limit jobs."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from job_automation.models import Job

SORT_OPTIONS = ("title", "company", "location", "posted")


@dataclass(frozen=True)
class SearchCriteria:
    """What the user is looking for."""

    keywords: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    since: date | None = None
    sort_by: str = "title"
    limit: int | None = None


def _haystack(job: Job) -> str:
    return f"{job.title} {job.company} {job.description}".lower()


def deduplicate(jobs: Iterable[Job]) -> list[Job]:
    """Drop repeated postings (same title + company + location), keeping order."""
    seen: set[tuple[str, str, str]] = set()
    unique: list[Job] = []
    for job in jobs:
        key = (job.title.lower(), job.company.lower(), job.location.lower())
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


def _matches(job: Job, criteria: SearchCriteria) -> bool:
    text = _haystack(job)
    if criteria.keywords and not any(k.lower() in text for k in criteria.keywords):
        return False
    if any(word.lower() in text for word in criteria.exclude):
        return False
    location = job.location.lower()
    if criteria.locations and not any(loc.lower() in location for loc in criteria.locations):
        return False
    if criteria.since is not None:
        posted = job.posted_on
        if posted is None or posted < criteria.since:
            return False
    return True


def sort_jobs(jobs: list[Job], sort_by: str) -> list[Job]:
    """Sort by a text column, or newest-first for ``posted``."""
    if sort_by not in SORT_OPTIONS:
        raise ValueError(f"sort_by must be one of {SORT_OPTIONS}, got {sort_by!r}.")
    if sort_by == "posted":
        dated = sorted((j for j in jobs if j.posted_on), key=lambda j: j.posted_on, reverse=True)
        return dated + [j for j in jobs if j.posted_on is None]
    return sorted(jobs, key=lambda j: getattr(j, sort_by).lower())


def apply_criteria(jobs: Iterable[Job], criteria: SearchCriteria) -> list[Job]:
    """Full pipeline: de-duplicate -> filter -> sort -> limit."""
    selected = [job for job in deduplicate(jobs) if _matches(job, criteria)]
    selected = sort_jobs(selected, criteria.sort_by)
    return selected[: criteria.limit] if criteria.limit else selected
