"""Interface wrapper for web search functionality.

This module intentionally defines only the public interface. The concrete
network integration should be wired in later.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SearchResult:
    """Result returned by :func:`search`.

    Attributes:
        summary: High-level summary of the search results.
        sources: Source URLs or identifiers that back the summary.
    """

    summary: str
    sources: List[str]


def search(query: str) -> SearchResult:
    """Search the web for ``query``.

    TODO:
        Wire this function to a real network-backed provider once runtime
        configuration for API credentials and provider selection is available.

    Raises:
        NotImplementedError: Always raised until provider integration is added.
    """

    raise NotImplementedError(
        "Web search is not configured. TODO: connect this wrapper to a "
        "network search provider and credentials."
    )
