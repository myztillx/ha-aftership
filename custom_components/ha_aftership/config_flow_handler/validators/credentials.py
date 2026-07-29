"""
Credential validators.

Validation functions for user credentials and authentication.

When this file grows, consider splitting into:
- credentials.py: Basic credential validation
- oauth.py: OAuth-specific validation
- api_auth.py: API authentication methods
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ha_aftership.api import AftershipApiClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_credentials(hass: HomeAssistant, api_key: str) -> None:
    """
    Validate user credentials by testing API connection.

    Args:
        hass: Home Assistant instance.
        api_key: The API key to validate.

    Raises:
        AftershipApiClientAuthenticationError: If credentials are invalid.
        AftershipApiClientCommunicationError: If communication fails.
        AftershipApiClientError: For other API errors.

    """
    client = AftershipApiClient(hass, api_key)
    await client.async_test_connection()  # May raise authentication/communication errors


__all__ = [
    "validate_credentials",
]
