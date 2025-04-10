"""Date platform for simple_plant."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from homeassistant.components.date import (
    DateEntity,
    DateEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    DateEntityDescription(
        key="simple_plant_last_watered",
        name="Simple Plant Last Watered",
        icon="mdi:calendar-check",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the date platform."""
    async_add_entities(
        SimplePlantDate(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantDate(DateEntity):
    """simple_plant date class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        entry: ConfigEntry,
        description: DateEntityDescription,
    ) -> None:
        """Initialize the date class."""
        super().__init__()
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{entry.title}"
        self._attr_name = f"{description.key}_{entry.title}"
        self._attr_native_value = date.fromisoformat(
            str(entry.data.get("last_time_watered"))
        )
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=entry.title,
            manufacturer=MANUFACTURER,
        )

    def set_value(self, value: date) -> None:
        """Change the date."""
        self._attr_native_value = value
