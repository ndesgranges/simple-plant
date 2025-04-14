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

from .const import DOMAIN, LOGGER, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


class SimplePlantBinarySensor(BinarySensorEntity):
    """simple_plant binary_sensor base class."""

    _attr_has_entity_name = True
    _fallback_value: bool

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

        self._attr_native_value: bool | None = None

        self.entity_id = f"binary_sensor.{DOMAIN}_{description.key}_{entry.title}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{entry.title}"

        # Set up device info
        name = entry.title[0].upper() + entry.title[1:]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=name,
            manufacturer=MANUFACTURER,
        )

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
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return None
        return str(self._attr_device_info["name"]).lower()

    def get_dates(self) -> dict[str, date] | None:
        """Get dates from relevants device entites states."""
        states_to_get = {
            "last_watered": f"date.{DOMAIN}_last_watered_{self.device}",
            "nb_days": f"number.{DOMAIN}_days_between_waterings_{self.device}",
        }

        # Get states from hass
        data = {key: self.hass.states.get(eid) for key, eid in states_to_get.items()}

        # Check if all states are available
        if any(
            data[key] is None
            or not data[key].state  # type: ignore noqa: PGH003
            or data[key].state == "unavailable"  # type: ignore noqa: PGH003
            for key in states_to_get
        ):
            LOGGER.warning("%s: Couldn't get all states", self.unique_id)
            return None

        states = {key: data.state for key, data in data.items() if data is not None}

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
        device = str(self._attr_device_info["name"]).lower()

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

    _fallback_value = False

    async def _update_state(self, _event: Event | None = None) -> None:
        """Update the binary sensor state based on other entities."""
        dates = self.get_dates()

        if not dates:
            return

        self._attr_native_value = dates["today"] >= dates["next_watering"]
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

        self._attr_native_value = dates["today"] > dates["next_watering"]
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
