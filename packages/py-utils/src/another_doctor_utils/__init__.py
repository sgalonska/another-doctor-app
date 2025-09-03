"""Another Doctor Python Utilities

Shared utilities for HTTP clients, retry logic, logging, and validation.
"""

from .http_client import HTTPClient, APIError
from .retry import with_retry, RetryConfig
from .logging import setup_logging, get_logger
from .validation import validate_case_json, validate_match_result

__version__ = "0.1.0"
__all__ = [
    "HTTPClient",
    "APIError", 
    "with_retry",
    "RetryConfig",
    "setup_logging",
    "get_logger",
    "validate_case_json",
    "validate_match_result",
]