"""Binary sensor platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.util.dt import as_local

from .entity import SimplePlantTrackedEntity

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


class SimplePlantBinarySensor(SimplePlantTrackedEntity, BinarySensorEntity):
    """simple_plant binary_sensor base class."""

    _fallback_value: bool = False
    _attr_should_poll = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(hass, entry, description, "binary_sensor")
        self._attr_native_value: bool | None = None

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return (
            self._fallback_value
            if self._attr_native_value is None
            else self._attr_native_value
        )

    def get_dates(self) -> dict[str, datetime] | None:
        """Get dates from relevants device entites states."""
        return self.coordinator.get_dates()

    async def _update_state(
        self,
        _event: Event[EventStateChangedData] | datetime | None = None,
    ) -> None:
        """Update the binary sensor state based on other entities."""
        raise NotImplementedError


class SimplePlantTodo(SimplePlantBinarySensor):
    """simple_plant binary_sensor for todo."""

    _fallback_value = False

    async def _update_state(self, _event: Event | None = None) -> None:
        """Update the binary sensor state based on other entities."""
        dates = self.get_dates()

        if not dates:
            return

        self._attr_native_value = (
            as_local(dates["today"]).date() >= as_local(dates["next_watering"]).date()
        )
        self.async_write_ha_state()


class SimplePlantProblem(SimplePlantBinarySensor):
    """simple_plant binary_sensor for problem."""

    _fallback_value = False
    _attr_translation_key = "problem"

    async def _update_state(self, _event: Event | None = None) -> None:
        """Update the binary sensor state based on other entities."""
        dates = self.get_dates()

        if not dates:
            return

        self._attr_native_value = (
            as_local(dates["today"]).date() > as_local(dates["next_watering"]).date()
        )
        self.async_write_ha_state()


ENTITIES = [
    {
        "class": SimplePlantTodo,
        "description": BinarySensorEntityDescription(
            key="todo",
            translation_key="todo",
            name="Simple Plant Binary Sensor Todo",
            icon="mdi:water-check-outline",
        ),
    },
    {
        "class": SimplePlantProblem,
        "description": BinarySensorEntityDescription(
            key="problem",
            translation_key="problem",
            name="Simple Plant Binary Sensor Problem",
            device_class=BinarySensorDeviceClass.PROBLEM,
            icon="mdi:water-alert-outline",
        ),
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        entity["class"](hass, entry, entity["description"]) for entity in ENTITIES
    )
