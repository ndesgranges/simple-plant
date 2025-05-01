"""Date platform for simple_plant."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from homeassistant.components.date import (
    DateEntity,
    DateEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import as_local, as_utc

from .const import DOMAIN
from .coordinator import SimplePlantCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    DateEntityDescription(
        key="last_watered",
        translation_key="last_watered",
        icon="mdi:calendar-check",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the date platform."""
    async_add_entities(
        SimplePlantDate(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SimplePlantDate(CoordinatorEntity[SimplePlantCoordinator], DateEntity):
    """simple_plant date class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: DateEntityDescription,
    ) -> None:
        """Initialize the date class."""
        coordinator: SimplePlantCoordinator = hass.data[DOMAIN][entry.entry_id]
        super().__init__(coordinator)
        self.entity_description = description

        device = self.coordinator.device

        self._fallback_value = as_local(
            datetime.fromisoformat(str(entry.data.get("last_watered")))
        ).date()

        self.entity_id = f"date.{DOMAIN}_{description.key}_{device}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{device}"

        # Set up device info
        self._attr_device_info = self.coordinator.device_info

    @property
    def device(self) -> str | None:
        """Return the device name."""
        return self.coordinator.device

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()
        if not self.native_value:
            await self.async_set_value(self._fallback_value)

    async def async_set_value(self, value: date) -> None:
        """Change the date."""
        # Validate the date is not in the future
        dt = datetime.combine(value, datetime.min.time())
        new_val = as_utc(as_local(dt))
        await self.coordinator.async_set_last_watered(new_val)

    @property
    def native_value(self) -> date | None:
        """Return the date value."""
        if not self.coordinator.data:
            return None

        date_str = self.coordinator.data.get("last_watered")
        if not date_str:
            return None

        return as_local(datetime.fromisoformat(date_str)).date()
