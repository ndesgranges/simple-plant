"""Data coordinator for simple_plant."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify

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
        self.device = slugify(entry.title)
        self.store = SimplePlantStore(hass)
        self.entry = entry

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

    async def async_set_last_watered(self, value: date) -> None:
        """Change last watered date manually."""
        if value > date.today():  # noqa: DTZ011
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_future_date",
                translation_placeholders={},
            )
        await self.store.async_save_data(
            self.device, {"last_watered": value.isoformat()}
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
            last_watered = date.fromisoformat(data["last_watered"])
        if "_old_last_watered" in data:
            old_last_watered = date.fromisoformat(data["_old_last_watered"])

        if last_watered and last_watered != date.today():  # noqa: DTZ011
            await self.async_action_mark_as_watered(save_old=last_watered)
        else:
            await self.async_action_cancel_mark_as_watered(old_value=old_last_watered)

    async def async_action_cancel_mark_as_watered(
        self, old_value: date | None = None
    ) -> None:
        """Update last watered date to old value."""
        if old_value:
            await self.async_set_last_watered(old_value)
        else:
            await self.async_action_mark_as_watered()

    async def async_action_mark_as_watered(self, save_old: date | None = None) -> None:
        """Update last watered date today."""
        today = date.today()  # noqa: DTZ011
        if save_old:
            await self.store.async_save_data(
                self.device, {"_old_last_watered": save_old.isoformat()}
            )
        await self.async_set_last_watered(today)

    def get_dates(self) -> dict[str, date] | None:
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

        last_watered_date = date.fromisoformat(states["last_watered"])
        nb_days = float(states["nb_days"])

        return {
            "last_watered": last_watered_date,
            "next_watering": last_watered_date + timedelta(days=nb_days),
            "today": date.today(),  # noqa: DTZ011
        }
