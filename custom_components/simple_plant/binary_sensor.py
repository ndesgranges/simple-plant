"""Binary sensor platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.util.dt import as_local

from .const import DOMAIN

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SimplePlantCoordinator


class SimplePlantBinarySensor(BinarySensorEntity):
    """simple_plant binary_sensor base class."""

    _attr_has_entity_name = True
    _fallback_value: bool = False

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__()
        self._hass = hass
        self.entity_description = description
        self.coordinator: SimplePlantCoordinator = hass.data[DOMAIN][entry.entry_id]

        self._attr_should_poll = True

        device = self.coordinator.device

        self._attr_native_value: bool | None = None

        self.entity_id = f"binary_sensor.{DOMAIN}_{description.key}_{device}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{device}"

        # Set up device info
        self._attr_device_info = self.coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return (
            self._fallback_value
            if self._attr_native_value is None
            else self._attr_native_value
        )

    @property
    def device(self) -> str | None:
        """Return the device name."""
        return self.coordinator.device

    def get_dates(self) -> dict[str, datetime] | None:
        """Get dates from relevants device entites states."""
        return self.coordinator.get_dates()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        device = self.coordinator.device

        # Subscribe to state changes
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                f"date.{DOMAIN}_last_watered_{device}",
                self._update_state,
            )
        )
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                f"number.{DOMAIN}_days_between_waterings_{device}",
                self._update_state,
            )
        )
        self.async_on_remove(
            async_track_time_change(
                self.hass,
                self._update_state,
                hour=0,
                minute=0,
                second=0,
            )
        )

        # Initial update
        await self._update_state()

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
