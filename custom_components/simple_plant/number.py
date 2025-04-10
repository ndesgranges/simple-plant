"""Number platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="simple_plant_days_between_waterings",
        name="Simple Plant Days Between Waterings",
        device_class=NumberDeviceClass.DURATION,
        mode=NumberMode.BOX,
        icon="mdi:counter",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        SimplePlantNumber(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantNumber(NumberEntity):
    """simple_plant number class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        _config: ConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__()
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"

        self._attr_native_min_value = 1
        self._attr_native_max_value = 60
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "days"

        self._attr_native_value = _config.data.get("days_between_watering")

        # Set up device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{_config.title}")},
            name=_config.title,
            manufacturer=MANUFACTURER,
        )
