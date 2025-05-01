"""Button platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SimplePlantCoordinator


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
        self.coordinator: SimplePlantCoordinator = hass.data[DOMAIN][entry.entry_id]

        device = self.coordinator.device

        self.entity_id = f"button.{DOMAIN}_{description.key}_{device}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{device}"

        # Set up device info
        self._attr_device_info = self.coordinator.device_info

    @property
    def device(self) -> str | None:
        """Return the device name."""
        return self.coordinator.device

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_mark_as_watered_toggle()
