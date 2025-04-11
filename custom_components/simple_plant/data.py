"""Storage helper for simple_plant."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY

STORAGE_VERSION = 1


class SimplePlantStore:
    """
    Class to hold simple_plant storage hanlders.

    The goal of such a class it to provide helpers to allow state persistance
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self.hass = hass
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data = {}

    async def async_load(self) -> dict:
        """Load the data from storage."""
        self._data = await self.store.async_load() or {}
        return self._data

    async def async_save(self, data: dict) -> None:
        """Save data to storage."""
        await self.async_load()
        self._data.update(data)
        await self.store.async_save(self._data)
