"""Adds config flow for Simple PLant."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import aiofiles
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.helpers import selector

from .const import DOMAIN, HEALTH_OPTIONS, IMAGES_MIME_TYPES, LOGGER, STORAGE_DIR


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
        if (
            "last_time_watered" in user_input
            and date.fromisoformat(user_input["last_time_watered"]) > date.today()  # noqa: DTZ011
        ):
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

        with process_uploaded_file(self.hass, file_id) as uploaded_file:
            # Save the file
            storage_dir = Path(self.hass.config.path("local", STORAGE_DIR))
            storage_dir.mkdir(parents=True, exist_ok=True)

            suffix = uploaded_file.suffix
            if suffix not in IMAGES_MIME_TYPES:
                return self.async_show_form(
                    step_id="user",
                    errors={"base": "upload_failed_type"},
                )
            file_path = storage_dir / f"{file_id}{suffix}"

            # Safely copy the file using async operations
            async with aiofiles.open(file_path, "wb") as destination_file:  # noqa: SIM117
                async with aiofiles.open(uploaded_file, "rb") as source_file:
                    await destination_file.write(await source_file.read())

            # store path
            relative_path = f"/local/{STORAGE_DIR}/{file_path.name}"
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
            vol.Required("days_between_waterings"): selector.NumberSelector(
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
