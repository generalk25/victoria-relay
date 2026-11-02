"""The Victoria Relay conversation agent.

It does exactly one thing: hand the sentence to Victoria (via the
relay endpoint on hastur) and return her reply as the pipeline
response. No intent matching, no device access, no opinions.
"""
from __future__ import annotations

import logging
import uuid

import aiohttp

from homeassistant.components import conversation
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import ERROR_LINE, HOLDING_LINE

_LOGGER = logging.getLogger(__name__)


class VictoriaRelayAgent(conversation.AbstractConversationAgent):
    """Conversation agent that relays every sentence to Victoria."""

    def __init__(self, hass: HomeAssistant, relay_url: str,
                 timeout: int) -> None:
        self.hass = hass
        self._relay_url = relay_url
        self._timeout = timeout

    @property
    def supported_languages(self) -> list[str] | str:
        return conversation.MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        request_id = uuid.uuid4().hex
        payload = {
            "id": request_id,
            "text": user_input.text,
            "language": user_input.language,
            "conversation_id": user_input.conversation_id,
        }
        speech = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._relay_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._timeout),
                ) as resp:
                    data = await resp.json()
                    speech = (data or {}).get("speech")
                    if (data or {}).get("timeout"):
                        speech = HOLDING_LINE
        except TimeoutError:
            _LOGGER.warning(
                "victoria_relay: relay timed out after %ss for %r",
                self._timeout, user_input.text[:60])
            speech = HOLDING_LINE
        except Exception:  # relay down, bad JSON, anything
            _LOGGER.exception("victoria_relay: relay call failed")
            speech = ERROR_LINE

        response = intent.IntentResponse(language=user_input.language)
        if speech:
            response.async_set_speech(speech)
        return conversation.ConversationResult(
            response=response,
            conversation_id=user_input.conversation_id,
        )
