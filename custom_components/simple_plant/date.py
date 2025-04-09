"""Date platform for simple_plant."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from homeassistant.components.date import (
    DateEntity,
    DateEntityDescription,
)

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
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the date platform."""
    async_add_entities(
        SimplePlantDate(hass, config, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantDate(DateEntity):
    """simple_plant date class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        _config: ConfigEntry,
        description: DateEntityDescription,
    ) -> None:
        """Initialize the date class."""
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"
        self._attr_ = date.fromisoformat(str(_config.data.get("last_time_watered")))

    def set_value(self, value: date) -> None:
        """Change the date."""
        self._attr_native_value = value
