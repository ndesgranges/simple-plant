"""Select platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)

from .const import DOMAIN, HEALTH_OPTIONS, LOGGER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SimplePlantCoordinator


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


class SimplePlantSelect(SelectEntity):
    """simple_plant select class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__()
        self.entity_description = description
        self._fallback_value = str(entry.data.get("health"))
        self.coordinator: SimplePlantCoordinator = hass.data[DOMAIN][entry.entry_id]

        device = self.coordinator.device

        self.entity_id = f"select.{DOMAIN}_{description.key}_{device}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{device}"

        self._attr_extra_state_attributes = {
            "state_color": False,
        }

        # Set up device info
        self._attr_device_info = self.coordinator.device_info

    @property
    def device(self) -> str | None:
        """Return the device name."""
        return self.coordinator.device

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()

        def warning(msg: str) -> None:
            LOGGER.warning("%s :%s", self.unique_id, msg)

        # Load stored data
        if self.coordinator.data is None:
            warning("Coordinator not ready at initialization")
            return
        data = self.coordinator.data.get(self.unique_id)
        if data is None:
            if self._fallback_value is None:
                warning("Initialization failed as _fallback_value is None")
                return
            await self.async_select_option(self._fallback_value)
            return
        await self.async_select_option(data)

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
