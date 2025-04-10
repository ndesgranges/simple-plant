"""
Custom integration to integrate simple_plant with Home Assistant.

For more details about this integration, please refer to
https://github.com/ndesgranges/simple-plant
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .const import DOMAIN, LOGGER, PLATFORMS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    try:
        # Get the photo path from the entry's data
        photo_path = entry.data.get("photo")
        if photo_path:
            # Convert /local/simple_plant/xxx.png to actual file path
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
