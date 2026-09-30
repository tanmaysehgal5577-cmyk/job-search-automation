"""Project-specific exception hierarchy.

Having one base class lets the CLI distinguish expected, user-facing failures
(bad config, site changed, validation failed) from genuine bugs.
"""


class AutomationError(Exception):
    """Base class for every expected failure raised by this project."""


class ConfigError(AutomationError):
    """Configuration is missing or invalid."""


class NavigationError(AutomationError):
    """A page could not be loaded or returned a bad HTTP status."""


class ValidationError(AutomationError):
    """The automation ran but its result failed a sanity check."""


class FormSubmissionError(AutomationError):
    """A form was submitted but the server response did not match the input."""
