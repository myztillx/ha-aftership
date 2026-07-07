"""
API package for ha_aftership.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client. Entities must never
    import or call the API client directly.

Exception hierarchy:
    AftershipApiClientError (base)
    ├── AftershipApiClientCommunicationError (network/timeout)
    └── AftershipApiClientAuthenticationError (401/403)

Coordinator exception mapping:
    ApiClientAuthenticationError → ConfigEntryAuthFailed (triggers reauth)
    ApiClientCommunicationError → UpdateFailed (auto-retry)
    ApiClientError             → UpdateFailed (auto-retry)
"""

from .client import (
    AftershipApiClient,
    AftershipApiClientAuthenticationError,
    AftershipApiClientCommunicationError,
    AftershipApiClientError,
)

__all__ = [
    "AftershipApiClient",
    "AftershipApiClientAuthenticationError",
    "AftershipApiClientCommunicationError",
    "AftershipApiClientError",
]
