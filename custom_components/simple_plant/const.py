"""Constants for simple_plant."""

from logging import Logger, getLogger
from homeassistant.const import Platform

LOGGER: Logger = getLogger(__package__)

DOMAIN = "simple_plant"

STORAGE_DIR = "simple_plant"

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DATETIME,
    Platform.IMAGE,
    Platform.NUMBER,
    Platform.SELECT,
]
