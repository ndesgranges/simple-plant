"""Adds config flow for Simple PLant."""

from __future__ import annotations

import shutil
from pathlib import Path

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.helpers import selector

from .const import DOMAIN, HEALTH_OPTIONS, LOGGER, STORAGE_DIR


class SimplePlantFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Simple Plant."""

    def __init__(self) -> None:
        """Init."""
        self._user_inputs: dict = {}

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """
        Provide Base Plant information Config Flow.

        1st call = return form to show
        2nd call = return form with user input
        """
        if user_input is None:
            # 1st call
            return self.async_show_form(step_id="user", data_schema=user_form())
        # 2nd call
        if "photo" not in user_input:
            return self.async_show_form(
                step_id="photo",
                errors={"upload_failed": "File upload failed"},
            )
        file_id = user_input["photo"]

        with process_uploaded_file(self.hass, file_id) as uploaded_file:
            # Save the file
            storage_dir = Path(self.hass.config.path("media", STORAGE_DIR))
            storage_dir.mkdir(parents=True, exist_ok=True)
            file_path = storage_dir / f"{file_id}{uploaded_file.suffix}"

            # Copy the uploaded file to your component's directory
            shutil.copyfile(uploaded_file, file_path)

            # store path
            relative_path = f"media/{STORAGE_DIR}/{file_path.name}"
            user_input["photo"] = relative_path

            return self.async_create_entry(title=user_input["name"], data=user_input)
        return self.async_create_entry(title=user_input["name"], data=user_input)


def user_form() -> vol.Schema:
    """Return a new device form."""
    LOGGER.debug("config_flow, 1st call : displaying form")
    return vol.Schema(
        {
            vol.Required("name"): selector.TextSelector(
                selector.TextSelectorConfig(multiline=False, multiple=False)
            ),
            vol.Required("last_time_watered"): selector.DateSelector(
                selector.DateSelectorConfig(),
            ),
            vol.Required("days_between_watering"): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=60,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="days",
                ),
            ),
            vol.Required("current_health"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    {
                        "options": HEALTH_OPTIONS,
                        "custom_value": False,
                        "sort": False,
                    }
                )
            ),
            vol.Optional("comment", default=""): str,
            vol.Required("photo"): selector.FileSelector(
                selector.FileSelectorConfig(accept="image/*")
            ),
        }
    )
