import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_VARIABLES
from homeassistant.core import callback
from .const import DOMAIN, TITLE, CONF_EXCLUDE_LOW_FLOORS, CONF_LOW_FLOOR_LIMIT

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_VARIABLES): str,
        vol.Optional(CONF_EXCLUDE_LOW_FLOORS, default=False): bool,
        vol.Optional(CONF_LOW_FLOOR_LIMIT, default=5): int,
    }
)

class NaverLandConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Naver Land."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Validate the input here if needed
        await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_USERNAME]}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"{TITLE} ({user_input[CONF_USERNAME]})", data=user_input
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NaverLandOptionsFlow(config_entry)

class NaverLandOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_EXCLUDE_LOW_FLOORS,
                        default=options.get(CONF_EXCLUDE_LOW_FLOORS, False),
                    ): bool,
                    vol.Optional(
                        CONF_LOW_FLOOR_LIMIT,
                        default=options.get(CONF_LOW_FLOOR_LIMIT, 5),
                    ): int,
                }
            ),
        )
