import pytest

from job_automation.models import Job, parse_jobs


def test_from_raw_cleans_whitespace_and_defaults_location():
    job = Job.from_raw({"title": "  Dev \n Ops ", "company": "Acme", "location": " ", "posted": "2021-04-01"})
    assert job.title == "Dev Ops"
    assert job.location == "Not specified"
    assert job.posted_on.isoformat() == "2021-04-01"


@pytest.mark.parametrize("raw", [{}, {"title": "x"}, {"company": "y"}, {"title": " ", "company": "y"}])
def test_from_raw_requires_title_and_company(raw):
    with pytest.raises(ValueError):
        Job.from_raw(raw)


def test_parse_jobs_skips_bad_items_and_counts_them():
    jobs, skipped = parse_jobs([{"title": "A", "company": "B"}, {"title": ""}, {"company": "C"}])
    assert len(jobs) == 1
    assert skipped == 2


def test_posted_on_is_none_for_bad_dates():
    assert Job("A", "B", "C", posted_date="not-a-date").posted_on is None
