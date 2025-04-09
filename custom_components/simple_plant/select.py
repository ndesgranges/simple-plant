"""Select platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)

from .const import HEALTH_OPTIONS

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
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        SimplePlantSelect(hass, config, entity_description)
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
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"
        self._attr_current_option = _config.data.get("current_health")

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
