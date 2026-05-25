# pylint: disable=duplicate-code
"""Number platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTime

from .entity import SimplePlantStoredEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="days_between_waterings",
        translation_key="days_between_waterings",
        device_class=NumberDeviceClass.DURATION,
        mode=NumberMode.BOX,
        icon="mdi:counter",
        native_step=0,
        native_unit_of_measurement=UnitOfTime.DAYS,
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


class SimplePlantNumber(SimplePlantStoredEntity, NumberEntity):  # pylint: disable=abstract-method
    """simple_plant number class."""

    _attr_should_poll = False
    _attr_native_min_value = 1
    _attr_native_max_value = 60
    _attr_native_step = 1

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(hass, entry, description, "number")
        self._fallback_value = entry.data.get("days_between_waterings")
        self._attr_native_value: float | None = None

    async def _restore_value(self, value: Any) -> None:
        """Restore a stored or fallback value."""
        await self.async_set_native_value(float(value))

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()

        # Save to persistent storage
        if self.unique_id is not None:
            await self.coordinator.async_store_value(self.unique_id, str(value))
