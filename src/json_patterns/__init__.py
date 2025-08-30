"""A package for matching JSON objects using pattern-based templates."""

from .exceptions import (
    JSONKeyMismatchError,
    JSONListLengthMismatchError,
    JSONPatternError,
    JSONPatternMatchError,
    JSONPatternTypeError,
    JSONPatternValueInconsistencyError,
    JSONStructureError,
    JSONValueMismatchError,
)
from .json_matcher import JSONMatcher
from .patterns import compile_template

__version__ = "0.1.0"

__all__ = [
    "JSONMatcher",
    "compile_template",
    "JSONPatternError",
    "JSONStructureError",
    "JSONKeyMismatchError",
    "JSONListLengthMismatchError",
    "JSONValueMismatchError",
    "JSONPatternMatchError",
    "JSONPatternValueInconsistencyError",
    "JSONPatternTypeError",
]
