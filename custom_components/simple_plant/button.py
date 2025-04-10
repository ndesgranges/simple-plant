"""Button platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER

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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        SimplePlantButton(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantButton(ButtonEntity):
    """simple_plant button class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        entry: ConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__()
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{entry.title}"
        self._attr_name = f"{description.key}_{entry.title}"
        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=entry.title,
            manufacturer=MANUFACTURER,
        )

    def press(self) -> None:
        """Press the button."""
        raise NotImplementedError
