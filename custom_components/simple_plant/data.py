"""Storage helper for simple_plant."""

from typing import Any, ClassVar

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import LOGGER, STORAGE_KEY

STORAGE_VERSION = 1


class SimplePlantStore:
    """
    Class to hold simple_plant storage hanlders.

    The goal of such a class it to provide helpers to allow state persistance
    """

    _instance: ClassVar["SimplePlantStore | None"] = None
    _initialized: bool = False

    def __new__(cls, _hass: HomeAssistant) -> "SimplePlantStore":
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        if not self._initialized:
            LOGGER.debug("Initializing storage %s", STORAGE_KEY)
            self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
            self._data: dict[str, Any] | None = None
            self._initialized = True

    async def async_load(self) -> None:
        """Load the data from storage."""
        self._data = await self.store.async_load() or {}

    async def async_get_data(self, device: str) -> dict[str, Any]:
        """Get data from storage."""
        if self._data is None:
            await self.async_load()
        if self._data is None:  # for linting
            LOGGER.error("Failed to load data from storage")
            return {}
        return self._data.get(device, {})

    async def async_save_data(self, device: str, data: dict) -> None:
        """Save data to storage."""
        if self._data is None:
            await self.async_load()
        if self._data is None:  # for linting
            LOGGER.error("Failed to load data from storage")
            return
        device_data = self._data.get(device, {})
        # update data
        device_data.update(data)
        self._data[device] = device_data
        # store data
        LOGGER.debug("Storing following data to device %s : %s", device, data)
        await self.store.async_save(self._data)

    async def async_remove_device(self, device: str) -> None:
        """Remove device data from storage."""
        if self._data is None:
            await self.async_load()
        if self._data is None:  # for linting
            LOGGER.error("Failed to load data from storage")
            return
        if device in self._data:
            del self._data[device]
            await self.store.async_save(self._data)

    async def async_rename_device(self, device: str, new_id: str) -> None:
        """Migrate device data from old `device` name to `new_name`."""
        if self._data is None:
            await self.async_load()
        if self._data is None:  # for linting
            LOGGER.error("Failed to load data from storage")
            return
        if device in self._data:
            device_data: dict[str, Any] = self._data.get(device, {})
            new_data = {}
            for key, value in device_data.items():
                if device in key:
                    striped_key = key[: -len(device)]
                    new_data[striped_key + new_id] = value
                else:
                    new_data[key] = value
            self._data[new_id] = new_data
            del self._data[device]
            await self.store.async_save(self._data)
