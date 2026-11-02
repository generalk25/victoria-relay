"""Victoria Relay: register the relay conversation agent."""
from __future__ import annotations

from homeassistant.components import conversation as ha_conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_RELAY_URL, CONF_TIMEOUT, DEFAULT_RELAY_URL, \
    DEFAULT_TIMEOUT, DOMAIN
from .conversation import VictoriaRelayAgent


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    agent = VictoriaRelayAgent(
        hass,
        relay_url=entry.data.get(CONF_RELAY_URL, DEFAULT_RELAY_URL),
        timeout=int(entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
    )
    ha_conversation.async_set_agent(hass, entry, agent)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ha_conversation.async_unset_agent(hass, entry)
    return True
