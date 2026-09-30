import pytest

from job_automation.config import Settings
from job_automation.exceptions import ConfigError


def test_defaults_when_environment_is_empty():
    settings = Settings.from_env(environ={})
    assert settings.browser == "chromium"
    assert settings.headless is True
    assert settings.timeout_ms == 30_000


def test_values_are_read_and_normalised():
    settings = Settings.from_env(environ={"BROWSER": "Firefox", "HEADLESS": "no", "MAX_RETRIES": "5"})
    assert (settings.browser, settings.headless, settings.max_retries) == ("firefox", False, 5)


@pytest.mark.parametrize(
    "environ",
    [{"BROWSER": "netscape"}, {"HEADLESS": "maybe"}, {"TIMEOUT_MS": "abc"},
     {"MAX_RETRIES": "0"}, {"LOG_LEVEL": "LOUD"}],
)
def test_invalid_values_raise_config_error(environ):
    with pytest.raises(ConfigError):
        Settings.from_env(environ=environ)
