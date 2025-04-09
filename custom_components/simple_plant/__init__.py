"""
Custom integration to integrate simple_plant with Home Assistant.

For more details about this integration, please refer to
https://github.com/ndesgranges/simple-plant
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import DOMAIN, PLATFORMS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)
    # entry.async_on_unload(entry.add_update_listener(async_reload_entry))  # noqa: E501, ERA001

    return True


# async def async_unload_entry(
#     hass: HomeAssistant,
# ) -> bool:
#     """Handle removal of an entry."""
#     # return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)  # noqa: E501, ERA001


# async def async_reload_entry(
#     hass: HomeAssistant,
#     # entry: SimplePlantConfigEntry,
# ) -> None:
#     """Reload config entry."""
#     # await async_unload_entry(hass, entry)  # noqa: ERA001
#     # await async_setup_entry(hass, entry)  # noqa: ERA001
