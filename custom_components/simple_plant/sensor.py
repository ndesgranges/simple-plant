"""Sensor platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.util.dt import as_local

from .entity import SimplePlantTrackedEntity

if TYPE_CHECKING:
    from datetime import date, datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        device_class=SensorDeviceClass.DATE,
        key="next_watering",
        translation_key="next_watering",
        icon="mdi:clipboard-text-clock",
    ),
)

COLOR_MAPPING = {"Today": "Goldenrod", "Late": "Tomato"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        SimplePlantSensor(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantSensor(SimplePlantTrackedEntity, SensorEntity):
    """simple_plant sensor class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(hass, entry, description, "sensor")
        self._fallback_value: date | None = None
        self._attr_native_value: date | None = None
        self._attr_extra_state_attributes = {
            "state_color": False,
        }

    @property
    def native_value(self) -> date | None:
        """Return true if the binary_sensor is on."""
        return (
            self._fallback_value
            if self._attr_native_value is None
            else self._attr_native_value
        )

    async def _update_state(
        self, _event: Event[EventStateChangedData] | datetime | None = None
    ) -> None:
        """Update the binary sensor state based on other entities."""
        dates = self.coordinator.get_dates()

        if not dates:
            return

        # Color
        today = as_local(dates["today"]).date()
        next_watering = as_local(dates["next_watering"]).date()

        color_key = "OK"
        if today == next_watering:
            color_key = "Today"
        if today > next_watering:
            color_key = "Late"

        if color_key in COLOR_MAPPING:
            self._attr_extra_state_attributes = {
                "state_color": True,
                "color": COLOR_MAPPING[color_key],
            }
        else:
            self._attr_extra_state_attributes = {"state_color": False}

        # Value
        self._attr_native_value = next_watering
        self.async_write_ha_state()
