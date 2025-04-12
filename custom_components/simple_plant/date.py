"""Date platform for simple_plant."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from homeassistant.components.date import (
    DateEntity,
    DateEntityDescription,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER
from .data import SimplePlantStore

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


class SimplePlantDate(DateEntity):
    """simple_plant date class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: DateEntityDescription,
    ) -> None:
        """Initialize the date class."""
        super().__init__()
        self.entity_description = description

        self._fallback_value = self.str2date(str(entry.data.get("last_watered")))

        self.entity_id = f"date.{DOMAIN}_{description.key}_{entry.title}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{entry.title}"

        # Set up device info
        name = entry.title[0].upper() + entry.title[1:]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{entry.title}")},
            name=name,
            manufacturer=MANUFACTURER,
        )
        self._store = SimplePlantStore(hass, str(self.device))

    @staticmethod
    def str2date(iso_date: str) -> date:
        """Convert string to date."""
        return date.fromisoformat(iso_date)

    @staticmethod
    def date2str(date_obj: date) -> str:
        """Convert date to str."""
        return date_obj.isoformat()

    @property
    def device(self) -> str | None:
        """Return the device name."""
        if not self._attr_device_info or "name" not in self._attr_device_info:
            return None
        return str(self._attr_device_info["name"]).lower()

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()
        # Load stored data
        stored_data = await self._store.async_load()
        if self.unique_id in stored_data:
            await self.async_set_value(self.str2date(stored_data[self.unique_id]))
        else:
            await self.async_set_value(self._fallback_value)

    async def async_set_value(self, value: date) -> None:
        """Change the date."""
        # Validate the date is not in the future
        if value > date.today():  # noqa: DTZ011
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_future_date",
                translation_placeholders={},
            )

        self._attr_native_value = value

        # Save to persistent storage
        await self._store.async_save({self.unique_id: self.date2str(value)})
