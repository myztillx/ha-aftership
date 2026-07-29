"""Diagnostic sensors for ha_aftership."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from tracking.models import Tag, Tracking

from custom_components.ha_aftership.const import LOGGER
from custom_components.ha_aftership.coordinator import AftershipDataUpdateCoordinator
from custom_components.ha_aftership.entity.base import AftershipEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import MATCH_ALL

if TYPE_CHECKING:
    from custom_components.ha_aftership.coordinator import AftershipDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class AfterShipSensorEntityDescription(SensorEntityDescription):
    """Describes an AfterShip sensor entity."""

    filter_fn: Callable[[Tag | None], bool]


SENSOR_TYPES: tuple[AfterShipSensorEntityDescription, ...] = (
    AfterShipSensorEntityDescription(
        key="total",
        name="Total Packages",
        # translation_key="filter_life",
        icon="mdi:package-variant",
        # entity_category=EntityCategory.DIAGNOSTIC,
        # device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement="packages",
        # suggested_display_precision=0,
        # state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
        filter_fn=lambda tag: True,  # Matches all tags
    ),
    AfterShipSensorEntityDescription(
        key="in_transit",
        name="In Transit Packages",
        icon="mdi:truck-delivery",
        native_unit_of_measurement="packages",
        # state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
        filter_fn=lambda tag: tag in [Tag.PENDING, Tag.IN_TRANSIT, Tag.OUT_FOR_DELIVERY],
    ),
    AfterShipSensorEntityDescription(
        key="delivered",
        name="Delivered Packages",
        icon="mdi:package-variant-closed-check",
        native_unit_of_measurement="packages",
        # state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
        filter_fn=lambda tag: tag == Tag.DELIVERED,
    ),
)


class AftershipDiagnosticSensor(SensorEntity, AftershipEntity):
    """Diagnostic sensor class for filter and runtime."""

    entity_description: AfterShipSensorEntityDescription

    # Automatically exclude all attributes from history recording
    _unrecorded_attributes = frozenset({MATCH_ALL})

    def __init__(
        self,
        coordinator: AftershipDataUpdateCoordinator,
        entity_description: AfterShipSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> int:
        """Return the calculated count of filtered packages."""
        return len(self._get_filtered_trackings())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the detailed state attributes."""
        LOGGER.debug("Calculating extra_state_attributes for sensor '%s'.", self.entity_description.key)
        filtered_trackings = self._get_filtered_trackings()
        attrs: dict[str, Any] = {"trackings": []}

        for tracking in filtered_trackings:
            # Extract detailed tracking info for the UI
            tracking_info: dict[str, Any] = {
                "tracking_number": tracking.tracking_number,
                "slug": tracking.slug,
                "tag": tracking.tag.value if tracking.tag else None,
                "subtag": tracking.subtag,
                "title": tracking.title,
                "created_at": tracking.created_at,
                "updated_at": tracking.updated_at,
                "expected_delivery": (
                    tracking.courier_estimated_delivery_date.estimated_delivery_date
                    if tracking.courier_estimated_delivery_date
                    else None
                ),
            }
            if hasattr(tracking, "checkpoints") and tracking.checkpoints:
                checkpoints = []
                for checkpoint in tracking.checkpoints:
                    checkpoint_info = {
                        "checkpoint_time": checkpoint.checkpoint_time,
                        "location": checkpoint.location,
                        "city": checkpoint.city,
                        "state": checkpoint.state,
                        "postal_code": checkpoint.postal_code,
                        "country": checkpoint.country_region,
                        "message": checkpoint.message,
                        "tag": checkpoint.tag.value if checkpoint.tag else None,
                    }
                    checkpoints.append(checkpoint_info)
                tracking_info["checkpoints"] = checkpoints
            # This one works as well, but is less explicit and may include more data than desired
            # tracking_info = tracking.to_json()

            attrs["trackings"].append(tracking_info)

        return attrs

    def _get_filtered_trackings(self) -> list[Tracking]:
        """Safely fetch and filter tracking entities from the coordinator."""
        if not self.coordinator.data or not self.coordinator.data.data or not self.coordinator.data.data.trackings:
            LOGGER.debug("No trackings found in coordinator data. Returning empty list.")
            return []

        # Filter the trackings based on the lambda function defined in the description
        return [t for t in self.coordinator.data.data.trackings if self.entity_description.filter_fn(t.tag)]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Diagnostic entities should always be available to show status
        return True
