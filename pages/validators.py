# validators.py

import os

from django.core.exceptions import ValidationError
from pathvalidate import ValidationError as PathValidationError
from pathvalidate import validate_filepath


def validate_path(value) -> None:
    """
    Validates the given path by checking if it is a valid filepath.

    Args:
        value (str): The path to be validated.

    Raises:
        ValidationError: If the path is invalid.

    """
    try:
        # automatically uses the platform the Python code runs on.
        validate_filepath(os.path.join(value, "test.txt"), platform="auto")
    except PathValidationError as e:
        raise ValidationError(e) from e
