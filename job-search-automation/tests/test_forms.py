import json

import pytest

from job_automation.config import Settings
from job_automation.exceptions import ConfigError, FormSubmissionError
from job_automation.forms import Applicant, parse_form_response

EXPECTED = {"custname": "Tanmay", "custemail": "t@example.com"}


def test_matching_echo_is_accepted():
    body = json.dumps({"form": {**EXPECTED, "extra": "ignored"}})
    assert parse_form_response(body, EXPECTED)["custname"] == "Tanmay"


def test_mismatch_and_bad_json_are_rejected():
    with pytest.raises(FormSubmissionError):
        parse_form_response(json.dumps({"form": {"custname": "Someone Else"}}), EXPECTED)
    with pytest.raises(FormSubmissionError):
        parse_form_response("<html>oops</html>", EXPECTED)


def test_applicant_requires_all_env_values():
    with pytest.raises(ConfigError, match="APPLICANT_EMAIL"):
        Applicant.from_settings(Settings(applicant_name="A", applicant_phone="1"))
    settings = Settings(applicant_name="A", applicant_email="a@b.c", applicant_phone="1")
    assert Applicant.from_settings(settings).email == "a@b.c"
