from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Any


class BaseConnector(ABC):
    """Abstract connector interface for importing rows of data.

    Implementations should provide a method that accepts an iterable of
    row mappings (string keys) and return processed results or raise
    informative exceptions.
    """

    @abstractmethod
    def import_rows(self, rows: Iterable[Mapping[str, Any]]):
        """Process an iterable of row mappings.

        Implementations may return any structure (e.g. list of models)
        or a tuple (successes, errors)."""

        raise NotImplementedError
