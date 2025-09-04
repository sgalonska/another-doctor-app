# Another Doctor Python Utilities

Shared Python utilities and common functionality for the Another Doctor medical platform.

## Features

- HTTP client utilities
- Data validation with Pydantic
- Retry logic with Tenacity
- Structured logging with Structlog

## Usage

This package is used internally by the Another Doctor backend and workers.

```python
from another_doctor_utils import some_utility
```

## Development

Install in development mode:

```bash
pip install -e .
```

Run tests:

```bash
pytest
```