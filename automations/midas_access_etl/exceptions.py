from __future__ import annotations


class MidasAccessError(Exception):
    """Base exception for Midas Access ETL."""


class MidasAccessAuthError(MidasAccessError):
    """Raised when login or session validation fails."""


class MidasAccessQueryError(MidasAccessError):
    """Raised when the access query fails."""


class MidasAccessValidationError(MidasAccessError):
    """Raised when data quality validation fails."""


class MidasAccessLoadError(MidasAccessError):
    """Raised when persistence fails."""
