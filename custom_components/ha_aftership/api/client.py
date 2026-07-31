"""
API Client for ha_aftership.

This module provides the API client for communicating with external services.
It demonstrates proper error handling, authentication patterns, and async operations.

For more information on creating API clients:
https://developers.home-assistant.io/docs/api_lib_index
"""

from __future__ import annotations

import aiohttp
import tracking
from tracking import GetTrackingsResponse, auth

from homeassistant.core import HomeAssistant


class AftershipApiClientError(Exception):
    """Base exception to indicate a general API error."""


class AftershipApiClientCommunicationError(
    AftershipApiClientError,
):
    """Exception to indicate a communication error with the API."""


class AftershipApiClientAuthenticationError(
    AftershipApiClientError,
):
    """Exception to indicate an authentication error with the API."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """
    Verify that the API response is valid.

    Raises appropriate exceptions for authentication and HTTP errors.

    Args:
        response: The aiohttp ClientResponse to verify.

    Raises:
        AftershipApiClientAuthenticationError: For 401/403 errors.
        aiohttp.ClientResponseError: For other HTTP errors.

    """
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise AftershipApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class AftershipApiClient:
    """
    API Client for Aftership integration.

    This client demonstrates authentication and API communication patterns
    for Home Assistant integrations. It handles HTTP requests, error handling,
    and credential management.

    For more information on API clients:
    https://developers.home-assistant.io/docs/api_lib_index

    Attributes:
        _username: The username for API authentication.
        _password: The password for API authentication.
        _session: The aiohttp ClientSession for making requests.

    """

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
    ) -> None:
        """
        Initialize the API Client with credentials.

        Args:
            api_key: The API key for authenticating with the Aftership API.

        """
        self.hass = hass
        self._api_key = api_key
        self._client = tracking.Client(tracking.Configuration(api_key=api_key, authentication_type=auth.ApiKey))

    async def async_get_trackings(self) -> GetTrackingsResponse:
        """
        Get trackings from the API.

        This method fetches the current trackings from the Aftership API.

        Returns:
            A GetTrackingsResponse object containing the tracking data.

        Raises:
            AftershipApiClientError: For API errors.

        """
        try:
            return await self.hass.async_add_executor_job(self._client.tracking.get_trackings)
        except Exception as exception:
            msg = f"Failed to fetch AfterShip trackings: {exception}"
            raise AftershipApiClientError(
                msg,
            ) from exception

    async def async_add_tracking(
        self, tracking_number: str, title: str | None = None, courier: str | None = None
    ) -> None:
        """
        Add a new tracking to the API.

        This method adds a new tracking number with the specified title
        to the Aftership API.

        Args:
            tracking_number: The tracking number to add.
            title: The title for the tracking number.
            courier: The courier for the tracking number.

        Raises:
            AftershipApiClientError: For API errors.
        """
        req = tracking.CreateTrackingRequest()
        req.tracking_number = tracking_number
        if title:
            req.title = title
        if courier:
            req.slug = courier
        try:
            await self.hass.async_add_executor_job(
                self._client.tracking.create_tracking,
                req,
            )
        except Exception as exception:
            msg = f"Failed to add AfterShip tracking: {exception}"
            raise AftershipApiClientError(
                msg,
            ) from exception

    async def async_remove_tracking_by_id(self, tracking_id: str) -> None:
        """
        Remove a specific tracking by ID from the API.

        This method removes the tracking information for a specific tracking ID
        from the Aftership API.

        Args:
            tracking_id: The ID of the tracking to remove.
        """
        await self.hass.async_add_executor_job(self._client.tracking.delete_tracking_by_id, tracking_id)

    async def async_test_connection(self) -> bool:
        """
        Test the connection to the Aftership API.

        This method attempts to fetch trackings to verify that the API key is valid
        and that the connection to the Aftership API is working.

        Raises:
            AftershipApiClientError: If the connection test fails.
        """
        try:
            await self.hass.async_add_executor_job(self._client.courier.get_couriers)
        except AftershipApiClientError:
            return False
        else:
            return True
