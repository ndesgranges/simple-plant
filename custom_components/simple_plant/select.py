"""Select platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, HEALTH_OPTIONS, MANUFACTURER
from .data import SimplePlantStore

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="simple_plant_health",
        icon="mdi:heart-pulse",
        options=HEALTH_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        SimplePlantSelect(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantSelect(SelectEntity):
    """simple_plant select class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__()
        self.entity_description = description
        self._store = SimplePlantStore(hass)
        self._attr_unique_id = f"{description.key}_{entry.title}"
        self._fallback_value = str(entry.data.get("current_health"))
        self._attr_translation_key = "health"
        self.has_entity_name = True

        # Set up device info
        name = entry.title[0].upper() + entry.title[1:]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=name,
            manufacturer=MANUFACTURER,
        )

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()
        # Load stored data
        stored_data = await self._store.async_load()
        if self.unique_id in stored_data:
            await self.async_select_option(stored_data[self.unique_id])
        else:
            await self.async_select_option(self._fallback_value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        # Save to persistent storage
        await self._store.async_save({self.unique_id: option})
