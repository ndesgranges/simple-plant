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
        key="mark_watered",
        translation_key="mark_watered",
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

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__()
        self.entity_description = description
        self.coordinator = hass.data[DOMAIN][entry.entry_id]

        self.entity_id = f"button.{DOMAIN}_{description.key}_{entry.title}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{entry.title}"

        # Set up device info
        name = entry.title[0].upper() + entry.title[1:]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=name,
            manufacturer=MANUFACTURER,
        )

    @property
    def device(self) -> str | None:
        """Return the device name."""
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return None
        return str(self._attr_device_info["name"]).lower()

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_mark_as_watered_toggle()
