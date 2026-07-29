"""
Core DataUpdateCoordinator implementation for ha_aftership.

This module contains the main coordinator class that manages data fetching
and updates for all entities in the integration. It handles refresh cycles,
error handling, and triggers reauthentication when needed.

For more information on coordinators:
https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tracking import GetTrackingsResponse

from custom_components.ha_aftership.api import AftershipApiClientError
from custom_components.ha_aftership.const import LOGGER
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.ha_aftership.data import AftershipConfigEntry


class AftershipDataUpdateCoordinator(DataUpdateCoordinator[GetTrackingsResponse]):
    """
    Class to manage fetching data from the API.

    This coordinator handles all data fetching for the integration and distributes
    updates to all entities. It manages:
    - Periodic data updates based on update_interval
    - Error handling and recovery
    - Authentication failure detection and reauthentication triggers
    - Data distribution to all entities
    - Context-based data fetching (only fetch data for active entities)

    For more information:
    https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities

    Attributes:
        config_entry: The config entry for this integration instance.
    """

    config_entry: AftershipConfigEntry

    async def _async_setup(self) -> None:
        """
        Set up the coordinator.

        This method is called automatically during async_config_entry_first_refresh()
        and is the ideal place for one-time initialization tasks such as:
        - Loading device information
        - Setting up event listeners
        - Initializing caches

        This runs before the first data fetch, ensuring any required setup
        is complete before entities start requesting data.
        """
        # Example: Fetch device info once at startup
        # device_info = await self.config_entry.runtime_data.client.get_device_info()
        # self._device_id = device_info["id"]
        LOGGER.debug("Coordinator setup complete for %s", self.config_entry.entry_id)

    async def _async_update_data(self) -> GetTrackingsResponse:
        """
        Fetch data from API endpoint.

        This is the only method that should be implemented in a DataUpdateCoordinator.
        It is called automatically based on the update_interval.

        Context-based fetching:
        The coordinator tracks which entities are currently listening via async_contexts().
        This allows optimizing API calls to only fetch data that's actually needed.
        For example, if only sensor entities are enabled, we can skip fetching switch data.

        The API client uses the credentials from config_entry to authenticate:
        - username: from config_entry.data["username"]
        - password: from config_entry.data["password"]

        Expected API response structure (example):
        {
            "userId": 1,      # Used as device identifier
            "id": 1,          # Data record ID
            "title": "...",   # Additional metadata
            "body": "...",    # Additional content
            # In production, would include:
            # "air_quality": {"aqi": 45, "pm25": 12.3},
            # "filter": {"life_remaining": 75, "runtime_hours": 324},
            # "settings": {"fan_speed": "medium", "humidity": 55}
        }

        Returns:
            The data from the API as a dictionary.

        Raises:
            ConfigEntryAuthFailed: If authentication fails, triggers reauthentication.
            UpdateFailed: If data fetching fails for other reasons, optionally with retry_after.
        """
        try:
            return await self.config_entry.runtime_data.client.async_get_trackings()
        except AftershipApiClientError as exception:
            LOGGER.exception("Error communicating with API")
            # If the API provides rate limit information, you can honor it:
            # if hasattr(exception, 'retry_after'):
            #     raise UpdateFailed(retry_after=exception.retry_after) from exception
            raise UpdateFailed(
                translation_domain="ha_aftership",
                translation_key="update_failed",
            ) from exception

    async def async_add_tracking(self, tracking_number: str, title: str | None = None) -> None:
        """Add a tracking number and refresh data."""
        await self.config_entry.runtime_data.client.async_add_tracking(tracking_number, title)
        await self.async_request_refresh()

    async def async_remove_tracking(self, tracking_number: str) -> None:
        """Find tracking ID by number, remove it, and refresh data."""
        if not self.data.data:
            return
        trackings = self.data.data.trackings
        if trackings is None:
            return
        target_id = next((t.id for t in trackings if t.tracking_number == tracking_number), None)

        if target_id:
            await self.config_entry.runtime_data.client.async_remove_tracking_by_id(target_id)
            await self.async_request_refresh()
        else:
            LOGGER.warning("Tracking number %s not found for removal", tracking_number)
