"""Adds config flow for Simple PLant."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
import voluptuous as vol
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.util import slugify
from homeassistant.util.dt import as_local, as_utc, utcnow

from .const import DOMAIN, HEALTH_OPTIONS, IMAGES_MIME_TYPES, LOGGER, STORAGE_DIR

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

## UTILS


async def save_image(hass: HomeAssistant, file_id: str) -> str:
    """Permanently save an uploaded image."""
    with process_uploaded_file(hass, file_id) as uploaded_file:
        # Save the file
        storage_dir = Path(hass.config.path(STORAGE_DIR))
        storage_dir.mkdir(parents=True, exist_ok=True)

        suffix = uploaded_file.suffix
        if suffix not in IMAGES_MIME_TYPES:
            raise ValueError
        file_path = storage_dir / f"{file_id}{suffix}"

        # Safely copy the file using async operations
        async with aiofiles.open(file_path, "wb") as destination_file:  # noqa: SIM117
            async with aiofiles.open(uploaded_file, "rb") as source_file:
                await destination_file.write(await source_file.read())

        # relative path
        return f"/{STORAGE_DIR}/{file_path.name}"


def remove_photo(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove the photo file of a config entry."""
    try:
        # Get the photo path from the entry's data
        photo_path = entry.data.get("photo")
        if photo_path:
            # Convert url path to actual file path
            file_path = Path(str(hass.config.path(photo_path.lstrip("/"))))

            LOGGER.info("Trying to remove: %s", photo_path)

            # Check if file exists before trying to remove it
            if file_path.exists():
                file_path.unlink()
                LOGGER.info("Successfully removed image file: %s", file_path)
            else:
                LOGGER.warning("Image file not found: %s", file_path)
    except OSError as err:
        LOGGER.error("Error reading image file %s: %s", file_path, err)


## CONFIG FLOW SCHEMAS


def user_form() -> vol.Schema:
    """Return a new device form."""
    LOGGER.debug("config_flow, 1st call : displaying form")
    return vol.Schema(
        {
            vol.Required("name"): selector.TextSelector(
                selector.TextSelectorConfig(multiline=False, multiple=False)
            ),
            vol.Required("last_watered"): selector.DateSelector(
                selector.DateSelectorConfig(),
            ),
            vol.Required("days_between_waterings"): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=60,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="days",
                ),
            ),
            vol.Required("health"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    {
                        "options": HEALTH_OPTIONS,
                        "custom_value": False,
                        "sort": False,
                    }
                )
            ),
            vol.Optional("species", default=""): str,
            vol.Required("photo"): selector.FileSelector(
                selector.FileSelectorConfig(accept="image/*")
            ),
        }
    )


def option_form(suggested_species: str | None = None) -> vol.Schema:
    """Return a device reconfiguration form."""
    LOGGER.debug("option_flow, 1st call : displaying form")
    return vol.Schema(
        {
            vol.Optional("species", default="", description=suggested_species): str,
            vol.Optional("photo"): selector.FileSelector(
                selector.FileSelectorConfig(accept="image/*")
            ),
        }
    )


## CONFIG FLOWS


class SimplePlantFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Simple Plant."""

    def __init__(self) -> None:
        """Init."""
        self._user_inputs: dict = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get options flow for this handler."""
        return SimplePlantOptionFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """
        Provide Base Plant information Config Flow.

        1st call = return form to show
        2nd call = return form with user input
        """
        if user_input is None:
            # 1st call
            return self.async_show_form(step_id="user", data_schema=user_form())
        # 2nd call
        # Verify name
        domain_entries = self.hass.config_entries.async_entries(domain=DOMAIN)
        domain_entries_title_slugs = [slugify(entry.title) for entry in domain_entries]
        LOGGER.debug(domain_entries_title_slugs)
        if slugify(user_input["name"]) in domain_entries_title_slugs:
            return self.async_show_form(
                step_id="user",
                data_schema=user_form(),
                errors={"base": "name_exist"},
            )
        user_input["name_by_user"] = user_input["name"]
        # Verify date
        if "last_watered" in user_input:
            date = as_utc(as_local(datetime.fromisoformat(user_input["last_watered"])))
            if date > utcnow():
                return self.async_show_form(
                    step_id="user",
                    data_schema=user_form(),
                    errors={"base": "invalid_future_date"},
                )
        if "photo" not in user_input:
            return self.async_show_form(
                step_id="user",
                errors={"base": "upload_failed_generic"},
            )
        file_id = user_input["photo"]

        try:
            user_input["photo"] = await save_image(self.hass, file_id)
        except ValueError:
            return self.async_show_form(
                step_id="user",
                errors={"base": "upload_failed_type"},
            )

        return self.async_create_entry(title=user_input["name"], data=user_input)


class SimplePlantOptionFlowHandler(OptionsFlow):
    """Reconfiguration flow for Simple Plant."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Init."""
        self.user_inputs: dict = {}
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        """
        Provide new information.

        1st call = return form to show
        2nd call = return form with user input
        """
        form = option_form(self.entry.data.get("species"))

        if user_input is None:
            # 1st call
            return self.async_show_form(step_id="init", data_schema=form)
        # 2nd call
        if user_input.get("species"):
            self.user_inputs["species"] = user_input["species"]

        if user_input.get("photo"):
            try:
                file_id = user_input["photo"]
                self.user_inputs["photo"] = await save_image(self.hass, file_id)
                remove_photo(self.hass, self.entry)
            except ValueError:
                return self.async_show_form(
                    step_id="user",
                    errors={"base": "upload_failed_type"},
                )

        # On appelle le step de fin pour enregistrer les modifications
        return await self.async_end()

    async def async_end(self) -> ConfigFlowResult:
        """Finitsh ConfigEntry modification."""
        LOGGER.info(
            "Entry %s is being recreated",
            self.config_entry.entry_id,
        )

        data = dict(self.config_entry.data)
        data.update(self.user_inputs)
        self.hass.config_entries.async_update_entry(self.config_entry, data=data)

        return self.async_create_entry(
            # No data as config entry has been modified
            title=None,
            data={},
        )
