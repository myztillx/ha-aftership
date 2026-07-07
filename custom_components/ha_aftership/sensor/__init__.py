"""Sensor platform for ha_aftership."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ha_aftership.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.sensor import SensorEntityDescription

from .air_quality import ENTITY_DESCRIPTIONS as AIR_QUALITY_DESCRIPTIONS, AftershipAirQualitySensor
from .diagnostic import ENTITY_DESCRIPTIONS as DIAGNOSTIC_DESCRIPTIONS, AftershipDiagnosticSensor

if TYPE_CHECKING:
    from custom_components.ha_aftership.data import AftershipConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    *AIR_QUALITY_DESCRIPTIONS,
    *DIAGNOSTIC_DESCRIPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AftershipConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # Add air quality sensors
    async_add_entities(
        AftershipAirQualitySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in AIR_QUALITY_DESCRIPTIONS
    )
    # Add diagnostic sensors
    async_add_entities(
        AftershipDiagnosticSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in DIAGNOSTIC_DESCRIPTIONS
    )
