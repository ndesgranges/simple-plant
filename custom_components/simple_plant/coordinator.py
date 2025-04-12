"""Data coordinator for simple_plant."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

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
        self.device = entry.title
        self.store = SimplePlantStore(hass, self.device)
        self.entry = entry

    async def _async_update_data(self) -> dict:
        """Fetch data from storage."""
        return await self.store.async_load()

    async def async_set_last_watered(self) -> None:
        """Update last watered date."""
        today = date.today().isoformat()  # noqa: DTZ011
        await self.store.async_save({"_last_watered": today})
        await self.async_refresh()
