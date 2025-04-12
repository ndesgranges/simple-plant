"""Storage helper for simple_plant."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import LOGGER, STORAGE_KEY

STORAGE_VERSION = 1


class SimplePlantStore:
    """
    Class to hold simple_plant storage hanlders.

    The goal of such a class it to provide helpers to allow state persistance
    """

    def __init__(self, hass: HomeAssistant, device: str) -> None:
        """Initialize the storage."""
        self.hass = hass
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data = {}
        self.device = device

    async def async_load(self) -> dict:
        """Load the data from storage."""
        self._data = await self.store.async_load() or {}
        return self._data.get(self.device, {})

    async def async_save(self, data: dict) -> None:
        """Save data to storage."""
        await self.async_load()
        device_data = self._data.get(self.device, {})
        device_data.update(data)
        LOGGER.debug("Storing following data to device %s : %s", self.device, data)
        self._data[self.device] = device_data
        await self.store.async_save(self._data)
