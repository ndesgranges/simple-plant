"""Constants for simple_plant."""

from logging import Logger, getLogger

from homeassistant.const import Platform

STORAGE_KEY = "simple_plant_data"

LOGGER: Logger = getLogger(__package__)

DOMAIN = "simple_plant"

STORAGE_DIR = "simple_plant"

MANUFACTURER = "Simple Plant"

HEALTH_OPTIONS = [
    "notset",
    "poor",
    "fair",
    "good",
    "verygood",
    "excellent",
]

IMAGES_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".tiff": "image/tiff",
    ".svg": "image/svg+xml",
}

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
    Platform.DATE,
    Platform.IMAGE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]
