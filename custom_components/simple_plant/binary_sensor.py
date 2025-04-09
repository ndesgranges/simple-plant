"""Binary sensor platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="simple_plant_todo",
        name="Simple Plant Binary Sensor Todo",
        # device_class=BinarySensorDeviceClass.MOISTURE,  # noqa: ERA001
        icon="mdi:water-check-outline",
    ),
    BinarySensorEntityDescription(
        key="simple_plant_problem",
        name="Simple Plant Binary Sensor Problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:water-alert-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        SimplePlantBinarySensor(hass, config, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantBinarySensor(BinarySensorEntity):
    """simple_plant binary_sensor class."""

    def __init__(
        self,
        _hass: HomeAssistant,
        _config: ConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        self.entity_description = description
        self._attr_unique_id = f"{description.key}_{_config.title}"
        self._attr_name = f"{description.key}_{_config.title}"
        self._attr_native_value = False

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self._attr_native_value
