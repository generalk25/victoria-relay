"""Config flow for Victoria Relay: where is the relay endpoint?"""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_RELAY_URL, CONF_TIMEOUT, DEFAULT_RELAY_URL, \
    DEFAULT_TIMEOUT, DOMAIN

SCHEMA = vol.Schema({
    vol.Required(CONF_RELAY_URL, default=DEFAULT_RELAY_URL): str,
    vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
})


class VictoriaRelayConfigFlow(config_entries.ConfigFlow,
                              domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Victoria Relay", data=user_input)
        return self.async_show_form(step_id="user", data_schema=SCHEMA)
