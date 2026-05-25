"""Base entity for simple_plant."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import (
        Event,
        EventStateChangedData,
        HomeAssistant,
    )
    from homeassistant.helpers.entity import EntityDescription

    from .coordinator import SimplePlantCoordinator


class SimplePlantEntity:  # pylint: disable=too-few-public-methods
    """Base mixin for simple_plant entities."""

    _attr_has_entity_name = True
    coordinator: SimplePlantCoordinator
    hass: HomeAssistant
    unique_id: str | None

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: EntityDescription,
        platform: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__()
        self.entity_description = description
        self.coordinator = hass.data[DOMAIN][entry.entry_id]
        device = self.coordinator.device
        self.entity_id = f"{platform}.{DOMAIN}_{description.key}_{device}"
        self._attr_unique_id = f"{DOMAIN}_{description.key}_{device}"
        self._attr_device_info = self.coordinator.device_info

    @property
    def device(self) -> str | None:
        """Return the device name."""
        return self.coordinator.device


class SimplePlantTrackedEntity(SimplePlantEntity):
    """Mixin for entities that track watering state changes."""

    async def async_added_to_hass(self) -> None:
        """Subscribe to state changes and midnight timer."""
        await super().async_added_to_hass()  # pylint: disable=no-member
        self.async_on_remove(  # pylint: disable=no-member
            async_track_state_change_event(
                self.hass,
                f"date.{DOMAIN}_last_watered_{self.device}",
                self._update_state,
            )
        )
        self.async_on_remove(  # pylint: disable=no-member
            async_track_state_change_event(
                self.hass,
                f"number.{DOMAIN}_days_between_waterings_{self.device}",
                self._update_state,
            )
        )
        self.async_on_remove(  # pylint: disable=no-member
            async_track_time_change(
                self.hass,
                self._update_state,
                hour=0,
                minute=0,
                second=0,
            )
        )
        await self._update_state()

    @abstractmethod
    async def _update_state(
        self,
        _event: Event[EventStateChangedData] | datetime | None = None,
    ) -> None:
        """Update entity state based on tracked entities."""


class SimplePlantStoredEntity(SimplePlantEntity):
    """Mixin for entities with persistent coordinator storage."""

    _fallback_value: Any

    async def async_added_to_hass(self) -> None:
        """Load stored data from coordinator."""
        await super().async_added_to_hass()  # pylint: disable=no-member

        def warning(msg: str) -> None:
            LOGGER.warning("%s :%s", self.unique_id, msg)

        if self.coordinator.data is None:
            warning("Coordinator not ready at initialization")
            return
        data = self.coordinator.data.get(self.unique_id)
        if data is None:
            if self._fallback_value is None:
                warning("Initialization failed as _fallback_value is None")
                return
            await self._restore_value(self._fallback_value)
            return
        await self._restore_value(data)

    @abstractmethod
    async def _restore_value(self, value: Any) -> None:
        """Restore a stored or fallback value."""
