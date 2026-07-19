"""Exception types used across the reasonable package."""
from __future__ import annotations


class ReasonableError(Exception):
    """Base class for all reasonable-package errors."""


class TargetNotFound(ReasonableError):
    """Raised when an `agree --target ...` (or other) reference cannot be
    resolved against the current folded state. Only ever raised for logs
    that were NOT produced through the validated write path (e.g. a
    hand-crafted event list in a test) -- validate.py catches the same
    condition ahead of time and turns it into a normal validation error.
    """
