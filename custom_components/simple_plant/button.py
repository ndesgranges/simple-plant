"""Button platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key="simple_plant_mark_watered",
        name="Simple Plant Mark as watered action",
        icon="mdi:watering-can",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        SimplePlantButton(hass, config, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantButton(ButtonEntity):
    """simple_plant button class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        _config: ConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"

    def press(self) -> None:
        """Press the button."""
        raise NotImplementedError
