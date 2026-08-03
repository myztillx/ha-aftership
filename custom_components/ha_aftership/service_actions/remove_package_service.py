"""Function call for aftership remove_package service."""

import asyncio
from typing import Final

import voluptuous as vol

from custom_components.ha_aftership.const import ATTR_COURIER, ATTR_TITLE, ATTR_TRACKING_NUMBER, DOMAIN, LOGGER
from custom_components.ha_aftership.data import AftershipConfigEntry
from homeassistant.const import ATTR_CONFIG_ENTRY_ID
from homeassistant.core import ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, service

SERVICE_REMOVE_PACKAGE_SCHEMA: Final = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_TRACKING_NUMBER): cv.string,
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_COURIER): cv.string,
    }
)


async def remove_package(call: ServiceCall) -> None:
    """Handle the remove_package service call."""
    LOGGER.info("Remove package service called with data: %s", call.data)

    tracking_number: str = call.data[ATTR_TRACKING_NUMBER]

    entry: AftershipConfigEntry = service.async_get_config_entry(call.hass, DOMAIN, call.data[ATTR_CONFIG_ENTRY_ID])

    aftership_runtime = entry.runtime_data

    # 1. Validate that the tracking number exists before attempting to remove it
    coordinator_data = aftership_runtime.coordinator.data or []
    # LOGGER.info("Current coordinator data: %s", json.dumps(coordinator_data.to_json()))
    if not coordinator_data.data or not hasattr(coordinator_data.data, "trackings"):
        raise ServiceValidationError("No tracking data available to validate against.")

    trackings = (
        coordinator_data.data.trackings if coordinator_data and hasattr(coordinator_data.data, "trackings") else []
    )
    if not trackings or len(trackings) == 0:
        raise ServiceValidationError("No trackings found in Aftership data.")

    valid_tracking_numbers = [
        pkg.tracking_number for pkg in trackings if hasattr(pkg, "tracking_number") and pkg.tracking_number
    ]

    if tracking_number not in valid_tracking_numbers:
        raise ServiceValidationError(f"Tracking number {tracking_number} does not exist in Aftership.")

    # 2. Get the tracking ID for the specified tracking number
    tracking_id = next((pkg.id for pkg in trackings if pkg.tracking_number == tracking_number), None)
    if not tracking_id:
        raise ServiceValidationError(f"Tracking ID for tracking number {tracking_number} not found.")

    # 3. Remove the package from the API
    await aftership_runtime.client.async_remove_tracking_by_id(tracking_id)

    # 4. Define a small helper function for the background work
    async def delayed_refresh() -> None:
        await asyncio.sleep(10)
        await aftership_runtime.coordinator.async_request_refresh()

    # 5. Fire and forget! Send the helper function to the background
    call.hass.async_create_task(delayed_refresh())
