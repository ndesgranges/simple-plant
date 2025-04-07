"""Custom types for simple_plant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import SimplePlantApiClient
    from .coordinator import SimplePlantDataUpdateCoordinator


type SimplePlantConfigEntry = ConfigEntry[SimplePlantData]


@dataclass
class SimplePlantData:
    """Data for the Simple Plant integration."""

    client: SimplePlantApiClient
    coordinator: SimplePlantDataUpdateCoordinator
    integration: Integration
