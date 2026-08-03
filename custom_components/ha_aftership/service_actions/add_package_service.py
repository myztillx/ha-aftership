"""Function call for aftership add_package service."""

import asyncio
from typing import Final

import voluptuous as vol

from custom_components.ha_aftership.const import ATTR_COURIER, ATTR_TITLE, ATTR_TRACKING_NUMBER, DOMAIN, LOGGER
from custom_components.ha_aftership.data import AftershipConfigEntry
from homeassistant.const import ATTR_CONFIG_ENTRY_ID
from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv, service

SERVICE_ADD_PACKAGE_SCHEMA: Final = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_TRACKING_NUMBER): cv.string,
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_COURIER): cv.string,
    }
)


async def add_package(call: ServiceCall) -> None:
    """Handle the add_package service call."""
    LOGGER.info("Add package service called with data: %s", call.data)

    tracking_number: str = call.data[ATTR_TRACKING_NUMBER]
    title = call.data.get(ATTR_TITLE, None)
    courier = call.data.get(ATTR_COURIER, None)

    entry: AftershipConfigEntry = service.async_get_config_entry(call.hass, DOMAIN, call.data[ATTR_CONFIG_ENTRY_ID])

    aftership_runtime = entry.runtime_data

    # 1. Add the package to the API
    await aftership_runtime.client.async_add_tracking(tracking_number, title, courier)

    # 2. Define a small helper function for the background work
    async def delayed_refresh() -> None:
        await asyncio.sleep(10)
        await aftership_runtime.coordinator.async_request_refresh()

    # 3. Fire and forget! Send the helper function to the background
    call.hass.async_create_task(delayed_refresh())
