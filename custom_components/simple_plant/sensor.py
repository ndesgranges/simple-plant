"""Sensor platform for simple_plant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.util.dt import as_local

from .const import DOMAIN, LOGGER
from .entity import SimplePlantTrackedEntity

if TYPE_CHECKING:
    from datetime import date, datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        device_class=SensorDeviceClass.DATE,
        key="next_watering",
        translation_key="next_watering",
        icon="mdi:clipboard-text-clock",
    ),
)

FERTILIZATION_DESCRIPTIONS = (
    SensorEntityDescription(
        device_class=SensorDeviceClass.DATE,
        key="next_fertilization",
        translation_key="next_fertilization",
        icon="mdi:clipboard-text-clock",
    ),
)

COLOR_MAPPING = {"Today": "Goldenrod", "Late": "Tomato"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    entities: list[SensorEntity] = [
        SimplePlantSensor(hass, entry, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    ]

    if entry.data.get("days_between_fertilizations"):
        entities.extend(
            SimplePlantFertilizationSensor(hass, entry, desc)
            for desc in FERTILIZATION_DESCRIPTIONS
        )

    # Create the global counter sensors only once
    if not hass.data[DOMAIN].get("_global_sensor_created"):
        hass.data[DOMAIN]["_global_sensor_created"] = True
        entities.append(SimplePlantCountSensor(hass))
        entities.append(SimplePlantFertilizeCountSensor(hass))

    async_add_entities(entities)


class SimplePlantSensor(SimplePlantTrackedEntity, SensorEntity):
    """simple_plant sensor class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(hass, entry, description, "sensor")
        self._fallback_value: date | None = None
        self._attr_native_value: date | None = None
        self._attr_extra_state_attributes = {
            "state_color": False,
        }

    @property
    def native_value(self) -> date | None:
        """Return true if the binary_sensor is on."""
        return (
            self._fallback_value
            if self._attr_native_value is None
            else self._attr_native_value
        )

    async def _update_state(
        self, _event: Event[EventStateChangedData] | datetime | None = None
    ) -> None:
        """Update the binary sensor state based on other entities."""
        dates = self.coordinator.get_dates()

        if not dates:
            return

        # Color
        today = as_local(dates["today"]).date()
        next_watering = as_local(dates["next_watering"]).date()

        color_key = "OK"
        if today == next_watering:
            color_key = "Today"
        if today > next_watering:
            color_key = "Late"

        if color_key in COLOR_MAPPING:
            self._attr_extra_state_attributes = {
                "state_color": True,
                "color": COLOR_MAPPING[color_key],
            }
        else:
            self._attr_extra_state_attributes = {"state_color": False}

        # Value
        self._attr_native_value = next_watering
        self.async_write_ha_state()


class SimplePlantFertilizationSensor(SimplePlantTrackedEntity, SensorEntity):
    """simple_plant fertilization sensor class."""

    _tracked_date_key = "last_fertilized"
    _tracked_number_key = "days_between_fertilizations"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the fertilization sensor class."""
        super().__init__(hass, entry, description, "sensor")
        self._fallback_value: date | None = None
        self._attr_native_value: date | None = None
        self._attr_extra_state_attributes = {
            "state_color": False,
        }

    @property
    def native_value(self) -> date | None:
        """Return the sensor value."""
        return (
            self._fallback_value
            if self._attr_native_value is None
            else self._attr_native_value
        )

    async def _update_state(
        self, _event: Event[EventStateChangedData] | datetime | None = None
    ) -> None:
        """Update the sensor state based on fertilization entities."""
        dates = self.coordinator.get_fertilization_dates()

        if not dates:
            return

        today = as_local(dates["today"]).date()
        next_fertilization = as_local(dates["next_fertilization"]).date()

        color_key = "OK"
        if today == next_fertilization:
            color_key = "Today"
        if today > next_fertilization:
            color_key = "Late"

        if color_key in COLOR_MAPPING:
            self._attr_extra_state_attributes = {
                "state_color": True,
                "color": COLOR_MAPPING[color_key],
            }
        else:
            self._attr_extra_state_attributes = {"state_color": False}

        self._attr_native_value = next_fertilization
        self.async_write_ha_state()


GLOBAL_ENTITY_PREFIX = f"binary_sensor.{DOMAIN}_todo_"
GLOBAL_FERT_PREFIX = f"binary_sensor.{DOMAIN}_fertilize_todo_"


class SimplePlantCountSensor(SensorEntity):
    """Sensor counting all plants that need watering (today or late)."""

    _attr_has_entity_name = True
    _attr_translation_key = "plants_to_water"
    _attr_icon = "mdi:watering-can"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value: int = 0

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the global count sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_plants_to_water"

    async def async_added_to_hass(self) -> None:
        """Subscribe to state changes and midnight time change."""
        self._update_count()

        entity_ids = [
            eid
            for eid in self.hass.states.async_entity_ids("binary_sensor")
            if eid.startswith(GLOBAL_ENTITY_PREFIX)
        ]
        if entity_ids:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, entity_ids, self._on_state_changed
                )
            )

        self.async_on_remove(
            async_track_time_change(
                self.hass, self._on_midnight, hour=0, minute=0, second=0
            )
        )

        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", self._on_any_state_changed)
        )

    def _update_count(self) -> None:
        """Count all watering todo binary sensors that are on."""
        self._attr_native_value = sum(
            1
            for eid in self.hass.states.async_entity_ids("binary_sensor")
            if eid.startswith(GLOBAL_ENTITY_PREFIX)
            and self.hass.states.get(eid) is not None
            and self.hass.states.get(eid).state == "on"  # type: ignore[union-attr]
        )

    async def _on_state_changed(self, _event: Event[EventStateChangedData]) -> None:
        """Handle tracked entity state change."""
        self._update_count()
        self.async_write_ha_state()

    async def _on_midnight(self, _now: datetime) -> None:
        """Refresh at midnight."""
        self._update_count()
        self.async_write_ha_state()

    async def _on_any_state_changed(self, event: Event) -> None:  # type: ignore[type-arg]
        """Track newly added or removed todo entities."""
        entity_id: str = event.data.get("entity_id", "")
        if not entity_id.startswith(GLOBAL_ENTITY_PREFIX):
            return

        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")

        if new_state is None:
            LOGGER.debug("Todo entity removed: %s", entity_id)
            self._update_count()
            self.async_write_ha_state()
            return

        if old_state is not None:
            return

        LOGGER.debug("New todo entity detected: %s", entity_id)
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [entity_id], self._on_state_changed
            )
        )
        self._update_count()
        self.async_write_ha_state()


class SimplePlantFertilizeCountSensor(SensorEntity):
    """Sensor counting all plants that need fertilizing (today or late)."""

    _attr_has_entity_name = True
    _attr_translation_key = "plants_to_fertilize"
    _attr_icon = "mdi:sprout"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value: int = 0

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the global fertilization count sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_plants_to_fertilize"

    async def async_added_to_hass(self) -> None:
        """Subscribe to state changes and midnight time change."""
        self._update_count()

        entity_ids = [
            eid
            for eid in self.hass.states.async_entity_ids("binary_sensor")
            if eid.startswith(GLOBAL_FERT_PREFIX)
        ]
        if entity_ids:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, entity_ids, self._on_state_changed
                )
            )

        self.async_on_remove(
            async_track_time_change(
                self.hass, self._on_midnight, hour=0, minute=0, second=0
            )
        )

        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", self._on_any_state_changed)
        )

    def _update_count(self) -> None:
        """Count all fertilize_todo binary sensors that are on."""
        self._attr_native_value = sum(
            1
            for eid in self.hass.states.async_entity_ids("binary_sensor")
            if eid.startswith(GLOBAL_FERT_PREFIX)
            and self.hass.states.get(eid) is not None
            and self.hass.states.get(eid).state == "on"  # type: ignore[union-attr]
        )

    async def _on_state_changed(self, _event: Event[EventStateChangedData]) -> None:
        """Handle tracked entity state change."""
        self._update_count()
        self.async_write_ha_state()

    async def _on_midnight(self, _now: datetime) -> None:
        """Refresh at midnight."""
        self._update_count()
        self.async_write_ha_state()

    async def _on_any_state_changed(self, event: Event) -> None:  # type: ignore[type-arg]
        """Track newly added or removed fertilize_todo entities."""
        entity_id: str = event.data.get("entity_id", "")
        if not entity_id.startswith(GLOBAL_FERT_PREFIX):
            return

        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")

        if new_state is None:
            LOGGER.debug("Fertilize entity removed: %s", entity_id)
            self._update_count()
            self.async_write_ha_state()
            return

        if old_state is not None:
            return

        LOGGER.debug("New fertilize entity detected: %s", entity_id)
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [entity_id], self._on_state_changed
            )
        )
        self._update_count()
        self.async_write_ha_state()
