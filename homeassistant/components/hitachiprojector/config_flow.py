"""Config flow for Hitachi Projector integration."""

from __future__ import annotations

import logging
from typing import Any

from libhitachiprojector.hitachiprojector import HitachiProjectorConnection, ReplyType
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

TITLE = "Hitachi Projector"


class HitachiProjectorHub:
    """HitachiProjector hub."""

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, password: str) -> bool:
        """Test if we can authenticate with the host."""
        con = HitachiProjectorConnection(host=self.host, password=password)
        reply_type, _ = await con.get_power_status()
        if reply_type == ReplyType.DATA:
            return True

        if reply_type == ReplyType.AUTH:
            return False

        raise CannotConnect


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    hub = HitachiProjectorHub(data[CONF_HOST])

    if not await hub.authenticate(data[CONF_PASSWORD]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": TITLE}


class HitachiProjectorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hitachi Projector."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, default=user_input.get(CONF_HOST) if user_input else None
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=user_input.get(CONF_PASSWORD) if user_input else None,
                ): str,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
