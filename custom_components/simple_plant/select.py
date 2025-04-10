"""Select platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, HEALTH_OPTIONS, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="simple_plant_health",
        name="Simple Plant Health",
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
        _hass: HomeAssistant,
        _config: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__()
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"
        self._attr_current_option = _config.data.get("current_health")

        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{_config.title}")},
            name=_config.title,
            manufacturer=MANUFACTURER,
        )

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
