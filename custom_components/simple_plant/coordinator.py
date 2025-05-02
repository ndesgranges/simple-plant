"""Data coordinator for simple_plant."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify
from homeassistant.util.dt import as_local, as_utc, utcnow

from .const import DOMAIN, LOGGER, MANUFACTURER
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
        self.device = slugify(entry.title)
        self.store = SimplePlantStore(hass)
        self.config_entry = entry

        # Set up device info
        name = entry.title[0].upper() + entry.title[1:]
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DOMAIN}_{self.device}")},
            name=name,
            manufacturer=MANUFACTURER,
            model=entry.data.get("species"),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from storage."""
        await self.store.async_load()
        return await self.store.async_get_data(self.device)

    async def remove_device_from_storage(self) -> None:
        """Remove entry in storage."""
        await self.store.async_remove_device(self.device)
        await self.async_refresh()

    async def async_store_value(self, entity_id: str, value: str) -> None:
        """Store value in the store."""
        await self.store.async_save_data(self.device, {entity_id: value})
        await self.async_refresh()

    async def async_rename_device(self, new_id: str) -> None:
        """Migrate data for a device to another name."""
        await self.store.async_rename_device(self.device, new_id)
        await self.async_refresh()

    async def async_set_last_watered(self, value: datetime) -> None:
        """Change last watered date manually."""
        new_value = as_utc(value)
        if new_value > utcnow():
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_future_date",
                translation_placeholders={},
            )
        await self.store.async_save_data(
            self.device, {"last_watered": new_value.isoformat()}
        )
        await self.async_refresh()

    async def async_mark_as_watered_toggle(self) -> None:
        """Toggle last watered between old value and today."""
        data = await self.store.async_get_data(self.device)
        if data is None:
            LOGGER.warning("%s: No data found in storage", self.device)
            return

        last_watered = None
        old_last_watered = None
        if "last_watered" in data:
            last_watered = as_utc(
                as_local(datetime.fromisoformat(data["last_watered"]))
            )
        if "_old_last_watered" in data:
            old_last_watered = as_utc(
                as_local(datetime.fromisoformat(data["_old_last_watered"]))
            )

        if last_watered and as_local(last_watered).date() != as_local(utcnow()).date():
            await self.async_action_mark_as_watered(save_old=last_watered)
        else:
            await self.async_action_cancel_mark_as_watered(old_value=old_last_watered)

    async def async_action_cancel_mark_as_watered(
        self, old_value: datetime | None = None
    ) -> None:
        """Update last watered date to old value."""
        if old_value:
            await self.async_set_last_watered(as_utc(old_value))
        else:
            await self.async_action_mark_as_watered()

    async def async_action_mark_as_watered(
        self, save_old: datetime | None = None
    ) -> None:
        """Update last watered date today."""
        today = utcnow()
        if save_old:
            await self.store.async_save_data(
                self.device, {"_old_last_watered": as_utc(save_old).isoformat()}
            )
        await self.async_set_last_watered(today)

    def get_dates(self) -> dict[str, datetime] | None:
        """Get dates from relevants device entites states."""
        states_to_get = {
            "last_watered": f"date.{DOMAIN}_last_watered_{self.device}",
            "nb_days": f"number.{DOMAIN}_days_between_waterings_{self.device}",
        }

        # Get states from hass
        data = {key: self.hass.states.get(eid) for key, eid in states_to_get.items()}

        # Check if all states are available
        if any(
            data[key] is None
            or not data[key].state  # type: ignore noqa: PGH003
            or data[key].state == "unavailable"  # type: ignore noqa: PGH003
            for key in states_to_get
        ):
            LOGGER.warning("%s: Couldn't get all states", self.device)
            return None

        states = {key: data.state for key, data in data.items() if data is not None}

        last_watered_date = datetime.fromisoformat(states["last_watered"])
        nb_days = float(states["nb_days"])

        return {
            "last_watered": last_watered_date,
            "next_watering": last_watered_date + timedelta(days=nb_days),
            "today": utcnow(),
        }
