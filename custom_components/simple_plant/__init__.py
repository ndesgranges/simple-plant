"""
Custom integration to integrate simple_plant with Home Assistant.

For more details about this integration, please refer to
https://github.com/ndesgranges/simple-plant
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import async_get_hass
from homeassistant.helpers.config_validation import config_entry_only_config_schema
from homeassistant.helpers.device_registry import (
    EVENT_DEVICE_REGISTRY_UPDATED,
    EventDeviceRegistryUpdatedData,
    async_entries_for_config_entry,
    async_get,
)
from homeassistant.util import slugify

from .config_flow import remove_photo
from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import SimplePlantCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, HomeAssistant
    from homeassistant.helpers.typing import ConfigType


CONFIG_SCHEMA = config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Set up the Simple Plant component."""
    hass.data.setdefault(DOMAIN, {})
    return True


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    LOGGER.debug("Setting up entry %s", entry.title)
    coordinator = SimplePlantCoordinator(hass, entry)

    if entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
        await coordinator.async_config_entry_first_refresh()
    else:
        await coordinator.async_request_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    entry.async_on_unload(
        hass.bus.async_listen(
            EVENT_DEVICE_REGISTRY_UPDATED,  # type: ignore[arg-type]
            on_device_registry_update_handler,
        )
    )

    return True


async def on_device_registry_update_handler(
    event: Event[EventDeviceRegistryUpdatedData],
) -> None:
    """Handle update of device registry."""
    changes = event.data.get("changes")
    if not changes or not isinstance(changes, dict) or "name_by_user" not in changes:
        return
    # Get device
    hass = async_get_hass()
    device_registry = async_get(hass)
    device = device_registry.async_get(event.data.get("device_id"))
    if not device:
        return
    # Get entries
    entries: set[ConfigEntry] = set()
    for entry_id in device.config_entries:
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry:
            entries.add(entry)
    # Update entries
    for entry in entries:
        device_name_from_entry_title = entry.title[0].upper() + entry.title[1:]
        if (
            device_name_from_entry_title == device.name_by_user
            or device.name_by_user is None
        ):
            return
        LOGGER.debug(
            "Renaming entry %s to %s",
            entry.title,
            device.name_by_user,
        )
        data = dict(entry.data)
        data.update(
            {
                "name": device.name_by_user,
                "name_by_user": device.name_by_user,
            }
        )
        new_title = device.name_by_user

        coordinator: SimplePlantCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_rename_device(slugify(new_title))

        await hass.config_entries.async_unload(entry.entry_id)
        hass.config_entries.async_update_entry(entry, data=data, title=new_title)
        hass.config_entries.async_schedule_reload(entry.entry_id)
        device_registry.async_remove_device(device.id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle unloading of an entry."""
    # Unload platforms
    LOGGER.debug("Unloading %s", entry.title)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    LOGGER.debug("Unloading status : %s", "OK" if unload_ok else "NOK")

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
    remove_photo(hass, entry)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload config entry."""
    if entry.title != entry.data.get("name"):
        LOGGER.info("Changing name of %s to %s", entry.data.get("name"), entry.title)
        # Migrate storage storage
        coordinator: SimplePlantCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_rename_device(slugify(entry.title))
        # Update entry
        data = dict(entry.data)
        data.update({"name": entry.title, "name_by_user": entry.title})
        hass.config_entries.async_update_entry(entry, data=data)
        # remove obsolete device
        device_name = entry.title[0].upper() + entry.title[1:]
        device_registry = async_get(hass)
        for device in async_entries_for_config_entry(device_registry, entry.entry_id):
            if device.name != device_name:
                device_registry.async_remove_device(device.id)
        return
    LOGGER.info("Reloading entry %s", entry.title)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
