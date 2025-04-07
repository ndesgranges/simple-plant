"""Adds config flow for Simple PLant."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .const import DOMAIN, LOGGER


class SimplePlantFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Simple Plant."""

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """
        Config Flow.

        1st call = return form to show
        2nd call = get completed form and create device
        """
        if user_input is None:
            # 1st call
            return new_device_form(self)
        # 2nd call
        return


def new_device_form(hanlder: SimplePlantFlowHandler) -> config_entries.ConfigFlowResult:
    """Return a new device form."""
    LOGGER.debug("config_flow, 1st call : displaying form")
    user_form = vol.Schema(
        {
            vol.Required("name"): selector.LabelSelector(
                selector.LabelSelectorConfig()
            ),
            vol.Required("last_time_watered"): selector.DateSelector(
                selector.DateSelectorConfig(),
            ),
            vol.Required("photo"): selector.MediaSelector(
                selector.MediaSelectorConfig(),
            ),
            vol.Required("current_health"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    {
                        "options": [
                            "notset",
                            "poor",
                            "fair",
                            "good",
                            "verygood",
                            "excellent",
                        ],
                        "multiple": False,
                        "custom_value": False,
                        "sort": False,
                    }
                )
            ),
            vol.Optional("comment", default=""): str,
        }
    )
    return hanlder.async_show_form(step_id="user", data_schema=user_form)
