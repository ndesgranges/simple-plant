"""Image platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.image import (
    ImageEntity,
    ImageEntityDescription,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    ImageEntityDescription(
        key="simple_plant_picture",
        name="Simple Plant Picture",
        icon="mdi:image",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the image platform."""
    async_add_entities(
        SimplePlantImage(hass, config, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantImage(ImageEntity):
    """simple_plant image class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        _config: ConfigEntry,
        description: ImageEntityDescription,
    ) -> None:
        """Initialize the image class."""
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"
        self._attr_image_url = _config.data.get("photo")
