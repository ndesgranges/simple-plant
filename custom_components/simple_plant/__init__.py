"""
Custom integration to integrate simple_plant with Home Assistant.

For more details about this integration, please refer to
https://github.com/ndesgranges/simple-plant
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.helpers.config_validation import config_entry_only_config_schema

from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import SimplePlantCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType


CONFIG_SCHEMA = config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Set up the Simple Plant component."""
    hass.data.setdefault(DOMAIN, {})
    return True


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    coordinator = SimplePlantCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove entry data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    # Remove storage
    coordinator = SimplePlantCoordinator(hass, entry)
    await coordinator.remove_device_from_storage()

    # Remove photo
    try:
        # Get the photo path from the entry's data
        photo_path = entry.data.get("photo")
        if photo_path:
            # Convert url path to actual file path
            file_path = Path(str(hass.config.path(photo_path.lstrip("/"))))

            # Check if file exists before trying to remove it
            if file_path.exists():
                file_path.unlink()
                LOGGER.info(f"Successfully removed image file: %{file_path}")
            else:
                LOGGER.warning(f"Image file not found: {file_path}")
    except OSError as err:
        LOGGER.error(f"Error reading image file {file_path}: {err}")


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
