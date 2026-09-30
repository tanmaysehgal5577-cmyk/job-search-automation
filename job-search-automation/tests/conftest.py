import pytest

from job_automation.models import Job


@pytest.fixture
def jobs() -> list[Job]:
    return [
        Job("Python Developer", "Acme", "Sydney, AU", "2021-04-20", "https://x/1", "https://x/1a"),
        Job("Senior Java Engineer", "Globex", "London, UK", "2021-04-10", "https://x/2", "https://x/2a"),
        Job("Data Analyst", "Initech", "Sydney, AU", "2021-03-01", "https://x/3", "https://x/3a"),
        Job("Python Developer", "Acme", "Sydney, AU", "2021-04-20", "https://x/1", "https://x/1a"),
        Job("Undated Role", "Umbrella", "Not specified"),
    ]
