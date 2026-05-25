# pylint: disable=duplicate-code
"""Select platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)

from .const import HEALTH_OPTIONS
from .entity import SimplePlantStoredEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="health",
        translation_key="health",
        icon="mdi:heart-pulse",
        options=HEALTH_OPTIONS,
    ),
)

COLOR_MAPPING = {
    "poor": "Tomato",
    "fair": "Yellow",
    "good": "GreenYellow",
    "verygood": "LawnGreen",
    "excellent": "LimeGreen",
}


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


class SimplePlantSelect(SimplePlantStoredEntity, SelectEntity):  # pylint: disable=abstract-method
    """simple_plant select class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(hass, entry, description, "select")
        self._fallback_value = str(entry.data.get("health"))
        self._attr_extra_state_attributes = {
            "state_color": False,
        }
        self._attr_current_option: str | None = None

    async def _restore_value(self, value: Any) -> None:
        """Restore a stored or fallback value."""
        await self.async_select_option(value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        # Color
        if option in COLOR_MAPPING:
            self._attr_extra_state_attributes = {
                "state_color": True,
                "color": COLOR_MAPPING[option],
            }
        else:
            self._attr_extra_state_attributes = {"state_color": False}
        # Save to persistent storage
        if self.unique_id is not None:
            await self.coordinator.async_store_value(self.unique_id, option)
