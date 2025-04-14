"""Data coordinator for simple_plant."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .data import SimplePlantStore

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


class SimplePlantCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching Simple Plant data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
        )
        self.device = entry.title.lower()
        self.store = SimplePlantStore(hass, self.device)
        self.entry = entry

    async def _async_update_data(self) -> dict:
        """Fetch data from storage."""
        return await self.store.async_load()

    async def remove_device_from_storage(self) -> None:
        """Remove entry in storage."""
        await self.store.async_remove_device()
        await self.async_refresh()

    async def async_store_value(self, entity_id: str, value: str) -> None:
        """Store value in the store."""
        await self.store.async_save({entity_id: value})
        await self.async_refresh()

    async def async_set_last_watered(self, value: date) -> None:
        """Change last watered date manually."""
        if value > date.today():  # noqa: DTZ011
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_future_date",
                translation_placeholders={},
            )
        await self.store.async_save({"last_watered": value.isoformat()})
        await self.async_refresh()

    async def async_action_mark_as_watered(self) -> None:
        """Update last watered date today."""
        today = date.today()  # noqa: DTZ011
        await self.async_set_last_watered(today)
