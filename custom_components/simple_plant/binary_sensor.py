"""Binary sensor platform for simple_plant."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


class SimplePlantBinarySensor(BinarySensorEntity):
    """simple_plant binary_sensor base class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__()
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{entry.title}"
        self._attr_name = f"{description.key}_{entry.title}"
        self._attr_native_value = False
        self._hass = hass
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=entry.title,
            manufacturer=MANUFACTURER,
        )

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self._attr_native_value

    def get_dates(self) -> dict[str, date] | None:
        """Get dates from relevants device entites states."""
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return None
        device = self._attr_device_info["name"]

        states_to_get = {
            "last_watered": f"date.{DOMAIN}_last_watered_{device}",
            "nb_days": f"number.{DOMAIN}_days_between_waterings_{device}",
        }

        # Get states from hass
        states = {key: self.hass.states.get(eid) for key, eid in states_to_get.items()}

        # Verify the data is available
        for data in states.values():
            if not data or data == "unavailable":
                return None
        # Extract the values
        states = {key: data.state for key, data in states.items() if data is not None}

        last_watered_date = date.fromisoformat(states["last_watered"])
        nb_days = float(states["nb_days"])

        return {
            "last_watered": last_watered_date,
            "next_watering": last_watered_date + timedelta(days=nb_days),
            "today": date.today(),  # noqa: DTZ011
        }

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return
        device = self._attr_device_info["name"]

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

        # Initial update
        await self._update_state()

    async def _update_state(
        self, _event: Event[EventStateChangedData] | None = None
    ) -> None:
        """Update the binary sensor state based on other entities."""
        raise NotImplementedError


class SimplePlantTodo(SimplePlantBinarySensor):
    """simple_plant binary_sensor for todo."""

    async def _update_state(self, _event: Event | None = None) -> None:
        """Update the binary sensor state based on other entities."""
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return
        dates = self.get_dates()

        if not dates:
            return

        self._attr_native_value = dates["today"] >= dates["next_watering"]
        self.async_write_ha_state()


class SimplePlantProblem(SimplePlantBinarySensor):
    """simple_plant binary_sensor for todo."""

    async def _update_state(self, _event: Event | None = None) -> None:
        """Update the binary sensor state based on other entities."""
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return
        dates = self.get_dates()

        if not dates:
            return

        self._attr_native_value = dates["today"] > dates["next_watering"]
        self.async_write_ha_state()


ENTITIES = [
    {
        "class": SimplePlantTodo,
        "description": BinarySensorEntityDescription(
            key="simple_plant_todo",
            name="Simple Plant Binary Sensor Todo",
            icon="mdi:water-check-outline",
        ),
    },
    {
        "class": SimplePlantProblem,
        "description": BinarySensorEntityDescription(
            key="simple_plant_problem",
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
