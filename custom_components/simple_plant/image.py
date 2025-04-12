"""Image platform for simple_plant."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
from homeassistant.components.image import (
    ImageEntity,
    ImageEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, IMAGES_MIME_TYPES, LOGGER, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    ImageEntityDescription(
        key="simple_plant_picture",
        icon="mdi:image",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the image platform."""
    async_add_entities(
        SimplePlantImage(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantImage(ImageEntity):
    """simple_plant image class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: ImageEntityDescription,
    ) -> None:
        """Initialize the image class."""
        super().__init__(hass)
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{entry.title}"
        self._attr_image_url = hass.config.path(
            str(entry.data.get("photo")).lstrip("/")
        )
        self._attr_translation_key = "picture"
        self.has_entity_name = True

        self._attr_content_type = self._get_content_type(
            Path(str(entry.data.get("photo")))
        )
        # Set up device info
        name = entry.title[0].upper() + entry.title[1:]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=name,
            manufacturer=MANUFACTURER,
        )

    def _get_content_type(self, path: Path) -> str:
        """Get the content type of the image based on its extension."""
        if path.suffix in IMAGES_MIME_TYPES:
            return IMAGES_MIME_TYPES[path.suffix]
        return "image/jpeg"  # default to jpeg

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""
        file_path = Path(str(self._attr_image_url))
        if file_path.exists():
            async with aiofiles.open(file_path, mode="rb") as file:
                return await file.read()
        LOGGER.error("Image file not found")
        return None
