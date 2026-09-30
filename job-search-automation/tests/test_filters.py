from datetime import date

import pytest

from job_automation.filters import SearchCriteria, apply_criteria, deduplicate, sort_jobs


def test_deduplicate_keeps_first_occurrence(jobs):
    assert len(deduplicate(jobs)) == 4


def test_keywords_use_or_logic_and_ignore_case(jobs):
    result = apply_criteria(jobs, SearchCriteria(keywords=("PYTHON", "analyst")))
    assert {j.title for j in result} == {"Python Developer", "Data Analyst"}


def test_exclude_and_location(jobs):
    criteria = SearchCriteria(locations=("sydney",), exclude=("analyst",))
    assert [j.title for j in apply_criteria(jobs, criteria)] == ["Python Developer"]


def test_since_drops_older_and_undated_jobs(jobs):
    result = apply_criteria(jobs, SearchCriteria(since=date(2021, 4, 1)))
    assert {j.company for j in result} == {"Acme", "Globex"}


def test_sort_by_posted_is_newest_first_with_undated_last(jobs):
    ordered = sort_jobs(deduplicate(jobs), "posted")
    assert [j.company for j in ordered] == ["Acme", "Globex", "Initech", "Umbrella"]


def test_limit(jobs):
    assert len(apply_criteria(jobs, SearchCriteria(limit=2))) == 2


def test_invalid_sort_raises(jobs):
    with pytest.raises(ValueError):
        sort_jobs(jobs, "salary")
